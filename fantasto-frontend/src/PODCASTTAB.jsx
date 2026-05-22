import { useState, useRef } from 'react'


function PODCASTTAB({model}){
  const [trackStatus, setTrackStatus] = useState("")
  const [finalResult, setFinalResult] = useState(null)
  const [pdfFile, setPdfFile] = useState(null)
  const intervalRef = useRef(null)


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
      body: JSON.stringify({ text: extractedText, model: model })})
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
  return(<div> <input type="file" accept='.pdf' onChange={(e) => setPdfFile(e.target.files[0])}/> <button onClick={Generate}>Generate</button> {finalResult && <audio controls src={URL.createObjectURL(finalResult)} />} </div>
    )
}

export default PODCASTTAB