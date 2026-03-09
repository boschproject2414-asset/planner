import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function Materials(){
  const {id}=useParams();
  const [rows,setRows]=useState([])
  const [risks,setRisks]=useState([])
  useEffect(()=>{
    apiFetch(`/v2/projects/${id}/materials`).then(r=>r.json()).then(setRows)
    apiFetch(`/v2/projects/${id}/material-risks`).then(r=>r.json()).then(setRisks)
  },[id])
  return <div>
    <h2>Material Intelligence</h2>
    <p>At-risk materials: {risks.length}</p>
    <table border='1' cellPadding='6'><thead><tr><th>Part</th><th>Ownership</th><th>Status</th><th>Need By</th><th>Promised</th></tr></thead><tbody>
      {rows.map(m=><tr key={m.id}><td>{m.part_number}</td><td>{m.ownership}</td><td>{m.status}</td><td>{m.need_by_date}</td><td>{m.promised_date}</td></tr>)}
    </tbody></table>
  </div>
}
