"""Portable descriptive analysis. Python standard library; no model or API calls."""
import json,math,random,statistics
from collections import defaultdict
from pathlib import Path
HOME=Path(__file__).resolve().parents[1]

def wilson(w:int,n:int)->list[float]:
 if not 0<=w<=n or n<=0:raise ValueError('Invalid count')
 z=1.959963984540054;p=w/n;d=1+z*z/n
 center=(p+z*z/(2*n))/d
 half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0.,center-half),min(1.,center+half)]

def fisher(a:int,na:int,b:int,nb:int)->float:
 if not (0<=a<=na and 0<=b<=nb and na>0 and nb>0):raise ValueError('Invalid count')
 successes=a+b
 def probability(x):return math.comb(na,x)*math.comb(nb,successes-x)/math.comb(na+nb,successes)
 observed=probability(a)
 return min(1.,sum(probability(x) for x in range(max(0,successes-nb),min(na,successes)+1) if probability(x)<=observed*(1+1e-12)))

def newcombe(a:int,na:int,b:int,nb:int)->list[float]:
 """Unpaired score interval, a/na minus b/nb, no continuity correction."""
 la,ua=wilson(a,na);lb,ub=wilson(b,nb);pa,pb=a/na,b/nb;delta=pa-pb
 return [max(-1.,delta-math.hypot(pa-la,ub-pb)),min(1.,delta+math.hypot(ua-pa,pb-lb))]

def matched(first:list[dict],second:list[dict])->dict:
 def keyed(rows):
  result={}
  for r in rows:
   key=r['scenario']
   if key is None or key in result:raise ValueError('Missing or repeated scenario')
   result[key]=r
  return result
 a,b=keyed(first),keyed(second)
 if not a or a.keys()!=b.keys():raise ValueError('Scenario sets do not match')
 for k in a:
  if a[k]['entry_sha256']!=b[k]['entry_sha256']:raise ValueError('Mismatched native entry')
 diff=[int(a[k]['win'])-int(b[k]['win']) for k in sorted(a)]
 plus=diff.count(1);minus=diff.count(-1);n=plus+minus
 p=min(1.,2*sum(math.comb(n,k) for k in range(min(plus,minus)+1))/2**n) if n else 1.
 rng=random.Random(19102026)
 bootstrap=sorted(sum(rng.choices(diff,k=len(diff)))/len(diff) for _ in range(20000))
 def quantile(q):
  index=q*(len(bootstrap)-1);lo=int(index);f=index-lo
  return bootstrap[lo]*(1-f)+bootstrap[min(lo+1,len(bootstrap)-1)]*f
 return {'n':len(diff),'difference':statistics.mean(diff),'first_only':plus,'second_only':minus,'exact_mcnemar_p':p,'paired_bootstrap95':[quantile(.025),quantile(.975)],'bootstrap_resamples':20000,'bootstrap_seed':19102026}

def main():
 rows=json.loads((HOME/'data/games.json').read_text());groups=defaultdict(list)
 if len({r['game_id'] for r in rows})!=len(rows):raise ValueError('Duplicate games')
 for r in rows:groups[f"{r['environment']}|{r['model']}|{r['post_action_frames']}"] .append(r)
 out={'cohorts':{},'comparisons':{},'interpretation':'Exploratory analyses. Nominal intervals/tests do not account for training-run uncertainty, repeated fixed-entry trajectories, or adaptive experiment selection.'}
 for key,rs in groups.items():
  w=sum(r['win'] for r in rs);n=len(rs)
  out['cohorts'][key]={'wins':w,'n':n,'rate':w/n,'wilson95':wilson(w,n),'mean_episode_median_latency_ms':statistics.mean(r['delay_median_ms'] for r in rs),'outcomes':{v:sum(r['outcome']==v for r in rs) for v in sorted({r['outcome'] for r in rs})}}
 original_comparisons=[('PPO15','BC04'),('PPO15','JEV'),('PPO10','BC04'),('PPO10','PPO15')]
 if 'main|Pretrained Qwen|6' in out['cohorts']:
  original_comparisons += [(m,'Pretrained Qwen') for m in ['BC04','PPO15','JEV']]
 for first,second in original_comparisons:
  a,b=[out['cohorts'][f'main|{m}|6'] for m in [first,second]]
  out['comparisons'][f'main:{first}-{second}']={'difference':a['rate']-b['rate'],'newcombe95':newcombe(a['wins'],a['n'],b['wins'],b['n']),'fisher_two_sided_p':fisher(a['wins'],a['n'],b['wins'],b['n']),'paired':False}
 for first,second in [('PPO15','BC04'),('PPO15','PPO10'),('JEV','PPO15'),('JEV','JEV delayed')]:
  out['comparisons'][f'randomized:{first}-{second}']=matched(groups[f'randomized|{first}|6'],groups[f'randomized|{second}|6'])
 one=groups['randomized|PPO15|1'];scenarios={r['scenario'] for r in one}
 out['comparisons']['randomized:PPO15-one-six']=matched(one,[r for r in groups['randomized|PPO15|6'] if r['scenario'] in scenarios])
 (HOME/'data/analysis.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
