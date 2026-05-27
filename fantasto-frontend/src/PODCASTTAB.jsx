import { useState, useRef } from 'react'


function PODCASTTAB({model}){
  const [trackStatus, setTrackStatus] = useState("")
  const [finalResult, setFinalResult] = useState(null)
  const [isloading, setisloading] = useState(false)
  const [Qarea, setQarea] = useState(false)
  const [isQALoading, setIsQALoading] = useState(false)
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
  const API_URL = import.meta.env.VITE_API_URL


  const Generate = async () => {
    
    
    if (!pdfFile) {
    alert("Please upload a PDF first.")
    setisloading(false)
    return
}try {setTrackStatus("pending")
    setisloading(true)
    setFinalResult(null)
    clearInterval(intervalRef.current)
    const formData = new FormData()
    formData.append("file", pdfFile)
    const extractResponse = await fetch(`${API_URL}/extract-pdf-text`, {
        method: "POST",
        body: formData
      })
    const extractedText = await extractResponse.text()

    const response = await fetch(`${API_URL}/generate-pdf-to-podcast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: extractedText, model: model })})
    const data = await response.json()
    console.log(data.answer)
    console.log(data)
    setJobId(data.job_id)
    intervalRef.current = setInterval(async () => {
    const statusResponse = await fetch(`${API_URL}/job/podcast/${data.job_id}`)
    
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
    setTrackStatus(statusData.Status)
    }
    }, 3000)
  }
    catch (e) {
        setisloading(false)
        setTrackStatus(e.message)
    }
  }

const Question = async () => {
  setIsQALoading(true)
  setOutOfContext("")
  setAnswer("")
  setClarifyQuestion("")
  console.log(mode)
    const response = await fetch(`${API_URL}/ask-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    if (data.answer.startsWith("ANSWER:")){
      setAnswer(data.answer.replace("ANSWER:", "").trim())
      setLMemo(data.live_memory)
      setIsQALoading(false)
      setMode("question")
    }
    else if (data.answer.startsWith("CLARIFY:")){
      setClarifyQuestion(data.answer.replace("CLARIFY:", "").trim())
      originalQuestion.current=question
      setMode("clarify")
      setIsQALoading(false)
      
    }
    else if (data.answer.startsWith("OUT_OF_CONTEXT:")){
      setOutOfContext(data.answer.replace("OUT_OF_CONTEXT:", "").trim())
      originalQuestion.current=question
      setMode("out_of_context")
      setIsQALoading(false)
      
    }
    
  }
  const SubmitClarification = async () => {
    setAnswer("")
    setClarifyQuestion("")
    setIsQALoading(true)
    const combinedQuestion = `Original question: ${originalQuestion.current}\nClarifying question: ${clarifyQuestion}\nUser's answer: ${clarificationAnswer}`
    const response = await fetch(`${API_URL}/ask-question`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: combinedQuestion, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    setAnswer(data.answer.replace("ANSWER:", "").trim())
    setLMemo(data.live_memory)
    setMode("question")
    setClarificationAnswer("")
    setIsQALoading(false)
  }

  const SubmitoutOfContext = async () => {
    setAnswer("")
    setIsQALoading(true)
    const combinedQuestion = `Original question: ${originalQuestion.current}\nopen to general answer: ${outOfContext}`
    setOutOfContext("")
    const response = await fetch(`${API_URL}/ask-question`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: combinedQuestion, job_id: jobId, live_memory: lMemo })
    })
    const data = await response.json()
    setAnswer(data.answer.replace("ANSWER:", "").replace("OUT_OF_CONTEXT:", "").trim())
    setLMemo(data.live_memory)
    setMode("question")
    setIsQALoading(false)
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
        {isloading ? (
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div className="spinner"></div>
            <span className="status-text">{trackStatus}</span>
          </div>
        ) : (
          <span className="status-text">{trackStatus}</span>
        )}
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
        className="panel-textarea"
        style={{ minHeight: "100px" }}
        value={mode === "clarify" ? clarificationAnswer : question}
        onChange={(e) => mode === "clarify" ? setClarificationAnswer(e.target.value) : setQuestion(e.target.value)}
        placeholder={mode === "clarify" ? "Enter your clarification..." : "Enter Your Question."}
        />
        <div className="panel-actions">
          <button className="primary-button" onClick={
            mode === "question" ? Question :
            mode === "clarify" ? SubmitClarification :
            SubmitoutOfContext
          } disabled={isQALoading}>Send</button>
          {isQALoading && (
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div className="spinner"></div>
              <span>Thinking...</span>
            </div>
          )}
        </div>
      </div>
      
    )}
    {clarifyQuestion && <div className="answer-box">{clarifyQuestion}</div>}
   {outOfContext && (
  <div className="answer-box" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
    <p>{outOfContext}</p>
    <div style={{ display: "flex", gap: "12px" }}>
      <button className="primary-button" onClick={SubmitoutOfContext}>Yes, get general answer</button>
      <button className="primary-button" onClick={() => { setOutOfContext(""); setMode("question") }}>No thanks</button>
    </div>
  </div>
)}
    {answer && <div className="answer-box">{answer}</div>}
  </div>
)}
</div>
)}
</div>
)
}

export default PODCASTTAB