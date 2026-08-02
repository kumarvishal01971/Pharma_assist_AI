import { useState, useRef } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { extractFromText, extractFromFile, sendChatMessage } from '../store/complaintSlice'

function riskClass(level) {
  if (!level) return ''
  return `risk-${level.toLowerCase()}`
}

export default function AICopilotPanel() {
  const dispatch = useDispatch()
  const [pasteText, setPasteText] = useState('')
  const [dragging, setDragging] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const fileInputRef = useRef(null)

  const {
    extractionStatus,
    extractionProgressLabel,
    extractionError,
    completenessScore,
    missingFields,
    aiRiskClassification,
    aiRiskRationale,
    aiSummary,
    possibleDuplicateIds,
    chatMessages,
    chatStatus,
  } = useSelector((s) => s.complaint)

  const loading = extractionStatus === 'loading'

  const handleFile = (file) => {
    if (!file) return
    dispatch(extractFromFile(file))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const submitPaste = () => {
    if (!pasteText.trim()) return
    dispatch(extractFromText(pasteText))
  }

  const submitChat = () => {
    if (!chatInput.trim()) return
    dispatch(sendChatMessage(chatInput))
    setChatInput('')
  }

  return (
    <section className="panel copilot-panel">
      <div className="copilot-header">
        <h2>
          <span className="copilot-icon">✦</span>
          AI Complaint Intake Assistant
        </h2>
        <span className="status-badge beta">BETA</span>
      </div>

      <div className="copilot-body">
        <div
          className={`dropzone ${dragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          ⬆ Drag &amp; drop complaint document here
          <br />
          or <span className="browse-link">click to browse</span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.eml"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>

        <div className="divider-or">OR</div>

        <div className="paste-area">
          <textarea
            placeholder="Paste Complaint Text / Email"
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
          />
          <button
            className="btn btn-primary"
            style={{ marginTop: 8, width: '100%', justifyContent: 'center' }}
            disabled={loading || !pasteText.trim()}
            onClick={submitPaste}
          >
            {loading ? 'Extracting...' : 'Extract from Pasted Text'}
          </button>
        </div>

        <div className="format-hint">
          ⓘ Supported formats: PDF, DOCX, TXT, EML · Max file size: 10MB
        </div>

        {loading && (
          <div className="extraction-progress">
            <div className="label">Extraction Progress</div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: '65%' }} />
            </div>
            <div className="progress-caption">{extractionProgressLabel}</div>
          </div>
        )}

        {extractionError && <div className="error-banner">{extractionError}</div>}

        {extractionStatus === 'succeeded' && (
          <>
            <div className="ai-insight-card">
              <div className="k">Completeness</div>
              {completenessScore}% complete
              {missingFields.length > 0 && (
                <> — missing: {missingFields.join(', ')}</>
              )}
            </div>

            {aiRiskClassification && (
              <div className="ai-insight-card">
                <div className="k">AI Risk Classification</div>
                <span className={riskClass(aiRiskClassification)}>
                  <strong>{aiRiskClassification}</strong>
                </span>
                {aiRiskRationale && <div style={{ marginTop: 4, color: 'var(--text-secondary)' }}>{aiRiskRationale}</div>}
              </div>
            )}

            {aiSummary && (
              <div className="ai-insight-card">
                <div className="k">Complaint Summary</div>
                {aiSummary}
              </div>
            )}

            {possibleDuplicateIds.length > 0 && (
              <div className="duplicate-warning">
                ⚠ Possible duplicate of {possibleDuplicateIds.length} existing complaint(s) with the same batch/product.
              </div>
            )}
          </>
        )}

        {extractionStatus === 'idle' && (
          <div className="ai-assistant-box">
            <div className="avatar">✦</div>
            <div>
              Upload a complaint document or paste text above. I will automatically extract the
              details and populate the form for you.
            </div>
          </div>
        )}
      </div>

      <div className="chat-log">
        {chatMessages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>{m.content}</div>
        ))}
        {chatStatus === 'loading' && <div className="chat-msg assistant">Thinking...</div>}
      </div>

      <div className="chat-input-row">
        <input
          placeholder="Ask me anything about this complaint..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitChat()}
        />
        <button className="chat-send" onClick={submitChat} disabled={!chatInput.trim()}>➤</button>
      </div>
      <div className="chat-disclaimer">AI responses may contain errors. Please verify information.</div>
    </section>
  )
}
