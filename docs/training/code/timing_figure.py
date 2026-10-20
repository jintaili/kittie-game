"""Describe empirical timing distributions from portable exported records."""
import json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'head-goon-study'
import matplotlib.pyplot as plt
HOME=Path(__file__).resolve().parents[1]
d=json.loads((HOME/'data/latencies.json').read_text());series={k:sorted(x for e in es for x in e['latencies_ms']) for k,es in d['groups'].items()}
def quantile(a,q):
 i=(len(a)-1)*q;j=int(i);f=i-j
 return a[j]*(1-f)+a[min(j+1,len(a)-1)]*f
summary={k:{'n':len(a),'mean':statistics.mean(a),'median':quantile(a,.5),'p90':quantile(a,.9),'p95':quantile(a,.95),'p99':quantile(a,.99),'max':max(a),'over_500_ms':sum(x>500 for x in a),'over_1000_ms':sum(x>1000 for x in a)} for k,a in series.items()}
(HOME/'data/latency-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
colors={'PPO15':'#17678a','Delayed JEV':'#b15225','Original JEV':'#648443'}
for name,a in series.items():
 y=[(i+1)/len(a) for i in range(len(a))]
 for ax in axes:ax.step(a,y,where='post',label=name,color=colors[name],lw=1.7)
axes[0].set(xlim=(80,450),ylim=(0,1.01),title='Central distribution',xlabel='Observation-to-action latency, ms',ylabel='Fraction of applied decisions')
axes[1].set(xlim=(80,max(map(max,series.values()))*1.03),ylim=(.95,1.001),title='Slowest 5% of responses',xlabel='Observation-to-action latency, ms')
for ax in axes:ax.grid(alpha=.15)
axes[0].legend(loc='upper left',fontsize=9)
fig.savefig(HOME/'latency-distributions.png',dpi=180);fig.savefig(HOME/'latency-distributions.svg', metadata={'Date': None});plt.close(fig)
print(json.dumps(summary,indent=2))

# Keep generated SVG diffs stable and whitespace-clean.
p = HOME / 'latency-distributions.svg'
p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()) + '\n')
