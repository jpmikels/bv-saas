'use client'
import { useState } from 'react'

export default function Home(){
  const [file, setFile] = useState<File|null>(null)
  const [msg, setMsg] = useState('')

  const upload = async () => {
    if(!file) return
    setMsg('Uploading...')
    // Replace with your API when implemented; for now just show success
    setTimeout(()=> setMsg('Uploaded (mock). Connect to API /v1/uploads to complete.'), 600)
  }

  return (
    <main>
      <h1>BV SaaS</h1>
      <input type="file" onChange={e=>setFile(e.target.files?.[0]??null)} />
      <button onClick={upload} style={{marginLeft:8}}>Upload</button>
      <p>{msg}</p>
    </main>
  )
}
