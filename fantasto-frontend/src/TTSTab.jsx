
import { useState, useRef } from 'react'
function TTSTab({model}) {const [trackStatus, setTrackStatus] = useState("")
  const [finalTtsResult, setFinalTtsResult] = useState(null)
const [ttxtext, setTtstext] = useState("")
const [isloading, setisloading] = useState(false)
const intervalRef = useRef(null)

const Send = async () => {setTrackStatus("")
  if (!ttxtext.trim()) {
    alert("Please enter some text first.")
    setisloading(false)
    return
}
try{
  setisloading(true) 
  setFinalTtsResult(null)
    clearInterval(intervalRef.current)
  const response = await fetch("http://127.0.0.1:8000/generate-text-to-speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: ttxtext, model: model })})
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
  setTrackStatus("Failed.Try again")
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
        <span className="status-text">{trackStatus}</span>
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