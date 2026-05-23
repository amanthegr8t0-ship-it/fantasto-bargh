import { useState, useRef } from 'react'
import TTSTab from './TTSTab'
import PODCASTTAB from './PODCASTTAB'
import './App.css'

function App() {

  const [activemodel, setActiveModel] = useState("Jason")
  const [activeTab, setActiveTab] = useState("tts")

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI Audio Studio</p>
          <h1>Fantasto Baragh</h1>
        </div>
        <div className="model-control">
          <label htmlFor="model-select">Voice</label>
          <select id="model-select" value={activemodel} onChange={(e) => setActiveModel(e.target.value)}>
            <option value="Jason">Jason</option>
            <option value="Aria">Aria</option>
          </select>
        </div>
      </header>

      <div className="tabs">
        <button className={`tab-button ${activeTab === "tts" ? "active" : ""}`} onClick={() => setActiveTab("tts")}>Text to Speech</button>
        <button className={`tab-button ${activeTab === "podcast" ? "active" : ""}`} onClick={() => setActiveTab("podcast")}>PDF to Podcast</button>
      </div>

      <main className="tab-panel">
        {activeTab === "tts" && <TTSTab model={activemodel} />}
        {activeTab === "podcast" && <PODCASTTAB model={activemodel} />}
      </main>
    </div>
  )
}

export default App
