import { useState, useRef } from 'react'


function PODCASTTAB({model}){
  const [trackStatus, setTrackStatus] = useState("")
  const [finalResult, setFinalResult] = useState(null)
  const [isloading, setisloading] = useState(false)
  const [Qarea, setQarea] = useState(false)
  const [pdfFile, setPdfFile] = useState(null)
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [clarifyQuestion, setClarifyQuestion] = useState("")
  const [outOfContext, setOutOfContext] = useState("")
  const [clarificationAnswer, setClarificationAnswer] = useState("")
  const originalQuestion = useRef("")
  const [lMemo, setLMemo] = useState("")
  const [mode, setMode] = useState("question")
  const [jobId, setJobId] = useState(null)
  const intervalRef = useRef(null)


  const Generate = async () => {setTrackStatus("")
    if (!pdfFile) {
    alert("Please upload a PDF first.")
    setisloading(false)
    return
}try {
    setisloading(true)
    setFinalResult(null)
    clearInterval(intervalRef.current)
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
    console.log(data.answer)
    console.log(data)
    setJobId(data.job_id)
    intervalRef.current = setInterval(async () => {
    const statusResponse = await fetch(`http://127.0.0.1:8000/job/podcast/${data.job_id}`)
    
    const contentType = statusResponse.headers.get("content-type")
    if (contentType === "audio/mpeg") {
      console.log(contentType)
      clearInterval(intervalRef.current)
      const audioBlob = await statusResponse.blob()
      setFinalResult(audioBlob)
      setTrackStatus("completed")
      setisloading(false)
    } else {
    const statusData = await statusResponse.json()
    setTrackStatus(statusData.status)
    }
    }, 3000)
  }
    catch (e) {
        setisloading(false)
        setTrackStatus("Failed.Try again")
    }
  }

const Question = async () => {
  setOutOfContext("")
  setAnswer("")
  setClarifyQuestion("")
  console.log(mode)
    const response = await fetch("http://127.0.0.1:8000/ask-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    if (data.answer.startsWith("ANSWER:")){
      setAnswer(data.answer.replace("ANSWER:", "").trim())
      setLMemo(data.live_memory)
      setMode("question")
    }
    else if (data.answer.startsWith("CLARIFY:")){
      setClarifyQuestion(data.answer.replace("CLARIFY:", "").trim())
      originalQuestion.current=question
      setMode("clarify")
      
    }
    else if (data.answer.startsWith("OUT_OF_CONTEXT:")){
      setOutOfContext(data.answer.replace("OUT_OF_CONTEXT:", "").trim())
      originalQuestion.current=question
      setMode("out_of_context")
      
    }
    
  }
  const SubmitClarification = async () => {
    const combinedQuestion = `Original question: ${originalQuestion.current}\nClarifying question: ${clarifyQuestion}\nUser's answer: ${clarificationAnswer}`
    const response = await fetch("http://127.0.0.1:8000/ask-question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: combinedQuestion, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    setAnswer(data.answer.replace("ANSWER:", "").trim())
    setLMemo(data.live_memory)
    setMode("question")
    setClarificationAnswer("")
  }

  const SubmitoutOfContext = async () => {
    const combinedQuestion = `Original question: ${originalQuestion.current}\nopen to general answer: ${outOfContext}`
    const response = await fetch("http://127.0.0.1:8000/ask-question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: combinedQuestion, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    setAnswer(data.answer.replace("ANSWER:", "").trim())
    setLMemo(data.live_memory)
    setMode("question")

      }

  return (
    <div className="panel panel-podcast">
      <div className="file-input-group">
        <label className="field-label" htmlFor="pdf-upload">Upload PDF</label>
        <input
          id="pdf-upload"
          className="file-input"
          type="file"
          accept='.pdf'
          onChange={(e) => setPdfFile(e.target.files[0])}
        />
        
      </div>
      <div className="panel-actions">
        <button className="primary-button" onClick={Generate} disabled={isloading}>Generate</button>
        <span className="status-text">{trackStatus}</span>
      </div>
      {finalResult && (
  <div>
    <div className="audio-card">
      <audio className="audio-player" controls src={URL.createObjectURL(finalResult)} />
    </div>
    <button className="primary-button" onClick={() => setQarea(!Qarea)}>Ask a Question</button>
    {Qarea && (
      <div>
        {mode !== "out_of_context" && (
  <div>
  <textarea
        value={mode === "clarify" ? clarificationAnswer : question}
        onChange={(e) => mode === "clarify" ? setClarificationAnswer(e.target.value) : setQuestion(e.target.value)}
        placeholder={mode === "clarify" ? "Enter your clarification..." : "Enter Your Question."}
        />
        <div className="panel-actions">
          <button className="primary-button" onClick={
            mode === "question" ? Question :
            mode === "clarify" ? SubmitClarification :
            SubmitoutOfContext
          } disabled={isloading}>Send</button>
        </div>
      </div>
      
    )}
    {clarifyQuestion && <div>{clarifyQuestion}</div>}
    {outOfContext && (
      <div>
        <p>{outOfContext}</p>
        <button className="primary-button" onClick={SubmitoutOfContext}>Yes, get general answer</button>
        <button className="primary-button" onClick={() => { setOutOfContext(""); setMode("question") }}>No thanks</button>
      </div>
    )}
    {answer && <div>{answer}</div>}
  </div>
)}
</div>
)}
</div>
)
}

export default PODCASTTAB