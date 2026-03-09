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
    <h2>Baselines & Actions</h2>
    <h3>Variance</h3>
    <pre>{JSON.stringify(variance,null,2)}</pre>
    <h3>Actions</h3>
    <pre>{JSON.stringify(actions,null,2)}</pre>
  </div>
}
