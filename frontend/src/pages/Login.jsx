import { useState } from 'react'
import { apiFetch } from '../api'

export function Login(){
  const [email,setEmail]=useState('admin@atlas.local')
  const [password,setPassword]=useState('admin123')
  const [token,setToken]=useState('')
  const submit=async()=>{
    const r=await apiFetch('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})})
    const data=await r.json();
    setToken(data.access_token||JSON.stringify(data))
  }
  return <div>
    <h2>Login</h2>
    <input value={email} onChange={e=>setEmail(e.target.value)} placeholder='email'/> <br/>
    <input type='password' value={password} onChange={e=>setPassword(e.target.value)} placeholder='password'/> <br/>
    <button onClick={submit}>Sign in</button>
    <p style={{wordBreak:'break-all'}}>Token: {token}</p>
  </div>
}
