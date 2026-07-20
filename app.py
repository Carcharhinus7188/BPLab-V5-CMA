from __future__ import annotations
import json, time
from datetime import date
import streamlit as st
from schemas import EXPERIMENTS, COMMON_FIELDS
from calculations import calculate, final_result
from word_export import export_doc

st.set_page_config(page_title='BPLab CMA原始记录系统',page_icon='🧪',layout='centered',initial_sidebar_state='collapsed')
st.markdown("""<style>
.block-container{max-width:780px;padding-top:.7rem;padding-bottom:2rem}.stApp{background:#f7f9fb}h1{font-size:1.55rem!important;margin-bottom:.05rem}h2{font-size:1.15rem!important}.bp{background:#fff;border:1px solid #dfe6eb;border-radius:10px;padding:12px;margin:8px 0}.small{color:#60717c;font-size:.82rem}.stButton button{min-height:42px}.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"]{min-height:40px}div[data-testid="stHorizontalBlock"]{gap:.5rem}@media(max-width:700px){.block-container{padding-left:.65rem;padding-right:.65rem}.stRadio>div{gap:.2rem}.stButton button{width:100%}}</style>""",unsafe_allow_html=True)
st.title('大连标普检测有限公司')
st.caption('DALIAN BIAOPU TESTING CO., LTD.｜CMA电子原始记录系统（轻量版，无Logo）')

codes=list(EXPERIMENTS)
code=st.selectbox('检测项目',codes,format_func=lambda c:EXPERIMENTS[c]['name'])
conf=EXPERIMENTS[code]
key=f'record_{code}'

def initial_field(field):
    k,label,typ,default,*rest=field
    if typ=='date': return str(date.today()) if not default else default
    return default

def new_record():
    common={k:initial_field(f) for f in COMMON_FIELDS}; common['record_no']=f"BP-{date.today().strftime('%Y%m%d')}-{int(time.time())%100000:05d}"
    setup={f[0]:initial_field(f) for f in conf.get('setup',[])}
    checks={x:True for x in conf.get('checks',[])}
    rows=[]
    for i in range(conf['n']):
        row={f[0]:initial_field(f) for f in conf['row_fields']}; row['sample_id']=row.get('sample_id') or (f'S{i+1}' if code!='shock' else f'T{i+1}')
        if code=='hv': row['sample_id']=f'S{(i//2)+1}'; row['face']=f'面{(i%2)+1}'
        rows.append(row)
    aux=[]
    if conf.get('aux'):
        for label in conf['aux']['rows']:
            a={f[0]:initial_field(f) for f in conf['aux']['fields']};a['_label']=label;aux.append(a)
    return {'common':common,'setup':setup,'checks':checks,'rows':rows,'aux':aux,'anomalies':[{'time':'','sample':'','description':'','impact':'','action':'','responsible':'','reviewer':''} for _ in range(4)],'archives':{x:False for x in conf.get('archives',[])}}

if key not in st.session_state: st.session_state[key]=new_record()
rec=st.session_state[key]

uploaded=st.file_uploader('导入此前下载的JSON草稿（可选）',type=['json'],key=f'up_{code}')
if uploaded:
    try:
        obj=json.load(uploaded)
        if obj.get('experiment')==code:
            st.session_state[key]=obj['record'];rec=st.session_state[key];st.success('草稿已导入。')
    except Exception as e: st.error(f'草稿读取失败：{e}')

step=st.radio('填写步骤',['1 基本信息','2 设备与过程','3 原始数据','4 辅助数据','5 异常归档','6 结果导出'],horizontal=True)

def widget(field,current,key_prefix):
    k,label,typ,default,*rest=field; kk=f'{key_prefix}_{k}'
    if typ=='text': return st.text_input(label,value=str(current if current is not None else ''),key=kk)
    if typ=='area': return st.text_area(label,value=str(current if current is not None else ''),height=90,key=kk)
    if typ=='number': return st.number_input(label,value=float(current or 0),step=0.001,format='%.4f',key=kk)
    if typ=='date': return str(st.date_input(label,value=date.fromisoformat(current) if current else date.today(),key=kk))
    if typ=='select':
        opts=rest[0]; idx=opts.index(current) if current in opts else 0; return st.selectbox(label,opts,index=idx,key=kk)
    return current

def save_form(fields,target,prefix,title):
    st.subheader(title)
    with st.form(prefix):
        values={}
        for i,f in enumerate(fields): values[f[0]]=widget(f,target.get(f[0],initial_field(f)),f'{prefix}_{i}')
        ok=st.form_submit_button('保存本步骤',use_container_width=True)
    if ok: target.update(values);st.success('已保存。')

if step.startswith('1'):
    save_form(COMMON_FIELDS,rec['common'],f'common_{code}','委托、样品、环境和人员信息')
elif step.startswith('2'):
    save_form(conf.get('setup',[]),rec['setup'],f'setup_{code}','设备、参数和使用前确认')
    st.subheader('关键过程控制点')
    with st.form(f'checks_{code}'):
        vals={x:st.checkbox(x,value=rec['checks'].get(x,True),key=f'ck_{code}_{i}') for i,x in enumerate(conf.get('checks',[]))}
        ok=st.form_submit_button('保存过程确认',use_container_width=True)
    if ok:rec['checks'].update(vals);st.success('已保存。')
