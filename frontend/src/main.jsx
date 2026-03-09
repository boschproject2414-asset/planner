import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'
import { Portfolio } from './pages/Portfolio'
import { ProjectHome } from './pages/ProjectHome'
import { Activities } from './pages/Activities'
import { GanttDependencies } from './pages/GanttDependencies'
import { Materials } from './pages/Materials'
import { DelaysRootCauses } from './pages/DelaysRootCauses'
import { BaselinesActions } from './pages/BaselinesActions'

function App(){
  return <BrowserRouter>
    <div style={{fontFamily:'Arial',padding:20,maxWidth:1400,margin:'0 auto'}}>
      <h1>Atlas v2 Planner Twin</h1>
      <nav style={{display:'flex',gap:10,flexWrap:'wrap',marginBottom:10}}>
        <Link to='/portfolio'>Portfolio</Link>
        <Link to='/project/1/home'>Project Home</Link>
        <Link to='/project/1/activities'>Activities</Link>
        <Link to='/project/1/gantt'>Gantt & Dependencies</Link>
        <Link to='/project/1/materials'>Materials</Link>
        <Link to='/project/1/delays'>Delays & Root Causes</Link>
        <Link to='/project/1/baselines'>Baselines & Actions</Link>
      </nav>
      <Routes>
        <Route path='/' element={<Navigate to='/portfolio'/>}/>
        <Route path='/portfolio' element={<Portfolio/>}/>
        <Route path='/project/:id/home' element={<ProjectHome/>}/>
        <Route path='/project/:id/activities' element={<Activities/>}/>
        <Route path='/project/:id/gantt' element={<GanttDependencies/>}/>
        <Route path='/project/:id/materials' element={<Materials/>}/>
        <Route path='/project/:id/delays' element={<DelaysRootCauses/>}/>
        <Route path='/project/:id/baselines' element={<BaselinesActions/>}/>
      </Routes>
    </div>
  </BrowserRouter>
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />)
