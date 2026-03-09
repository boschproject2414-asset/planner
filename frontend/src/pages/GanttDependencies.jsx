import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function GanttDependencies(){
  const {id}=useParams();
  const [deps,setDeps]=useState([])
  useEffect(()=>{apiFetch(`/v2/projects/${id}/dependencies`).then(r=>r.json()).then(setDeps)},[id])
  return <div>
    <h2>Gantt & Dependencies</h2>
    <p>Timeline view placeholder (MVP) + dependency risk table:</p>
    <table border='1' cellPadding='6'><thead><tr><th>Predecessor</th><th>Successor</th><th>Blocked</th></tr></thead><tbody>
      {deps.map(d=><tr key={d.id}><td>{d.predecessor}</td><td>{d.successor}</td><td>{String(d.blocked)}</td></tr>)}
    </tbody></table>
  </div>
}
