
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, FileText, X, CheckCircle2, AlertCircle,
  Loader2, RefreshCw
} from 'lucide-react'
import { resumeAPI } from '../services/api'

const MAX_SIZE = 5 * 1024 * 1024
const ALLOWED_TYPES = ['pdf', 'docx']

export default function ResumeUpload() {
  const navigate = useNavigate()
  const inputRef = useRef(null)

  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('idle')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  function validateFile(selected) {
    if (!selected) return 'Please select a file.'

    const extension = selected.name.split('.').pop().toLowerCase()

    if (!ALLOWED_TYPES.includes(extension)) {
      return 'Only PDF and DOCX files are supported.'
    }

    if (selected.size === 0) return 'The selected file is empty.'
    if (selected.size > MAX_SIZE) return 'File size must not exceed 5 MB.'

    return ''
  }

  function selectFile(selected) {
    const validationError = validateFile(selected)

    setError(validationError)
    setMessage('')
    setResult(null)
    setProgress(0)
    setStage('idle')

    if (!validationError) setFile(selected)
    else setFile(null)
  }

  async function handleUpload() {
    if (!file || stage === 'uploading' || stage === 'processing') return

    setError('')
    setMessage('')
    setProgress(0)
    setStage('uploading')

    try {
      const uploadResponse = await resumeAPI.upload(file, (event) => {
        if (event.total) {
          setProgress(Math.round((event.loaded * 100) / event.total))
        }
      })

      const uploaded = uploadResponse.data
      setResult(uploaded)
      setStage('processing')
      setMessage('Resume uploaded. Starting AI processing...')

      try {
        const processResponse = await resumeAPI.process(uploaded.resume_id)
        const processingResult = processResponse.data

        if (processingResult.success === false ||
            processingResult.processing_status === 'failed') {
          throw new Error(processingResult.message || 'AI processing failed.')
        }

        setStage('success')
        setMessage('Resume uploaded and AI processing completed successfully.')
      } catch (processingError) {
        setStage('processing_failed')
        setError(
          processingError.response?.data?.message ||
          processingError.message ||
          'Resume uploaded, but AI processing failed.'
        )
      }
    } catch (uploadError) {
      const statusCode = uploadError.response?.status

      setStage('upload_failed')
      setError(
        uploadError.response?.data?.error ||
        (statusCode === 409
          ? 'This resume has already been uploaded.'
          : uploadError.message || 'Resume upload failed.')
      )
    }
  }

  function resetUpload() {
    setFile(null)
    setProgress(0)
    setStage('idle')
    setMessage('')
    setError('')
    setResult(null)

    if (inputRef.current) inputRef.current.value = ''
  }

  const busy = ['uploading', 'processing'].includes(stage)

  return (
    <div className="max-w-3xl mx-auto space-y-7">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Upload Resumes
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload candidate resumes to extract information and generate AI rankings.
        </p>
      </div>

      <div
        onDragOver={(event) => {
          event.preventDefault()
          if (!busy) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault()
          setDragging(false)
          if (!busy) selectFile(event.dataTransfer.files[0])
        }}
        onClick={() => {
          if (!busy) inputRef.current?.click()
        }}
        className={`bg-white border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition ${
          dragging
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-slate-300 hover:border-indigo-400'
        } ${busy ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          disabled={busy}
          onChange={(event) => selectFile(event.target.files[0])}
        />

        <div className="w-16 h-16 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
          <Upload size={30} />
        </div>

        <h2 className="font-semibold text-slate-800 mt-5">
          Drag and drop your resume here
        </h2>

        <p className="text-sm text-slate-500 mt-2">
          or click to browse files
        </p>

        <p className="text-xs text-slate-400 mt-4">
          Supported formats: PDF, DOCX · Maximum size: 5 MB
        </p>
      </div>

      {file && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4">
          <FileText className="text-indigo-600" size={28} />

          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm truncate">{file.name}</p>
            <p className="text-xs text-slate-500">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>

          {!busy && (
            <button onClick={resetUpload} className="text-slate-400 hover:text-red-500">
              <X size={20} />
            </button>
          )}
        </div>
      )}

      {stage === 'uploading' && (
        <div className="bg-white border rounded-xl p-5">
          <div className="flex justify-between text-sm mb-3">
            <span className="font-medium">Uploading resume...</span>
            <span>{progress}%</span>
          </div>

          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {stage === 'processing' && (
        <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-5 flex gap-3">
          <Loader2 className="text-indigo-600 animate-spin" />
          <div>
            <p className="font-semibold text-indigo-900">AI processing in progress</p>
            <p className="text-sm text-indigo-700 mt-1">
              The resume has been uploaded. Django is now running the processing pipeline.
            </p>
          </div>
        </div>
      )}

      {message && stage === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 flex gap-3">
          <CheckCircle2 className="text-green-600" />
          <div>
            <p className="font-semibold text-green-800">Processing completed</p>
            <p className="text-sm text-green-700 mt-1">{message}</p>
            {result && (
              <p className="text-xs text-green-700 mt-2">
                Resume ID: {result.resume_id} · {result.extraction_status}
              </p>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 flex gap-3">
          <AlertCircle className="text-red-600 shrink-0" />
          <div>
            <p className="font-semibold text-red-800">Attention required</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            {stage === 'processing_failed' && (
              <p className="text-xs text-red-700 mt-2">
                The resume was uploaded successfully. You can retry processing later.
              </p>
            )}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleUpload}
          disabled={!file || busy}
          className="px-6 py-3 rounded-lg bg-indigo-600 text-white font-medium text-sm hover:bg-indigo-700 disabled:opacity-40"
        >
          {busy ? 'Please wait...' : 'Upload and Process'}
        </button>

        {(stage === 'success' || stage === 'processing_failed' || stage === 'upload_failed') && (
          <button
            onClick={resetUpload}
            className="px-5 py-3 rounded-lg border border-slate-200 text-slate-700 text-sm flex items-center gap-2"
          >
            <RefreshCw size={16} /> Upload Another
          </button>
        )}

        {stage === 'success' && (
          <button
            onClick={() => navigate('/')}
            className="px-5 py-3 rounded-lg border border-slate-200 text-slate-700 text-sm"
          >
            View Dashboard
          </button>
        )}
      </div>
    </div>
  )
}
