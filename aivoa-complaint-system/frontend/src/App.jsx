import Header from './components/Header'
import ComplaintForm from './components/ComplaintForm'
import AICopilotPanel from './components/AICopilotPanel'

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <div className="main-grid">
        <ComplaintForm />
        <AICopilotPanel />
      </div>
    </div>
  )
}
