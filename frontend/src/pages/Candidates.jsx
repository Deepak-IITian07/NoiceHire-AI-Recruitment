
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, Users, FileText, Eye,
  ChevronLeft, ChevronRight, RefreshCw, Trash2
} from 'lucide-react'
import { resumeAPI } from '../services/api'

const PAGE_SIZE = 10

export default function Candidates() {
  const navigate = useNavigate()

  const [resumes, setResumes] = useState([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadCandidates() {
    setLoading(true)
    setError('')

    try {
      const { data } = await resumeAPI.getAll()
      setResumes(Array.isArray(data) ? data : data.results ?? [])
    } catch {
      setError('Unable to load candidates.')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id, name) {
    if (!window.confirm(`Permanently delete ${name}? This also removes their resume and ranking data.`)) return

    try {
        await resumeAPI.delete(id)
        setResumes(prev => prev.filter(resume => resume.id !== id))
    } catch {
        alert('Unable to delete candidate. Please try again.')
    }
    }

  useEffect(() => {
    loadCandidates()
  }, [])

  const filtered = useMemo(() => {
    return resumes.filter((resume) => {
      const query = search.toLowerCase()

      const matchesSearch =
        (resume.candidate_identifier || '').toLowerCase().includes(query) ||
        (resume.original_filename || '').toLowerCase().includes(query)

      const matchesStatus =
        status === 'all' || resume.extraction_status === status

      return matchesSearch && matchesStatus
    })
  }, [resumes, search, status])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)

  const visible = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  )

  useEffect(() => {
    setPage(1)
  }, [search, status])

  if (loading) {
    return (
      <div className="py-24 flex justify-center text-slate-500">
        <RefreshCw className="animate-spin mr-3" />
        Loading candidates...
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-5 rounded-xl">
        {error}
        <button onClick={loadCandidates} className="underline ml-3">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">

      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Candidates
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage and review all uploaded candidate resumes.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-5">
        <div className="bg-white border rounded-xl p-5">
          <div className="flex justify-between">
            <p className="text-sm text-slate-500">Total Candidates</p>
            <Users className="text-indigo-600" />
          </div>
          <h2 className="text-3xl font-bold mt-3">{resumes.length}</h2>
        </div>

        <div className="bg-white border rounded-xl p-5">
          <div className="flex justify-between">
            <p className="text-sm text-slate-500">Filtered Results</p>
            <FileText className="text-purple-600" />
          </div>
          <h2 className="text-3xl font-bold mt-3">{filtered.length}</h2>
        </div>
      </div>

      <div className="bg-white border rounded-xl p-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={18} className="absolute left-3 top-3 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidate..."
            className="w-full border rounded-lg pl-10 pr-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-100"
          />
        </div>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All extraction statuses</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
          <option value="empty_text">Empty text</option>
          <option value="ocr_unavailable">OCR unavailable</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-4">Candidate</th>
                <th className="px-5 py-4">Resume</th>
                <th className="px-5 py-4">Extraction Status</th>
                <th className="px-5 py-4">Uploaded</th>
                <th className="px-5 py-4">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {visible.map((resume) => (
                <tr key={resume.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4 font-semibold text-slate-800">
                    {resume.candidate_identifier || 'Unknown'}
                  </td>

                  <td className="px-5 py-4 text-slate-500 max-w-56 truncate">
                    {resume.original_filename}
                  </td>

                  <td className="px-5 py-4">
                    <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs">
                      {resume.extraction_status}
                    </span>
                  </td>

                  <td className="px-5 py-4 text-slate-500">
                    {resume.uploaded_at
                      ? new Date(resume.uploaded_at).toLocaleDateString()
                      : 'N/A'}
                  </td>

                  <td className="px-5 py-4">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate(`/candidates/${resume.id}`)}
                            className="flex items-center gap-2 text-indigo-600 font-semibold hover:text-indigo-800"
                        >
                            <Eye size={16} /> View
                        </button>

                        <button
                            onClick={() => handleDelete(resume.id, resume.candidate_identifier || 'this candidate')}
                            className="flex items-center gap-2 text-red-600 font-semibold hover:text-red-800"
                        >
                            <Trash2 size={16} /> Delete
                        </button>
                        </div>
                  </td>
                </tr>
              ))}

              {visible.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-slate-500">
                    No candidates found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="border-t p-4 flex justify-between items-center">
          <p className="text-xs text-slate-500">
            Page {currentPage} of {totalPages} · {filtered.length} candidates
          </p>

          <div className="flex gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setPage(p => p - 1)}
              className="p-2 border rounded-lg disabled:opacity-30"
            >
              <ChevronLeft size={17} />
            </button>

            <button
              disabled={currentPage === totalPages}
              onClick={() => setPage(p => p + 1)}
              className="p-2 border rounded-lg disabled:opacity-30"
            >
              <ChevronRight size={17} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
