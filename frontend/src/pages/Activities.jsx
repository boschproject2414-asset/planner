import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function Activities(){
  const {id}=useParams()
  const [rows,setRows]=useState([])
  const [drawer,setDrawer]=useState(null)
  const load=()=>apiFetch(`/v2/projects/${id}/activities`).then(r=>r.json()).then(setRows)
  useEffect(load,[id])

  const add=async()=>{
    await apiFetch('/v2/activities',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:Number(id),phase:'Mechanical',activity_name:'New Task',base_effort_hours:8})})
    load()
  }
  return <div>
    <h2>Activities</h2>
    <button onClick={add}>Add Activity</button>
    <table border='1' cellPadding='6'><thead><tr><th>ID</th><th>Phase</th><th>Name</th><th>Status</th><th>%</th><th>Planned Finish</th><th>Forecast Finish</th></tr></thead><tbody>
      {rows.map(r=><tr key={r.id} onClick={()=>setDrawer(r)}><td>{r.id}</td><td>{r.phase}</td><td>{r.activity_name}</td><td>{r.status}</td><td>{r.percent_complete}</td><td>{r.planned_finish}</td><td>{r.forecast_finish}</td></tr>)}
    </tbody></table>
    {drawer && <div style={{marginTop:10,padding:10,border:'1px solid #aaa'}}><h3>Task Drawer: {drawer.activity_name}</h3><pre>{JSON.stringify(drawer,null,2)}</pre></div>}
  </div>
}