elif step.startswith('3'):
    st.subheader('逐个样品录入（每次仅加载一个样品，适合旧平板）')
    idx=st.selectbox('选择样品/试样',range(len(rec['rows'])),format_func=lambda i:f"{i+1}｜{rec['rows'][i].get('sample_id','')}")
    row=rec['rows'][idx]
    with st.form(f'row_{code}_{idx}'):
        vals={}
        for i,f in enumerate(conf['row_fields']): vals[f[0]]=widget(f,row.get(f[0],initial_field(f)),f'row_{code}_{idx}_{i}')
        ok=st.form_submit_button('保存该样品数据',use_container_width=True)
    if ok:row.update(vals);st.success(f'第{idx+1}个样品已保存。')
    completed=sum(any(v not in ('',0,0.0,None) for k,v in r.items() if k not in ('sample_id','face')) for r in rec['rows'])
    st.progress(completed/max(1,len(rec['rows'])),text=f'已录入 {completed}/{len(rec["rows"])} 个')
elif step.startswith('4'):
    if not conf.get('aux'):st.info('本项目没有单独的辅助数据表。')
    else:
        auxconf=conf['aux'];st.subheader(auxconf['name'])
        idx=st.selectbox('选择记录点',range(len(rec['aux'])),format_func=lambda i:f"{i+1}｜{rec['aux'][i].get('_label','')}")
        a=rec['aux'][idx]
        st.caption(a.get('_label',''))
        with st.form(f'aux_{code}_{idx}'):
            vals={}
            for i,f in enumerate(auxconf['fields']):vals[f[0]]=widget(f,a.get(f[0],initial_field(f)),f'aux_{code}_{idx}_{i}')
            ok=st.form_submit_button('保存该辅助记录',use_container_width=True)
        if ok:a.update(vals);st.success('辅助记录已保存。')
elif step.startswith('5'):
    st.subheader('异常、偏离与处理')
    idx=st.selectbox('异常记录序号',range(4),format_func=lambda i:f'第{i+1}条')
    a=rec['anomalies'][idx]
    fields=[('time','发生时间','text',''),('sample','涉及样品','text',''),('description','异常/偏离描述','area',''),('impact','影响评估','text',''),('action','处理措施及结果','area',''),('responsible','责任人','text',''),('reviewer','复核人','text','')]
    with st.form(f'anom_{code}_{idx}'):
        vals={f[0]:widget(f,a.get(f[0],''),f'anom_{code}_{idx}_{i}') for i,f in enumerate(fields)}
        ok=st.form_submit_button('保存异常记录',use_container_width=True)
    if ok:a.update(vals);st.success('已保存。')
    st.subheader('附件归档确认')
    with st.form(f'archives_{code}'):
        vals={x:st.checkbox(x,value=rec['archives'].get(x,False),key=f'ar_{code}_{i}') for i,x in enumerate(conf.get('archives',[]))}
        ok=st.form_submit_button('保存归档状态',use_container_width=True)
    if ok:rec['archives'].update(vals);st.success('已保存。')
else:
    rows=calculate(code,rec['rows'],rec['setup']); result=final_result(rows)
    st.subheader('结果汇总')
    st.metric('最终结果',result)
    counts={x:sum(r.get('result')==x for r in rows) for x in ['符合','不符合','仅记录','需复测','需复检','需重制']}
    st.write('；'.join(f'{k}：{v}' for k,v in counts.items() if v))
    missing=[]
    for k,label in [('record_no','记录编号'),('sample_name','样品名称'),('sample_no','样品编号/批号'),('operator','检测人员'),('reviewer','复核人员')]:
        if not rec['common'].get(k):missing.append(label)
    unchecked=[x for x,v in rec['checks'].items() if not v]
    if missing:st.warning('尚未填写：'+'、'.join(missing))
    if unchecked:st.warning('未确认控制点：'+'、'.join(unchecked))
    draft={'experiment':code,'record':rec}
    st.download_button('下载JSON草稿',json.dumps(draft,ensure_ascii=False,indent=2).encode('utf-8'),file_name=f"{rec['common'].get('record_no','record')}_{code}.json",mime='application/json',use_container_width=True)
    try:
        doc,result=export_doc(code,conf,rec['common'],rec['setup'],rec['checks'],rows,rec['aux'],rec['anomalies'],rec['archives'])
        st.download_button('生成并下载CMA原始记录Word',doc,file_name=f"{rec['common'].get('record_no','record')}_{conf['name']}.docx",mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',use_container_width=True,type='primary')
    except Exception as e:st.error(f'Word生成失败：{e}')
    if st.button('清空本项目，建立新记录',use_container_width=True):st.session_state[key]=new_record();st.rerun()

st.caption('说明：系统不添加Logo；Word输出以templates目录中的原始CMA记录表为版式基础。免费云端不作为唯一长期存储，请下载Word与JSON草稿归档。')
