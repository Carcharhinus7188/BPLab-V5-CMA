from __future__ import annotations
from statistics import mean
from collections import Counter

def avg(*vals):
    nums=[float(v or 0) for v in vals]
    return sum(nums)/len(nums) if nums else 0.0

def calculate(code, rows, setup):
    out=[]
    for row in rows:
        r=dict(row)
        if code=='rough':
            r['average']=round(avg(r.get('ra1'),r.get('ra2'),r.get('ra3')),3); r['result']='符合' if r['average']<=15 else '不符合'
        elif code=='mc':
            r['dm_avg']=round(avg(r.get('dm1'),r.get('dm2'),r.get('dm3')),4); r['tau']=round(float(r.get('k') or 0)*float(r.get('ffail') or 0),2); r['result']='符合' if r['tau']>25 else '不符合'
        elif code=='xray':
            r['roi_avg']=round(avg(r.get('roi1'),r.get('roi2'),r.get('roi3')),2); r['result']='需复检' if r.get('image_valid')!='有效' else ('符合' if r.get('anomaly')=='未见明显异常' else '不符合')
        elif code=='warp':
            r['delta']=round(float(r.get('h1') or 0)-float(r.get('h2') or 0),4); limit=float(setup.get('limit') or 0); r['result']='仅记录' if limit<=0 else ('符合' if abs(r['delta'])<=limit else '不符合')
        elif code=='cte':
            dt=float(r.get('end_temp') or 0)-float(r.get('start_temp') or 0); l0=float(r.get('l0') or 0); r['dt']=round(dt,3); r['alpha']=round((float(r.get('dl_um') or 0)/1000)/(l0*dt)*1e6,3) if l0 and dt else 0; r['result']='仅记录' if r.get('valid')=='有效' else '需复测'
        elif code=='shock':
            r['result']='符合' if all(r.get(k)=='无' for k in ['crack','chip','fracture']) else '不符合'
        elif code=='bend':
            limit=float(setup.get('limit') or 800); r['result']='符合' if float(r.get('stress') or 0)>=limit else '不符合'
        elif code=='hv':
            r['average']=round(avg(r.get('hv1'),r.get('hv2'),r.get('hv3')),1); r['result']='仅记录'
        elif code=='thickness':
            r['fixed_avg']=round(avg(r.get('f1'),r.get('f2'),r.get('f3')),4); r['mid_avg']=round(avg(r.get('m1'),r.get('m2'),r.get('m3')),4); r['end_avg']=round(avg(r.get('e1'),r.get('e2'),r.get('e3')),4); r['total_avg']=round(avg(r['fixed_avg'],r['mid_avg'],r['end_avg']),4); r['deviation']=round(r['total_avg']-float(setup.get('design') or 0),4); tol=float(setup.get('tolerance') or 0); r['result']='仅记录' if tol<=0 else ('符合' if abs(r['deviation'])<=tol else '不符合')
        elif code=='color':
            votes=[r.get('obs1'),r.get('obs2'),r.get('obs3')]; c=Counter(votes); majority=c.most_common(1)[0][0] if votes else '无法判定'; r['majority']=majority; r['result']='符合' if majority=='未见明显差异' else ('需复检' if majority=='无法判定' else '不符合')
        elif code=='cut':
            r['result']='符合' if r.get('quality')=='合格' else ('需重制' if r.get('quality')=='重制样' else '不符合')
        out.append(r)
    return out

def final_result(rows):
    results=[r.get('result','') for r in rows]
    if any(x in ('需复测','需复检','需重制') for x in results): return '需复测/复检/重制'
    if any(x=='不符合' for x in results): return '不符合'
    if any(x=='符合' for x in results): return '符合'
    return '仅提供实测结果'
