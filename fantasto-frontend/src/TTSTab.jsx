
import { useState, useRef } from 'react'
function TTSTab({model}) {const [trackStatus, setTrackStatus] = useState("")
const [finalTtsResult, setFinalTtsResult] = useState(null)
const [ttxtext, setTtstext] = useState("")
const [isloading, setisloading] = useState(false)
const intervalRef = useRef(null)

const Send = async () => {setisloading(true) 
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
    setisloading(false)
  } else {
  const statusData = await statusResponse.json()
  setTrackStatus(statusData.status)
  }
  }, 3000)
  }
  return ( <div> <textarea value={ttxtext} onChange={(e) => setTtstext(e.target.value)}placeholder="Enter Your Text Here"></textarea>  <button onClick={Send} disabled={isloading}>Send</button> <p>{trackStatus}</p>
      {finalTtsResult && <audio controls src={URL.createObjectURL(finalTtsResult)} />} </div>)
      }

export default TTSTab