import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api'

export function Portfolio(){
  const [rows,setRows]=useState([])
  useEffect(()=>{apiFetch('/v2/portfolio').then(r=>r.json()).then(setRows)},[])
  return <div>
    <h2>Portfolio</h2>
    <table border='1' cellPadding='8'><thead><tr><th>Project</th><th>Name</th><th>Delayed Activities</th><th>Material Risks</th></tr></thead><tbody>
      {rows.map(r=><tr key={r.id}><td><Link to={`/project/${r.id}/home`}>{r.project_code}</Link></td><td>{r.name}</td><td>{r.delayed}</td><td>{r.material_risks}</td></tr>)}
    </tbody></table>
  </div>
}
