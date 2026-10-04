"""Conditional scenario simulation, NOT observed enterprise data.
Run: python s1_risk.py. Requires Python 3.10+ and numpy.
All currency in VND. Volume basis and assumptions are in assumptions.json.
"""
from pathlib import Path
from statistics import NormalDist
import json
import numpy as np

OUT = Path(__file__).resolve().parent
N, SEED = 100_000, 20261003
RANGES = {'y': [.8,.9,.95], 'P': [90000,100000,110000],
          'proc':[25000,32000,40000], 'qa':[2000,3000,4000],
          'I':[1.5e9,2e9,3e9]}

def annuity(r, T=10):
    return (1-(1+r)**(-T))/r

def transport(d):
    d=np.asarray(d)
    if np.any(d<1): raise ValueError('Only d >= 1 km is parameterised')
    return 19232.4+7960.8*np.minimum(d-1,4)+6398.4*np.maximum(d-5,0)

def evaluate(y=.9,P=100000,proc=32000,qa=3000,I=2e9,d=5,Q=100000,
             residual=10000,rf=.10,gp=1,gr=1,haul=1,extra=0):
    vp,vr=y*gp,(1-y)*gr
    c=proc+qa+vr*residual+vp*haul*transport(d)+extra
    b=vp*P
    cf=Q*(b-c)
    f=-I+cf*annuity(rf)
    return dict(cost=c,revenue=b,margin=b-c,cf=cf,FNPV=f,
                FBCR=Q*b*annuity(rf)/(I+Q*c*annuity(rf)))

def inv_transport(cost):
    return 1+(cost-19232.4)/7960.8 if cost<=51075.6 else 5+(cost-51075.6)/6398.4

def triangular_ppf(u,bounds):
    a,m,b=bounds
    return np.where(u<(m-a)/(b-a),a+np.sqrt(u*(b-a)*(m-a)),
                    b-np.sqrt((1-u)*(b-a)*(b-m)))

def draws(seed=SEED,uniform=False,rho=0):
    rng=np.random.default_rng(seed)
    u=rng.random((N,5))
    if rho:
        z=rng.standard_normal((N,2))
        zy=z[:,0]; zp=rho*zy+np.sqrt(1-rho*rho)*z[:,1]
        cdf=NormalDist().cdf
        u[:,0]=np.fromiter((cdf(float(x)) for x in zy),float,N)
        u[:,2]=np.fromiter((cdf(float(x)) for x in zp),float,N)
    return {k:(v[0]+u[:,j]*(v[2]-v[0]) if uniform else triangular_ppf(u[:,j],v))
            for j,(k,v) in enumerate(RANGES.items())}

def stats(values):
    f=values['FNPV']; p=float(np.mean(f<0))
    q=np.quantile(f,[.05,.5,.95])/1e9
    return dict(p_loss=p,mc_se=np.sqrt(p*(1-p)/len(f)),
                p05_bn=float(q[0]),median_bn=float(q[1]),p95_bn=float(q[2]),
                mean_bn=float(np.mean(f)/1e9))

