import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DocumentUpload from './components/documents/DocumentUpload'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <main className="container mx-auto p-6">
          <Routes>
            <Route path="/" element={<DocumentUpload />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App