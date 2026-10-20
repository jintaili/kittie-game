"""Generate paper figures from the exported analysis, without new inference."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'head-goon-study'
import matplotlib.pyplot as plt
HOME=Path(__file__).resolve().parents[1]
analysis=json.loads((HOME/'data/analysis.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(10,4.4),sharey=True)
for ax,env,title in zip(axes,['main','randomized'],['Original fixed entry','Randomized scenarios']):
 models=['Pretrained Qwen','JEV','BC04','PPO15'] if env=='main' and 'main|Pretrained Qwen|6' in analysis['cohorts'] else ['JEV','BC04','PPO15']
 for x,model in enumerate(models):
  key=f'{env}|{model}|6'
  if key not in analysis['cohorts']:
   ax.text(x,.12,'Evaluation\nrunning',ha='center',color='#777',fontsize=9);continue
  m=analysis['cohorts'][key];lo,hi=m['wilson95'];rate=m['rate']
  color='#17678a' if model=='PPO15' else '#596773'
  ax.errorbar(x,rate,yerr=[[max(0,rate-lo)],[max(0,hi-rate)]],fmt='o',capsize=5,color=color)
  ax.annotate(f"{m['wins']}/{m['n']}",(x,hi),xytext=(0,8),textcoords='offset points',ha='center',fontsize=9)
 ax.set(xticks=range(len(models)),xticklabels=[m.replace('Pretrained Qwen','Pretrained\nQwen') for m in models],ylim=(0,1.13),title=title,ylabel='Win fraction',xlim=(-.5,len(models)-.5));ax.grid(axis='y',alpha=.15)
fig.tight_layout();fig.savefig(HOME/'performance.png',dpi=180);fig.savefig(HOME/'performance.svg', metadata={'Date': None});plt.close(fig)

# Keep generated SVG diffs stable and whitespace-clean.
p = HOME / 'performance.svg'
p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()) + '\n')
