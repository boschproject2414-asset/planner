import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function BaselinesActions(){
  const {id}=useParams();
  const [variance,setVariance]=useState([])
  const [actions,setActions]=useState([])
  useEffect(()=>{
    apiFetch(`/v2/projects/${id}/baseline-variance`).then(r=>r.json()).then(d=>setVariance(d.variance||[]))
    apiFetch(`/v2/projects/${id}/actions`).then(r=>r.json()).then(setActions)
  },[id])
  return <div>
    <h2 className='section-title'>Baselines & Actions</h2>
    <div className='grid-3'>
      <div className='card' style={{gridColumn:'span 2'}}><h3>Variance Snapshot</h3><pre>{JSON.stringify(variance,null,2)}</pre></div>
      <div className='card'><h3>Action Items</h3><pre>{JSON.stringify(actions,null,2)}</pre></div>
    </div>
  </div>
}
