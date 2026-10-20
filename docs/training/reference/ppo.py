"""Two PPO passes with fixed behavior probabilities and full-batch KL audits."""
import time
import copy
import random
import numpy as np
import torch
import torch.nn.functional as F
from .advantages import gae, weights, normalize_advantages


def fit_critic(policy, features, targets, optimizer, rows, epochs):
    # Whole-episode holdout for critic diagnostics, independently within each level.
    held = set()
    for stage in policy.config['stages']:
        episodes = sorted({r['episode_id'] for r in rows if r['stage']==stage})
        held.update(episodes[::5])
    test = torch.tensor([r['episode_id'] in held for r in rows],device=features.device)
    train = ~test
    if not train.any() or not test.any(): raise ValueError('Critic requires disjoint episodes')
    best=None; history=[]
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        error = (policy.value(features)-targets)/policy.config['critic_scale']
        loss = F.smooth_l1_loss(error[train],torch.zeros_like(error[train]))
        if not torch.isfinite(loss): raise ValueError('Nonfinite critic loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(policy.critic.parameters(),1.,error_if_nonfinite=True)
        optimizer.step()
        if (epoch+1)%25==0 or epoch+1==epochs:
            with torch.no_grad(): score=float((policy.value(features)[test]-targets[test]).square().mean())
            history.append({'epoch':epoch+1,'heldout_mse':score})
            if best is None or score<best[0]: best=(score,copy.deepcopy(policy.critic.state_dict()),copy.deepcopy(optimizer.state_dict()),epoch+1)
    policy.critic.load_state_dict(best[1]);optimizer.load_state_dict(best[2])
    with torch.no_grad():
        pred = policy.value(features);error=pred-targets
        if not torch.isfinite(pred).all() or pred.abs().max()>1e5: raise ValueError('Unacceptable critic numerical values')
        result={'epochs_run':epochs,'selected_epoch':best[3],'fit_history':history,'train_mse':float(error[train].square().mean()),'heldout_mse':float(error[test].square().mean()),
                'heldout_episodes':sorted(held),'value_min':float(pred.min()),'value_max':float(pred.max()),
                'target_min':float(targets.min()),'target_max':float(targets.max()),
                'heldout_residual_abs_p95':float(error[test].abs().quantile(.95))}
        variance=targets[test].var(unbiased=False)
        result['heldout_explained_variance']=float(1-error[test].var(unbiased=False)/variance) if variance>1e-8 else None
    return result


def loss_terms(lp, old, actions, adv, weight, config):
    ratio = (lp.gather(1,actions[:,None])-old.gather(1,actions[:,None])).squeeze(1).exp()
    surrogate = torch.minimum(ratio*adv,ratio.clamp(1-config['clip_epsilon'],1+config['clip_epsilon'])*adv)
    entropy = -(lp.exp()*lp).sum(-1)
    loss = ((-surrogate-config['entropy_coefficient']*entropy)*weight).sum()
    return loss, {'entropy':entropy,'old_kl':(old.exp()*(old-lp)).sum(-1),
                  'clip_fraction':((ratio-1).abs()>config['clip_epsilon']).float(),'ratio':ratio}


@torch.no_grad()
def audit(policy, rows, old, micro, stages):
    policy.actor.eval();logs=[];features=[]
    for start in range(0,len(rows),micro):
        part=rows[start:start+micro]
        lp,feat=policy.score([r['ids'] for r in part],[r['facing'] for r in part])
        logs.append(lp.cpu());features.append(feat.cpu())
    lp=torch.cat(logs)
    if not torch.isfinite(lp).all(): raise ValueError('Nonfinite policy audit')
    kl=(old.exp()*(old-lp)).sum(-1);ent=-(lp.exp()*lp).sum(-1)
    by={s:{'kl':float(kl[[r['stage']==s for r in rows]].mean()),
           'entropy':float(ent[[r['stage']==s for r in rows]].mean())} for s in stages}
    return {'equal_level_kl':sum(v['kl'] for v in by.values())/len(by),
            'decision_mean_kl':float(kl.mean()),'by_stage':by},torch.cat(features)


def update(policy, rows, actor_optimizer, critic_optimizer, config, version, micro, deadline, emit, save):
    if {r['policy_version'] for r in rows}!={version}: raise ValueError('Mixed behavior policies')
    features=torch.stack([r['features'] for r in rows]).to('cuda')
    old=torch.tensor([r['old_log_probs'] for r in rows])
    before,_=audit(policy,rows,old,micro,config['stages'])
    if max(abs(v['kl']) for v in before['by_stage'].values())>1e-4:
        raise ValueError('Collection and optimization probabilities differ before update')
    # Values were frozen at request time, before this batch's critic fitting.
    values=np.asarray([r['old_value'] for r in rows],dtype=np.float32)
    critic_initial={'source':'request_time_frozen_values','value_min':float(values.min()),'value_max':float(values.max())}
    adv,targets=gae(rows,values,config)
    weight=weights(rows,config['stages']);adv=normalize_advantages(adv,weight)
    tensor_adv=torch.tensor(adv,device='cuda');tensor_weight=torch.tensor(weight,device='cuda')
    old_gpu=old.to('cuda')
    targets=torch.tensor(targets,device='cuda')
    torch.save({'advantages':adv,'targets':targets.cpu(),'weights':weight,'behavior_log_probs':old,
                'episode_order':[r['episode_id'] for r in rows]},save.folder/f'iteration-{version+1:02d}-targets.pt')
    steps=0;records=[];stop=None;processed=0
    for epoch in range(config['ppo_epochs']):
        order=list(range(len(rows)));random.Random(config['seed']+version*100+epoch).shuffle(order)
        for offset in range(0,len(order),config['gradient_batch_size']):
            if time.monotonic()>=deadline: raise TimeoutError('Training allocation reached; partial actor retained')
            ids=order[offset:offset+config['gradient_batch_size']]
            policy.actor.train();actor_optimizer.zero_grad(set_to_none=True)
            metrics={'loss':0.,'entropy':0.,'old_kl':0.,'clip_fraction':0.}
            for start in range(0,len(ids),micro):
                part=ids[start:start+micro];batch=[rows[i] for i in part]
                lp,_=policy.score([r['ids'] for r in batch],[r['facing'] for r in batch])
                loss,m=loss_terms(lp,old_gpu[part],torch.tensor([r['action_index'] for r in batch],device='cuda'),
                                  tensor_adv[part],tensor_weight[part],config)
                loss=loss/len(ids)
                if not torch.isfinite(loss): raise ValueError('Nonfinite PPO objective')
                loss.backward();metrics['loss']+=float(loss.detach())
                for key in ('entropy','old_kl','clip_fraction'): metrics[key]+=float(m[key].detach().sum())/len(ids)
            # A drifting minibatch triggers a full audit before any further step.
            if metrics['old_kl']>1.5*config['target_kl']:
                actor_optimizer.zero_grad(set_to_none=True)
                checked,_=audit(policy,rows,old,micro,config['stages'])
                if checked['equal_level_kl']>(1.5*config['target_kl']) or max(v['kl'] for v in checked['by_stage'].values())>.06:
                    stop='full_batch_kl';break
                # Recompute this step after audit changed model mode and freed grads.
                policy.actor.train()
                for start in range(0,len(ids),micro):
                    part=ids[start:start+micro];batch=[rows[i] for i in part]
                    lp,_=policy.score([r['ids'] for r in batch],[r['facing'] for r in batch])
                    loss,_=loss_terms(lp,old_gpu[part],torch.tensor([r['action_index'] for r in batch],device='cuda'),tensor_adv[part],tensor_weight[part],config)
                    (loss/len(ids)).backward()
            norm=torch.nn.utils.clip_grad_norm_(list(policy.params.values()),config['max_grad_norm'],error_if_nonfinite=True)
            actor_optimizer.step();steps+=1;processed+=len(ids)
            emit({'kind':'optimizer','iteration':version+1,'ppo_epoch':epoch+1,'step_in_iteration':steps,
                  'gradient_norm':float(norm),**metrics})
            save.periodic({'phase':'optimizing','iteration':version+1,'ppo_epoch':epoch+1,'completed_indices':order[:offset+len(ids)],
                           'remaining_indices':order[offset+len(ids):],'actor_steps':steps})
        actor_optimizer.zero_grad(set_to_none=True)
        checked,new_features=audit(policy,rows,old,micro,config['stages']);records.append({'epoch':epoch+1,'examples':processed-sum(r.get('examples',0) for r in records),**checked})
        save.periodic({'phase':'ppo_pass_stopped' if stop else 'ppo_epoch_complete','iteration':version+1,'ppo_epoch':epoch+1,'actor_steps':steps},force=True)
        if checked['equal_level_kl']>(1.5*config['target_kl']) or max(v['kl'] for v in checked['by_stage'].values())>.06:
            stop='full_batch_kl'
        if stop: break
    if checked['equal_level_kl']>.15:
        raise ValueError('Policy quality stop: full-batch KL exceeded 0.15')
    critic_final=fit_critic(policy,new_features.to('cuda'),targets,critic_optimizer,rows,config['critic_epochs'])
    policy.actor.eval()
    return {'actor_steps':steps,'ppo_epochs_requested':config['ppo_epochs'],'epoch_audits':records,'full_passes_completed':sum(r['examples']==len(rows) for r in records),'planned_minibatches_per_pass':__import__('math').ceil(len(rows)/config['gradient_batch_size']),'actor_examples_processed':sum(r.get('examples',0) for r in records),'stop':stop,
            'critic_initial':critic_initial,'critic_final':critic_final,'examples':len(rows),
            'advantage_min':float(adv.min()),'advantage_max':float(adv.max()),
            'level_loss_mass':{s:float(weight[[r['stage']==s for r in rows]].sum()) for s in config['stages']}}
