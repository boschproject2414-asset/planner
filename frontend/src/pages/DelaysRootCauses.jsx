import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function DelaysRootCauses(){
  const {id}=useParams();
  const [delays,setDelays]=useState([])
  useEffect(()=>{apiFetch(`/v2/projects/${id}/delays`).then(r=>r.json()).then(setDelays)},[id])
  return <div>
    <h2>Delays & Root Causes</h2>
    <table border='1' cellPadding='6'><thead><tr><th>ID</th><th>Delay Hours</th><th>Status</th><th>Root Cause</th></tr></thead><tbody>
      {delays.map(d=><tr key={d.id}><td>{d.id}</td><td>{d.delay_hours}</td><td>{d.status}</td><td>{d.root_cause_category}</td></tr>)}
    </tbody></table>
  </div>
}
