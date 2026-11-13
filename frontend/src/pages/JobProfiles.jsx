
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BriefcaseBusiness, ArrowRight, RefreshCw } from 'lucide-react'
import { jobAPI } from '../services/api'

export default function JobProfiles() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    jobAPI.getAll()
      .then(({ data }) => {
        setJobs(Array.isArray(data) ? data : data.results ?? [])
      })
      .catch(() => setError('Unable to load job profiles.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-slate-500">Loading job profiles...</p>

  if (error) return (
    <div className="text-red-600">
      {error}
      <button onClick={() => window.location.reload()} className="ml-3 underline">
        Retry
      </button>
    </div>
  )

  return (
    <div className="space-y-7">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Job Profiles</h1>
        <p className="text-slate-500 text-sm mt-1">
          Explore job openings and their ranked candidates.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {jobs.map((job) => {
          const isLCA = job.job_id === 'JD1'

          return (
            <div key={job.id} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <div className="flex justify-between items-start">
                <div className={`p-3 rounded-xl ${isLCA ? 'bg-purple-50 text-purple-600' : 'bg-orange-50 text-orange-600'}`}>
                  <BriefcaseBusiness size={25} />
                </div>
                <span className="text-xs font-semibold bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
                  {job.job_id}
                </span>
              </div>

              <h2 className="text-xl font-bold text-slate-900 mt-5">
                {job.title}
              </h2>

              <p className="text-sm text-slate-500 mt-2 line-clamp-3">
                {job.role_summary || job.original_description}
              </p>

              <div className="mt-5 pt-4 border-t border-slate-100 flex justify-between items-center">
                <span className="text-xs text-slate-500">
                  {isLCA ? 'Experience: 2–3 years stated in JD' : 'Entry-level internship'}
                </span>

                <button
                  onClick={() => navigate(`/jobs/${job.job_id}`)}
                  className="flex items-center gap-2 text-sm font-semibold text-indigo-600 hover:text-indigo-800"
                >
                  View Candidates <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {jobs.length === 0 && (
        <p className="text-slate-500">No job profiles found.</p>
      )}
    </div>
  )
}
