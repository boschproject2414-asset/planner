import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function ProjectHome(){
  const {id}=useParams()
  const [data,setData]=useState({logs:[],risks:[],actions:[]})
  useEffect(()=>{apiFetch(`/v2/projects/${id}/home`).then(r=>r.json()).then(setData)},[id])
  const quick=async(path,method='POST',body)=>{
    const r=await apiFetch(path,{method,headers:{'Content-Type':'application/json'},body: body?JSON.stringify(body):undefined});
    alert(await r.text())
  }
  return <div>
    <h2 className='section-title'>Project Home</h2>
    <div style={{marginBottom:12}}>
      <button className='btn' onClick={()=>quick('/v2/seed')}>Seed sample data</button>
      <button className='btn primary' onClick={()=>quick(`/v2/projects/${id}/recalculate`)}>Recalculate Forecast</button>
      <button className='btn' onClick={()=>quick(`/v2/projects/${id}/baselines`,'POST',{name:`Baseline-${Date.now()}`})}>Create Baseline</button>
    </div>
    <div className='grid-3'>
      <div className='card'><h3>Latest Logs</h3><ul className='list'>{(data.logs||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div>
      <div className='card'><h3>Top Risks</h3><ul className='list'>{(data.risks||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div>
      <div className='card'><h3>Open Actions</h3><ul className='list'>{(data.actions||[]).map((x,i)=><li key={i}>{x}</li>)}</ul></div>
    </div>
  </div>
}
