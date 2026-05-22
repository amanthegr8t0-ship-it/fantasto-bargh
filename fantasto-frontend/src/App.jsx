import { useState } from 'react'
import { useRef } from 'react'
import './App.css'

function App() {

  const [activeTab, setActiveTab] = useState("tts")
  const [activemodel, setActiveModel] = useState("Jason")
  const [ttxtext, setTtstext] = useState("")
  const [trackStatus, setTrackStatus] = useState("")
  const [finalResult, setFinalResult] = useState(null)
  const [finalTtsResult, setFinalTtsResult] = useState(null)
  const [pdfFile, setPdfFile] = useState(null)
  const intervalRef = useRef(null)

  
  const Send = async () => {clearInterval(intervalRef.current)
  const response = await fetch("http://127.0.0.1:8000/generate-text-to-speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: ttxtext, model: activemodel })})
  const data = await response.json()
  console.log(data)
  intervalRef.current = setInterval(async () => {
  const statusResponse = await fetch(`http://127.0.0.1:8000/job/tts/${data.job_id}`)
  
  const contentType = statusResponse.headers.get("content-type")
  if (contentType === "audio/mpeg") {
    console.log(contentType)
    clearInterval(intervalRef.current)
    const audioBlob = await statusResponse.blob()
    setFinalTtsResult(audioBlob)
  } else {
  const statusData = await statusResponse.json()
  setTrackStatus(statusData.status)
  }
  }, 3000)
  }
  
  const Generate = async () => {clearInterval(intervalRef.current)
    const formData = new FormData()
    formData.append("file", pdfFile)
    const extractResponse = await fetch("http://127.0.0.1:8000/extract-pdf-text", {
        method: "POST",
        body: formData
      })
    const extractedText = await extractResponse.text()

    const response = await fetch("http://127.0.0.1:8000/generate-pdf-to-podcast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: extractedText, model: activemodel })})
    const data = await response.json()
    console.log(data)
    intervalRef.current = setInterval(async () => {
    const statusResponse = await fetch(`http://127.0.0.1:8000/job/podcast/${data.job_id}`)
    
    const contentType = statusResponse.headers.get("content-type")
    if (contentType === "audio/mpeg") {
      console.log(contentType)
      clearInterval(intervalRef.current)
      const audioBlob = await statusResponse.blob()
      setFinalResult(audioBlob)
    } else {
    const statusData = await statusResponse.json()
    setTrackStatus(statusData.status)
    }
    }, 3000)
  }

  return (
    <>
      <h1>Fantasto Baragh</h1>
      <button onClick={() => setActiveTab("tts")}>Text to Speech</button>
      <button onClick={() => setActiveTab("podcast")}>PDF To Podcast</button>
      <select value={activemodel} onChange={(e) => setActiveModel(e.target.value)}>
        <option value="Jason">Jason</option>
        <option value="Aria">Aria</option>
      </select>
      {activeTab === "tts" && <div> <textarea value={ttxtext} onChange={(e) => setTtstext(e.target.value)}placeholder="Enter Your Text Here"></textarea>  <button onClick={Send}>Send</button> <p>{trackStatus}</p>
      {finalTtsResult && <audio controls src={URL.createObjectURL(finalTtsResult)} />} </div>}
      {activeTab === "podcast" && <div> <input type="file" accept='.pdf' onChange={(e) => setPdfFile(e.target.files[0])}/> <button onClick={Generate}>Generate</button> {finalResult && <audio controls src={URL.createObjectURL(finalResult)} />} </div>}
    </>
  )
}

export default App
