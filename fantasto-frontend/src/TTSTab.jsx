import { useState, useRef } from 'react'

function TTSTab({model}) {
  const [trackStatus, setTrackStatus] = useState("")
  const [finalTtsResult, setFinalTtsResult] = useState(null)
  const [ttxtext, setTtstext] = useState("")
  const [isloading, setisloading] = useState(false)
  const intervalRef = useRef(null)
  const API_URL = import.meta.env.VITE_API_URL
  const Send = async () => {
  if (!ttxtext.trim()) {
    alert("Please enter some text first.")
    setisloading(false)
    return
}
try{
  setTrackStatus("Pending")
  setisloading(true) 
  setFinalTtsResult(null)
    clearInterval(intervalRef.current)
  const response = await fetch(`${API_URL}/generate-text-to-speech`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: ttxtext, model: model })})
  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`)
}
  const data = await response.json()
  console.log(data)
  intervalRef.current = setInterval(async () => {
  const statusResponse = await fetch(`${API_URL}/job/tts/${data.job_id}`)
  
  const contentType = statusResponse.headers.get("content-type")
  if (contentType === "audio/mpeg") {
    console.log(contentType)
    clearInterval(intervalRef.current)
    const audioBlob = await statusResponse.blob()
    setFinalTtsResult(audioBlob)
    setTrackStatus("completed")
    setisloading(false)
  } else {
    const statusData = await statusResponse.json()
    setTrackStatus(statusData.status)
  }
}, 3000)
}
catch(e){
  setisloading(false)
  setTrackStatus(e.message)
}
  }
  return (
    <div className="panel panel-tts">
      <label className="field-label" htmlFor="tts-text">Enter your text</label>
      <textarea
        id="tts-text"
        className="panel-textarea"
        value={ttxtext}
        onChange={(e) => setTtstext(e.target.value)}
        placeholder="Enter Your Text Here"
      ></textarea>
      <div className="panel-actions">
        <button className="primary-button" onClick={Send} disabled={isloading}>Send</button>
        {isloading ? (
  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
    <div className="spinner"></div>
    <span className="status-text">{trackStatus}</span>
  </div>
) : (
  <span className="status-text">{trackStatus}</span>
)}
        
      </div>
      {finalTtsResult && (
        <div className="audio-card">
          <audio className="audio-player" controls src={URL.createObjectURL(finalTtsResult)} />
        </div>
      )}
    </div>
  )
}

export default TTSTab