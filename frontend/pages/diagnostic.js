import React, {useEffect, useState} from 'react'

export default function Diagnostic(){
  const [info, setInfo] = useState({status: 'checking'})
  useEffect(()=>{
    async function fetchInfo(){
      try{
        const h = await fetch(process.env.NEXT_PUBLIC_API_BASE + '/health');
        const v = await fetch(process.env.NEXT_PUBLIC_API_BASE + '/version');
        const hj = await h.json();
        const vj = await v.json();
        setInfo({health: hj, version: vj});
      }catch(e){
        setInfo({error: String(e)})
      }
    }
    fetchInfo()
  }, [])

  return (
    <main style={{fontFamily:'system-ui, -apple-system, Roboto, Arial', padding:20}}>
      <h1>RealDiag — Diagnostic UI (Next)</h1>
      <p>This minimal Next.js page calls the API backend.</p>
      <pre style={{background:'#f6f8fa',padding:12,borderRadius:6}}>{JSON.stringify(info, null, 2)}</pre>
    </main>
  )
}
