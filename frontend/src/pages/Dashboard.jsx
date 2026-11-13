
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText, CheckCircle2, AlertCircle, BriefcaseBusiness,
  Users, RefreshCw, ArrowUpRight, TrendingUp, Target,
  BarChart3, Bell, CalendarDays, ChevronRight
} from 'lucide-react'
import { resumeAPI, rankingAPI } from '../services/api'


const normalize = (response) => {
  const data = response.data
  return Array.isArray(data) ? data : data?.results ?? []
}

const getScore = (item) => Number(item.score) || 0

const average = (items) =>
  items.length
    ? items.reduce((sum, item) => sum + getScore(item), 0) / items.length
    : 0

const median = (items) => {
  if (!items.length) return 0
  const scores = items.map(getScore).sort((a, b) => a - b)
  const mid = Math.floor(scores.length / 2)
  return scores.length % 2
    ? scores[mid]
    : (scores[mid - 1] + scores[mid]) / 2
}

const formatScore = (score) => score.toFixed(1)

function Panel({ title, icon: Icon, children, className = '' }) {
  return (
    <section className={`bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden ${className}`}>
      <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
        <span className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
          <Icon size={18} />
        </span>
        <h2 className="font-semibold text-slate-900">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}

function StatCard({ title, value, description, icon: Icon,color, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`text-left rounded-2xl p-5 border shadow-lg
        transition-all duration-200 hover:-translate-y-1 hover:shadow-xl
        ${color} ${onClick ? 'cursor-pointer' : 'cursor-default'}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium opacity-90">{title}</p>
        <span className="p-3 rounded-xl bg-white/20">
          <Icon size={22} />
        </span>
      </div>
      <div className="flex items-end justify-between mt-5">
        <span className="text-4xl font-bold">{value}</span>
        {onClick && <ChevronRight size={20} />}
      </div>
      <p className="text-xs mt-2 opacity-85">{description}</p>
    </button>
  )
}

function DonutChart({ successful, failed, pending, total }) {
  const successPercent = total ? successful / total * 100 : 0
  const failedPercent = total ? failed / total * 100 : 0

  const style = {
    background: total
      ? `conic-gradient(#16a34a 0% ${successPercent}%,
          #ef4444 ${successPercent}% ${successPercent + failedPercent}%,
          #cbd5e1 ${successPercent + failedPercent}% 100%)`
      : '#e2e8f0'
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-around gap-7">
      <div className="relative w-44 h-44 rounded-full shrink-0" style={style}>
        <div className="absolute inset-5 bg-white rounded-full flex flex-col items-center justify-center">
          <strong className="text-3xl text-slate-900">{total}</strong>
          <span className="text-xs text-slate-500">Resumes</span>
        </div>
      </div>

      <div className="space-y-4 w-full">
        {[
          ['Extracted Successfully', successful, '#16a34a'],
          ['Extraction Issues', failed, '#ef4444'],
          ['Pending / Other', pending, '#cbd5e1'],
        ].map(([label, value, color]) => (
          <div key={label} className="flex justify-between gap-3 text-sm">
            <span className="flex items-center gap-2 text-slate-600">
              <span className="w-3 h-3 rounded-full" style={{ background: color }} />
              {label}
            </span>
            <strong className="text-slate-800">{value}</strong>
          </div>
        ))}
      </div>
    </div>
  )
}

function DistributionChart({ candidates }) {
  const ranges = [
    { label: '0–20', min: 0, max: 20 },
    { label: '20–40', min: 20, max: 40 },
    { label: '40–60', min: 40, max: 60 },
    { label: '60–80', min: 60, max: 80 },
    { label: '80–100', min: 80, max: 101 },
  ]

  const counts = ranges.map(range =>
    candidates.filter(c =>
      getScore(c) >= range.min && getScore(c) < range.max
    ).length
  )

  const max = Math.max(...counts, 1)

  return (
    <div className="h-52 flex items-end justify-around gap-3 border-b border-l border-slate-200 px-3">
      {ranges.map((range, i) => (
        <div key={range.label} className="flex-1 h-full flex flex-col justify-end items-center gap-2">
          <span className="text-xs font-semibold text-slate-600">
            {counts[i]}
          </span>
          <div
            className="w-full max-w-14 bg-gradient-to-t from-indigo-700 to-violet-400 rounded-t-lg transition-all hover:opacity-80"
            style={{ height: `${Math.max(counts[i] / max * 72, 2)}%` }}
          />
          <span className="text-[10px] text-slate-500 whitespace-nowrap">
            {range.label}
          </span>
        </div>
      ))}
    </div>
  )
}

function TopTalent({ candidates }) {
  const sorted = [...candidates].sort((a, b) => getScore(b) - getScore(a))
  const topCount = Math.ceil(sorted.length * 0.25)
  const top = sorted.slice(0, topCount)

  const topAverage = average(top)
  const overallMedian = median(candidates)

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-32 overflow-hidden">
        <svg viewBox="0 0 200 110" className="w-full">
          <path
            d="M 15 100 A 85 85 0 0 1 185 100"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="15"
            strokeLinecap="round"
          />
          <path
            d="M 15 100 A 85 85 0 0 1 185 100"
            fill="none"
            stroke="#7c3aed"
            strokeWidth="15"
            strokeLinecap="round"
            pathLength="100"
            strokeDasharray="25 100"
          />
        </svg>
        <div className="absolute inset-x-0 bottom-1 text-center">
          <strong className="text-3xl text-slate-900">25%</strong>
          <p className="text-xs text-slate-500">Top candidates</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 w-full mt-4 text-center">
        <div>
          <strong className="text-xl">{topCount}</strong>
          <p className="text-xs text-slate-500">Candidates</p>
        </div>
        <div>
          <strong className="text-xl">{formatScore(topAverage)}</strong>
          <p className="text-xs text-slate-500">Average score</p>
        </div>
        <div>
          <strong className="text-xl">{formatScore(overallMedian)}</strong>
          <p className="text-xs text-slate-500">Median score</p>
        </div>
      </div>
    </div>
  )
}

function Comparison({ jd1, jd2 }) {
  const metrics = [
    ['Average score', average(jd1), average(jd2)],
    ['Median score', median(jd1), median(jd2)],
  ]

  return (
    <div className="space-y-6">
      {metrics.map(([label, first, second]) => (
        <div key={label}>
          <p className="text-sm font-medium text-slate-600 mb-3">{label}</p>
          {[
            ['JD1', first, '#7c3aed'],
            ['JD2', second, '#f59e0b'],
          ].map(([name, value, color]) => (
            <div key={name} className="mb-3">
              <div className="flex justify-between text-xs mb-1">
                <span>{name}</span>
                <strong>{formatScore(value)}</strong>
              </div>
              <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.max(0, Math.min(value, 100))}%`,
                    background: color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

function CandidateOverlap({ jd1, jd2 }) {
  const first = new Set(jd1.map(c => String(c.resume_id)))
  const second = new Set(jd2.map(c => String(c.resume_id)))

  const common = [...first].filter(id => second.has(id)).length
  const firstOnly = [...first].filter(id => !second.has(id)).length
  const secondOnly = [...second].filter(id => !first.has(id)).length
  const union = firstOnly + secondOnly + common
  const overlap = union ? common / union * 100 : 0

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-center h-44">
        <div className="flex items-center justify-center">
          <div className="w-36 h-36 rounded-full bg-violet-500/40 border border-violet-300 flex items-center justify-center -mr-7 z-10">
            <div className="text-center">
              <strong>JD1</strong>
              <p className="text-sm">{firstOnly + common}</p>
            </div>
          </div>
          <div className="w-36 h-36 rounded-full bg-orange-400/40 border border-orange-300 flex items-center justify-center -ml-7">
            <div className="text-center">
              <strong>JD2</strong>
              <p className="text-sm">{secondOnly + common}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <strong className="text-lg">{firstOnly}</strong>
          <p className="text-xs text-slate-500">JD1 only</p>
        </div>
        <div>
          <strong className="text-lg">{common}</strong>
          <p className="text-xs text-slate-500">Both</p>
        </div>
        <div>
          <strong className="text-lg">{secondOnly}</strong>
          <p className="text-xs text-slate-500">JD2 only</p>
        </div>
      </div>

      <p className="text-center text-sm font-semibold text-indigo-700 bg-indigo-50 rounded-lg p-3">
        Overlap: {overlap.toFixed(1)}% of ranked candidates
      </p>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadDashboard() {
    setLoading(true)
    setError('')

    try {
      const results = await Promise.allSettled([
        resumeAPI.getAll(),
        rankingAPI.getByJob('JD1'),
        rankingAPI.getByJob('JD2'),
      ])

      if (results[0].status === 'rejected') {
        throw new Error('Unable to load resumes. Check the Django API.')
      }

      const resumes = normalize(results[0].value)
      const jd1 = results[1].status === 'fulfilled'
        ? normalize(results[1].value) : []
      const jd2 = results[2].status === 'fulfilled'
        ? normalize(results[2].value) : []

      const successful = resumes.filter(
        r => r.extraction_status === 'success'
      )

      const failed = resumes.filter(
        r => ['failed', 'empty_text', 'ocr_unavailable']
          .includes(r.extraction_status)
      )

      const uniqueCandidates = new Map()

      ;[...jd1, ...jd2].forEach(candidate => {
        const key = candidate.resume_id ?? candidate.candidate_identifier
        if (key != null) uniqueCandidates.set(String(key), candidate)
      })

      const bestScores = new Map()
      ;[...jd1, ...jd2].forEach(candidate => {
        const key = String(candidate.resume_id)
        const existing = bestScores.get(key)
        if (!existing || getScore(candidate) > getScore(existing)) {
          bestScores.set(key, candidate)
        }
      })

      setStats({
        total: resumes.length,
        successful: successful.length,
        failed: failed.length,
        pending: resumes.length - successful.length - failed.length,
        jd1,
        jd2,
        review: uniqueCandidates.size,
        uniqueRanked: [...bestScores.values()],
        recent: resumes.slice(0, 5),
        jd1Error: results[1].status === 'rejected',
        jd2Error: results[2].status === 'rejected',
      })
    } catch (err) {
      setError(err.message || 'Dashboard loading failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32 text-slate-500">
        <RefreshCw className="animate-spin mr-3" />
        Loading NoiceHire analytics...
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-xl">
        <p className="text-red-700 font-semibold">{error}</p>
        <button onClick={loadDashboard} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg">
          Retry
        </button>
      </div>
    )
  }

  const cards = [
    {
      title: 'Total Resumes',
      value: stats.total,
      description: 'All uploaded documents',
      icon: FileText,
      color: 'bg-gradient-to-br from-indigo-600 to-violet-700 text-white border-indigo-400',
      action: () => navigate('/candidates'),
    },
    {
      title: 'Successfully Extracted',
      value: stats.successful,
      description: 'Documents with extracted text',
      icon: CheckCircle2,
      color: 'bg-gradient-to-br from-emerald-500 to-green-700 text-white border-green-400',
    },
    {
      title: 'Extraction Issues',
      value: stats.failed,
      description: 'Failed, empty or OCR unavailable',
      icon: AlertCircle,
      color: 'bg-gradient-to-br from-rose-500 to-red-700 text-white border-red-400',
      action: () => navigate('/candidates'),
    },
    {
      title: 'JD1 · LCA Consultant',
      value: stats.jd1.length,
      description: 'Ranked candidates',
      icon: BriefcaseBusiness,
      color: 'bg-gradient-to-br from-purple-600 to-violet-800 text-white border-purple-400',
      action: () => navigate('/jobs/JD1'),
    },
    {
      title: 'JD2 · UI/UX Designer',
      value: stats.jd2.length,
      description: 'Ranked candidates',
      icon: BriefcaseBusiness,
      color: 'bg-gradient-to-br from-orange-500 to-amber-700 text-white border-orange-400',
      action: () => navigate('/jobs/JD2'),
    },
  ]

  return (
    <div className="space-y-6 pb-10">

      {/* Hero */}
      <section className="dashboard-hero relative overflow-hidden rounded-3xl min-h-72 text-white">
        <div className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: 'radial-gradient(circle at 80% 20%, #a78bfa 0, transparent 35%), radial-gradient(circle at 20% 100%, #4f46e5 0, transparent 40%)'
          }}
        />
        <div className="relative z-10 p-8 md:p-10 flex flex-col md:flex-row justify-between gap-6">
          <div>
            <span className="inline-flex items-center gap-2 bg-white/15 rounded-full px-4 py-2 text-sm">
              ✨ Welcome to NoiceHire
            </span>
            <h1 className="text-3xl md:text-4xl font-bold mt-5">
              AI-Powered Recruitment
            </h1>
            <p className="text-indigo-100 mt-3 max-w-lg leading-relaxed">
              Streamline resume screening, evaluate candidates and make
              data-driven hiring decisions.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col gap-3">
            <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl px-5 py-3">
              <p className="text-xs text-indigo-200">Candidates requiring review</p>
              <strong className="text-2xl">{stats.review}</strong>
            </div>
            <button
              onClick={loadDashboard}
              className="flex items-center justify-center gap-2 px-5 py-3 bg-white text-indigo-700 rounded-xl font-semibold hover:bg-indigo-50 transition"
            >
              <RefreshCw size={17} /> Refresh analytics
            </button>
          </div>
        </div>
      </section>

      {/* KPI cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
        {cards.map(card => (
          <StatCard key={card.title} {...card} onClick={card.action} />
        ))}
      </section>

      {/* Analytics */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <Panel title="Processing Overview" icon={BarChart3}>
          <DonutChart
            successful={stats.successful}
            failed={stats.failed}
            pending={stats.pending}
            total={stats.total}
          />
        </Panel>

        <Panel title="Candidate Score Distribution" icon={TrendingUp}>
          <DistributionChart candidates={stats.uniqueRanked} />
          <p className="text-xs text-slate-400 text-center mt-4">
            Best available score per unique ranked candidate
          </p>
        </Panel>

        <Panel title="Top Talent · Top 25%" icon={Target}>
          <TopTalent candidates={stats.uniqueRanked} />
        </Panel>
      </div>

      {/* Comparison and overlap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Panel title="JD1 vs JD2 · Score Comparison" icon={TrendingUp}>
          <Comparison jd1={stats.jd1} jd2={stats.jd2} />
        </Panel>

        <Panel title="Candidate Overlap · JD1 & JD2" icon={Users}>
          <CandidateOverlap jd1={stats.jd1} jd2={stats.jd2} />
        </Panel>
      </div>

      {/* Recent resumes */}
      <Panel title="Recent Resumes" icon={FileText}>
        <div className="flex justify-end mb-4">
          <button
            onClick={() => navigate('/candidates')}
            className="text-sm text-indigo-600 font-semibold flex items-center gap-1 hover:text-indigo-800"
          >
            View all <ArrowUpRight size={15} />
          </button>
        </div>

        {stats.recent.length === 0 ? (
          <p className="text-center py-8 text-slate-400">
            No resumes uploaded yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-500 bg-slate-50">
                  <th className="p-3">Candidate</th>
                  <th className="p-3">File name</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Uploaded</th>
                  <th className="p-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stats.recent.map(resume => (
                  <tr
                    key={resume.id}
                    onClick={() => navigate(`/candidates/${resume.id}`)}
                    className="cursor-pointer hover:bg-indigo-50/70 transition"
                  >
                    <td className="p-3 font-medium text-slate-800">
                      {resume.candidate_identifier || 'Unknown'}
                    </td>
                    <td className="p-3 text-slate-500 max-w-48 truncate">
                      {resume.original_filename}
                    </td>
                    <td className="p-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        resume.extraction_status === 'success'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-amber-100 text-amber-700'
                      }`}>
                        {resume.extraction_status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-500 whitespace-nowrap">
                      {resume.uploaded_at
                        ? new Date(resume.uploaded_at).toLocaleDateString()
                        : 'N/A'}
                    </td>
                    <td className="p-3 text-indigo-600">
                      <ChevronRight size={18} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <div className="flex items-center gap-2 text-xs text-slate-400">
        <ArrowUpRight size={14} />
        AI-generated rankings support human assessment; they do not make autonomous hiring decisions.
      </div>

      {(stats.jd1Error || stats.jd2Error) && (
        <p className="text-sm text-amber-700">
          Some ranking data could not be loaded. Check the relevant API.
        </p>
      )}
    </div>
  )
}
