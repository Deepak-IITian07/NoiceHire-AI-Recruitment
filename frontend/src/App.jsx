import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/test/')
      .then(response => setData(response.data))
      .catch(error => setError(error.message))
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6">
        Resume Screening System
      </h1>

      {data && (
        <div className="text-center">
          <p className="text-green-400 font-bold">
            Backend Connected!
          </p>
          <p className="mt-2">{data.message}</p>
        </div>
      )}

      {error && (
        <p className="text-red-400">
          Connection Error: {error}
        </p>
      )}

      {!data && !error && <p>Connecting to backend...</p>}
    </div>
  )
}

export default App