def serial(v):
    if isinstance(v,dict): return {k:serial(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [serial(x) for x in v]
    if isinstance(v,np.generic): return v.item()
    return v

def main():
    base=evaluate()
    cap=2e9/(100000*annuity(.1))
    out={'base':base,'thresholds':{
        'price_delivered':(32000+3000+1000+cap)/.9+transport(5),
        'processing':90000-3000-1000-.9*transport(5)-cap,
        'yield':(32000+3000+10000+cap)/(100000-transport(5)+10000),
        'extra_unit_cost':float(base['margin']-cap),
        'distance_financial':inv_transport((90000-32000-3000-1000-cap)/.9)}}
    out['deterministic']={
        'adverse':evaluate(y=.8,P=90000,proc=40000,qa=4000,I=3e9,d=7.5),
        'base':base,
        'favourable':evaluate(y=.95,P=110000,proc=25000,qa=2000,I=1.5e9,d=3)}
    out['MC']={}
    for label,uniform,rho in [('triangular_independent',False,0),
                              ('triangular_negative_dependence',False,-.6),
                              ('triangular_positive_dependence',False,.6),
                              ('uniform_independent',True,0)]:
        x=draws(uniform=uniform,rho=rho)
        out['MC'][label]={str(d):stats(evaluate(**x,d=d)) for d in [3,5,7.5]}
        out['MC'][label]['realized_y_proc_pearson']=float(np.corrcoef(x['y'],x['proc'])[0,1])
        if label=='triangular_independent':
            out['convergence']={str(n):stats({k:v[:n] for k,v in evaluate(**x).items()}) for n in [10000,50000,N]}
            out['structural_MC']={
                'haul_15pct':stats(evaluate(**x,haul=1.15)),
                'extra_5000':stats(evaluate(**x,extra=5000)),
                'product_volume_factor_0.9':stats(evaluate(**x,gp=.9)),
                'product_volume_factor_1.1':stats(evaluate(**x,gp=1.1)),
                'Q_80000':stats(evaluate(**x,Q=80000)),
                'Q_120000':stats(evaluate(**x,Q=120000))}
            ranks={k:np.argsort(np.argsort(v)) for k,v in x.items()}
            fr=np.argsort(np.argsort(evaluate(**x)['FNPV']))
            out['spearman']={k:float(np.corrcoef(v,fr)[0,1]) for k,v in ranks.items()}
            f_by_route={f'FNPV_{d:g}km_VND':evaluate(**x,d=d)['FNPV'] for d in [3,5,7.5]}
            np.savez_compressed(OUT/'s1_draws_seed20261003.npz',**x,**f_by_route)
    out['replicate_seed_checks']={str(seed):stats(evaluate(**draws(seed=seed))) for seed in [20261004,20261005]}
    out['extra_cost_tests']={str(c):float(evaluate(extra=c)['FNPV']) for c in [0,2500,5000,10000]}
    # Meaningful checks: annual cash flow vs annuity, correct break-even root,
    # physical mass balance, and price-basis equivalent formulations.
    explicit=-2e9+sum(float(base['cf'])/(1.1**t) for t in range(1,11))
    assert abs(explicit-float(base['FNPV']))<.01
    assert abs(float(evaluate(d=out['thresholds']['distance_financial'])['FNPV']))<.01
    assert abs(float(evaluate(P=out['thresholds']['price_delivered'])['FNPV']))<.01
    assert abs(float(evaluate(y=out['thresholds']['yield'])['FNPV']))<.01
    assert abs(.9*1+(1-.9)*1-1)<1e-12
    assert abs(float(transport(5-1e-9)-transport(5+1e-9)))<.001
    gate=100000
    exgate=.9*gate-32000-3000-1000
    delivered=.9*(gate+transport(5))-32000-3000-1000-.9*transport(5)
    assert abs(exgate-delivered)<1e-9
    out['checks']='PASS: annuity, distance/price/yield roots, mass balance under equal densities, continuous tariff, consistent ex-gate versus delivered formulation.'
    assumptions={'n':N,'seed':SEED,'numpy':np.__version__,
      'site_context':'Mong Duong Mine, Quang Ninh; site-specific context/data are identified by the authors as recorded at the mine.',
      'site_record_provenance':'Raw mine records are not included; authors should document record identifier, date/period, method, units, and responsible source before publication.',
      'interpretation':'Outputs are model-derived. Monte Carlo distributions are analyst-selected uncertainty scenarios, not observed mine-data distributions.',
      'distribution_status':'Analyst-selected epistemic scenarios; NOT fitted to observed data or elicited from experts.',
      'ranges_low_mode_high':RANGES,'held_fixed':{'Q':100000,'T':10,'rf':.10,'residual':10000,
        'density_ratios_gp_gr':1,'haul_multiplier':1,'extra_unmodelled_cost':0},
      'scope':'One independent project draw, held constant in real terms for 10 years. Routes 3,5,7.5 km analysed separately.',
      'price_basis':'P is hypothetical DELIVERED revenue, NOT the observed ex-gate price cited in manuscript.',
      'capital':'Hired machinery; I is site preparation/mobilisation, excludes purchase of shift-costed equipment.',
      'volume':'y is mass recovery; gp=rho_input/rho_product; gr=rho_input/rho_residual. Equal-density base is unverified.',
      'dependence':'Gaussian copula normal-latent rho=-0.6,+0.6 for y/proc; not claimed as observed Spearman/Pearson correlation.'}
    (OUT/'assumptions.json').write_text(json.dumps(assumptions,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'results.json').write_text(json.dumps(serial(out),indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(serial({'thresholds':out['thresholds'],'MC':out['MC'],'structural_MC':out['structural_MC'],'checks':out['checks']}),indent=2))

if __name__=='__main__': main()
