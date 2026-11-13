
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Search, ChevronLeft, ChevronRight } from 'lucide-react'
import { rankingAPI } from '../services/api'

const PAGE_SIZE = 10

const scoreValue = (candidate) => (
  candidate.score == null ? -Infinity : Number(candidate.score)
)

const providedRank = (candidate) => {
  const value = candidate.rank ?? candidate.rank_position ?? candidate.position
  const rank = Number(value)

  return Number.isInteger(rank) && rank > 0 ? rank : null
}

export default function JobRankings() {
  const { jobId } = useParams()
  const navigate = useNavigate()

  const [candidates, setCandidates] = useState([])
  const [search, setSearch] = useState('')
  const [classification, setClassification] = useState('all')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')

    rankingAPI.getByJob(jobId)
      .then(({ data }) => {
        setCandidates(Array.isArray(data) ? data : data.results ?? [])
      })
      .catch(() => setError('Unable to load candidate rankings.'))
      .finally(() => setLoading(false))
  }, [jobId])

  const rankedCandidates = useMemo(() => (
    [...candidates]
      .sort((first, second) => scoreValue(second) - scoreValue(first))
      .map((candidate, index) => ({
        ...candidate,
        displayRank: providedRank(candidate) ?? index + 1,
      }))
  ), [candidates])

  const filtered = useMemo(() => {
    let result = rankedCandidates.filter((candidate) => {
      const name = `${candidate.candidate_identifier} ${candidate.original_filename}`.toLowerCase()
      return name.includes(search.toLowerCase())
    })

    // Until classification thresholds are calibrated,
    // all candidates remain pending human assessment.
    if (classification === 'review') {
      result = result.filter(() => true)
    }

    return result
  }, [rankedCandidates, search, classification])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)

  const visibleCandidates = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  )

  useEffect(() => {
    setPage(1)
  }, [search, classification])

  const title = jobId === 'JD1' ? 'LCA Consultant' : 'UI/UX Designer Intern'

  if (loading) return <p className="text-slate-500">Loading rankings...</p>

  if (error) return <p className="text-red-600">{error}</p>

  return (
    <div className="space-y-6">
      <div>
        <button
          onClick={() => navigate('/jobs')}
          className="text-sm text-indigo-600 mb-3"
        >
          ← Back to Job Profiles
        </button>

        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        <p className="text-sm text-slate-500 mt-1">
          {jobId} · {filtered.length} ranked candidates
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={18} className="absolute left-3 top-3 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidate..."
            className="w-full border border-slate-200 rounded-lg pl-10 pr-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-100"
          />
        </div>

        <select
          value={classification}
          onChange={(e) => setClassification(e.target.value)}
          className="border border-slate-200 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All candidates</option>
          <option value="review">Human review required</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-4 font-semibold">Rank</th>
                <th className="px-5 py-4 font-semibold">Candidate</th>
                <th className="px-5 py-4 font-semibold">Score</th>
                <th className="px-5 py-4 font-semibold">Classification</th>
                <th className="px-5 py-4 font-semibold">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {visibleCandidates.map((candidate) => (
                <tr key={candidate.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4">
                    <span className="font-bold text-indigo-600">#{candidate.displayRank}</span>
                  </td>
                  <td className="px-5 py-4">
                    <p className="font-semibold text-slate-800">
                      {candidate.candidate_identifier || 'Unknown'}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {candidate.original_filename}
                    </p>
                  </td>

                  <td className="px-5 py-4 font-bold text-slate-800">
                    {candidate.score == null ? 'N/A' : Number(candidate.score).toFixed(2)}
                  </td>

                  <td className="px-5 py-4">
                    <span className="px-3 py-1 rounded-full text-xs bg-amber-50 text-amber-700">
                      Human review
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <button
                      onClick={() => navigate(`/candidates/${candidate.resume_id}`)}
                      className="font-semibold text-indigo-600 hover:text-indigo-800"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}

              {visibleCandidates.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-slate-500">
                    No candidates found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="border-t border-slate-100 p-4 flex items-center justify-between">
          <p className="text-xs text-slate-500">
            Page {currentPage} of {totalPages} · {filtered.length} candidates
          </p>

          <div className="flex gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setPage((p) => p - 1)}
              className="p-2 border rounded-lg disabled:opacity-30"
            >
              <ChevronLeft size={17} />
            </button>

            <button
              disabled={currentPage === totalPages}
              onClick={() => setPage((p) => p + 1)}
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
