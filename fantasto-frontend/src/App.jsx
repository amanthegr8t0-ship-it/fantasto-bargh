import { useState, useRef } from 'react'
import TTSTab from './TTSTab'
import PODCASTTAB from './PODCASTTAB'
import './App.css'

function App() {

  const [activemodel, setActiveModel] = useState("Jason")
  const [activeTab, setActiveTab] = useState("tts")

  return (
    <>
      <h1>Fantasto Baragh</h1>
      <button onClick={() => setActiveTab("tts")}>Text to Speech</button>
      <button onClick={() => setActiveTab("podcast")}>PDF To Podcast</button>
      <select value={activemodel} onChange={(e) => setActiveModel(e.target.value)}>
        <option value="Jason">Jason</option>
        <option value="Aria">Aria</option>
      </select>
      {activeTab === "tts" && <TTSTab model={activemodel} />}
      {activeTab === "podcast" && <PODCASTTAB model={activemodel} />}
    </>
  )
}

export default App
