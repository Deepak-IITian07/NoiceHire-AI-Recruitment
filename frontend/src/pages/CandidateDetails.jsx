
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft, Download, User, GraduationCap, Code2,
  BriefcaseBusiness, FolderKanban, Award, AlertTriangle,
  FileText, RefreshCw, Mail, Phone, MapPin, Calendar,Trash2,
  ShieldCheck, Clock, ExternalLink
} from 'lucide-react'
import { resumeAPI, rankingAPI } from '../services/api'

function formatDate(value) {
  if (!value) return 'Present'
  return value
}

function Verification({ status }) {
  const styles = {
    verified: 'bg-green-50 text-green-700',
    unverified: 'bg-slate-100 text-slate-600',
    needs_review: 'bg-amber-50 text-amber-700',
  }

  return (
    <span className={`text-xs px-2.5 py-1 rounded-full ${styles[status] || styles.unverified}`}>
      {status?.replace('_', ' ') || 'unverified'}
    </span>
  )
}

function Confidence({ value }) {
  if (value == null) return null

  const percentage = Math.round(value * 100)

  return (
    <div className="mt-3">
      <div className="flex justify-between text-xs text-slate-500 mb-1">
        <span>Extraction confidence</span>
        <span>{percentage}%</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-500 rounded-full"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function Evidence({ items }) {
  if (!items?.length) return null

  return (
    <details className="mt-3 border-t border-slate-100 pt-3">
      <summary className="text-xs text-indigo-600 font-medium cursor-pointer">
        View supporting evidence ({items.length})
      </summary>

      <div className="mt-3 space-y-2">
        {items.map((item, index) => (
          <div key={index} className="bg-slate-50 rounded-lg p-3">
            <p className="text-sm text-slate-700">{item.text}</p>
            {item.page != null && (
              <p className="text-xs text-slate-400 mt-2">
                Page {item.page}
              </p>
            )}
          </div>
        ))}
      </div>
    </details>
  )
}

function Section({ title, icon: Icon, children }) {
  return (
    <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <h2 className="font-semibold text-slate-900 flex items-center gap-3 mb-5">
        <span className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
          <Icon size={19} />
        </span>
        {title}
      </h2>
      {children}
    </section>
  )
}

function InfoItem({ label, value, icon: Icon }) {
  return (
    <div className="flex gap-3 min-w-0">
      {Icon && <Icon size={17} className="text-slate-400 mt-0.5 shrink-0" />}
      <div className="min-w-0">
        <p className="text-xs text-slate-400">{label}</p>
        <p className="text-sm font-medium text-slate-800 break-words mt-1">
          {value || 'Not provided'}
        </p>
      </div>
    </div>
  )
}

function ExtractedField({ field }) {
  if (!field) return null

  return (
    <div className="border border-slate-100 rounded-xl p-4">
      <p className="text-sm font-medium text-slate-500 mb-2">
        {field.value || 'Not provided'}
      </p>
      <Verification status={field.verification_status} />
      <Confidence value={field.confidence} />
      <Evidence items={field.evidence} />
    </div>
  )
}

function EmptyState({ children }) {
  return (
    <p className="text-sm text-slate-400 py-2">{children}</p>
  )
}

function EducationCard({ item }) {
  return (
    <div className="border border-slate-200 rounded-xl p-5">
      <div className="flex justify-between gap-3 flex-wrap">
        <div>
          <h3 className="font-semibold text-slate-900">
            {item.degree || 'Degree not specified'}
          </h3>
          <p className="text-sm text-indigo-600 mt-1">
            {item.institution || 'Institution not specified'}
          </p>
        </div>
        <Verification status={item.verification_status} />
      </div>

      <p className="text-sm text-slate-600 mt-3">
        {item.field_of_study || 'Field not specified'}
      </p>

      <div className="flex flex-wrap gap-4 text-xs text-slate-500 mt-4">
        <span>{formatDate(item.start_date)} – {formatDate(item.end_date)}</span>
        {item.grade && <span>Grade: {item.grade}</span>}
      </div>

      <Confidence value={item.confidence} />
      <Evidence items={item.evidence} />
    </div>
  )
}

function ExperienceCard({ item }) {
  return (
    <div className="border border-slate-200 rounded-xl p-5">
      <div className="flex justify-between gap-3 flex-wrap">
        <div>
          <h3 className="font-semibold text-slate-900">
            {item.position || 'Position not specified'}
          </h3>
          <p className="text-sm text-indigo-600 mt-1">
            {item.company || 'Company not specified'}
          </p>
        </div>
        <Verification status={item.verification_status} />
      </div>

      <p className="text-xs text-slate-500 mt-3">
        {item.start_date || 'N/A'} – {formatDate(item.end_date)}
        {item.employment_type && ` · ${item.employment_type}`}
      </p>

      {item.description && (
        <p className="text-sm text-slate-600 mt-4 leading-relaxed">
          {item.description}
        </p>
      )}

      <Confidence value={item.confidence} />
      <Evidence items={item.evidence} />
    </div>
  )
}

function ProjectCard({ item }) {
  return (
    <div className="border border-slate-200 rounded-xl p-5">
      <div className="flex justify-between gap-3">
        <h3 className="font-semibold text-slate-900">{item.name}</h3>
        <Verification status={item.verification_status} />
      </div>

      {item.description && (
        <p className="text-sm text-slate-600 mt-3 leading-relaxed">
          {item.description}
        </p>
      )}

      <div className="flex flex-wrap gap-2 mt-4">
        {(item.technologies || []).map((tech, index) => (
          <span key={index} className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs">
            {tech}
          </span>
        ))}
      </div>

      <Confidence value={item.confidence} />
      <Evidence items={item.evidence} />
    </div>
  )
}

function ScoreCard({ title, result }) {
  if (!result) {
    return (
      <div className="bg-white border rounded-xl p-5">
        <h3 className="font-semibold">{title}</h3>
        <EmptyState>No ranking available.</EmptyState>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex justify-between items-center gap-3">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <span className="text-2xl font-bold text-indigo-600">
          {result.score == null ? 'N/A' : Number(result.score).toFixed(2)}
        </span>
      </div>

      <p className="text-xs text-slate-500 mt-2">
        Evidence availability: {result.information_availability_coverage ?? 'N/A'}
        {result.information_availability_coverage != null ? '%' : ''}
      </p>

      <div className="mt-5 space-y-4">
        <div>
          <p className="text-sm font-semibold mb-3">Category scores</p>
          {result.category_scores &&
            Object.entries(result.category_scores).map(([key, value]) => (
              <div key={key} className="mb-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className="font-semibold">{String(value)}</span>
                </div>
              </div>
            ))}
        </div>

        <div>
          <p className="text-sm font-semibold mb-2">Explanation</p>
          <p className="text-sm text-slate-600">
            {typeof result.explanation === 'string'
              ? result.explanation
              : 'See assessment details below.'}
          </p>
        </div>

        <div>
          <p className="text-sm font-semibold mb-2">Missing information</p>
          {Array.isArray(result.missing_information)
            ? result.missing_information.map((item, i) => (
                <p key={i} className="text-sm text-amber-700">• {String(item)}</p>
              ))
            : <p className="text-sm text-slate-500">
                {String(result.missing_information || 'None reported')}
              </p>}
        </div>
      </div>
    </div>
  )
}

export default function CandidateDetails() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [resume, setResume] = useState(null)
  const [rankings, setRankings] = useState({ JD1: null, JD2: null })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    let active = true

    async function loadCandidate() {
      setLoading(true)
      setError('')

      try {
        const [resumeResponse, jd1Response, jd2Response] = await Promise.all([
          resumeAPI.getById(id),
          rankingAPI.getByJob('JD1'),
          rankingAPI.getByJob('JD2'),
        ])

        if (!active) return

        const findResult = (response) => {
          const data = response.data
          const list = Array.isArray(data) ? data : data.results ?? []
          return list.find(item => String(item.resume_id) === String(id)) ?? null
        }

        setResume(resumeResponse.data)
        setRankings({
          JD1: findResult(jd1Response),
          JD2: findResult(jd2Response),
        })
      } catch {
        if (active) setError('Unable to load candidate information.')
      } finally {
        if (active) setLoading(false)
      }
    }

    loadCandidate()
    return () => { active = false }
  }, [id])

  if (loading) {
    return (
      <div className="py-24 flex justify-center text-slate-500">
        <RefreshCw className="animate-spin mr-3" />
        Loading candidate profile...
      </div>
    )
  }

  if (error || !resume) {
    return (
      <div className="bg-red-50 text-red-700 rounded-xl p-6">
        {error || 'Candidate not found.'}
        <button onClick={() => navigate(-1)} className="underline ml-3">
          Go back
        </button>
      </div>
    )
  }

  const data = resume.candidate_data || {}
  const personal = data.personal_info || {}
  const candidateName = personal.name?.value || resume.candidate_identifier || 'Unknown Candidate'
  const extractionFailed = resume.extraction_status !== 'success'

  async function handleDelete() {
    if (!window.confirm(`Permanently delete ${candidateName}? This also removes their resume and ranking data.`)) return

    setDeleting(true)

    try {
      await resumeAPI.delete(id)
      navigate('/candidates', { replace: true })
    } catch {
      alert('Unable to delete candidate.')
      setDeleting(false)
    }
  }

  return (
    <div className="space-y-6 pb-10">

      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800"
      >
        <ArrowLeft size={17} /> Back
      </button>

      {/* Candidate header */}
      <div className="bg-white border rounded-2xl p-6 shadow-sm">
        <div className="flex flex-wrap justify-between items-center gap-5">
          <div className="flex gap-4 items-center">
            <div className="w-16 h-16 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
              <User size={30} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">{candidateName}</h1>
              <p className="text-sm text-slate-500 mt-1">{resume.original_filename}</p>
              <p className="text-xs text-slate-400 mt-2">
                Resume ID: {resume.id} · Uploaded: {resume.uploaded_at ? new Date(resume.uploaded_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            {resume.file_url && (
              <a
                href={resume.file_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
              >
                <Download size={17} /> View Original Resume
                <ExternalLink size={14} />
              </a>
            )}
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="flex items-center gap-2 px-4 py-3 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50"
            >
              <Trash2 size={17} />
              {deleting ? 'Deleting...' : 'Delete Candidate'}
            </button>
          </div>
        </div>
      </div>

      {extractionFailed && (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex gap-3 text-amber-800">
          <AlertTriangle size={20} className="shrink-0" />
          <div>
            <p className="font-semibold text-sm">Extraction warning: {resume.extraction_status}</p>
            <p className="text-sm mt-1">
              {resume.extraction_error || 'Some resume information may be unavailable.'}
            </p>
          </div>
        </div>
      )}

      {/* Personal information */}
      <Section title="Personal Information" icon={User}>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-5">
          {[
            ['Name', personal.name, User],
            ['Email', personal.email, Mail],
            ['Phone', personal.phone, Phone],
            ['Location', personal.location, MapPin],
          ].map(([label, field, Icon]) => (
            <div key={label}>
              <InfoItem label={label} value={field?.value} icon={Icon} />
              <div className="mt-3">
                <Verification status={field?.verification_status} />
              </div>
              <Confidence value={field?.confidence} />
              <Evidence items={field?.evidence} />
            </div>
          ))}
        </div>

        <div className="mt-6 pt-5 border-t">
          <InfoItem
            label="Total Experience"
            value={data.total_experience_years?.value != null
              ? `${data.total_experience_years.value} years`
              : null}
            icon={Clock}
          />
          <Confidence value={data.total_experience_years?.confidence} />
          <Evidence items={data.total_experience_years?.evidence} />
        </div>
      </Section>

      {/* Education */}
      <Section title="Education" icon={GraduationCap}>
        {data.education?.length ? (
          <div className="grid md:grid-cols-2 gap-4">
            {data.education.map((item, i) => <EducationCard key={i} item={item} />)}
          </div>
        ) : <EmptyState>No education information extracted.</EmptyState>}
      </Section>

      {/* Skills */}
      <Section title="Technical Skills" icon={Code2}>
        {data.skills?.length ? (
          <div className="space-y-5">
            {Object.entries(
              data.skills.reduce((groups, skill) => {
                const category = skill.category || 'Other'
                groups[category] ||= []
                groups[category].push(skill)
                return groups
              }, {})
            ).map(([category, skills]) => (
              <div key={category}>
                <h3 className="text-xs font-semibold text-slate-500 uppercase mb-3">
                  {category}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill, i) => (
                    <div key={i} className="group relative">
                      <span className="bg-indigo-50 text-indigo-700 border border-indigo-100 px-3 py-2 rounded-lg text-sm">
                        {skill.name}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <div className="border-t pt-3 space-y-3">
              {data.skills.map((skill, i) => (
                <div key={i} className="flex flex-wrap items-center gap-3">
                  <span className="text-sm font-medium">{skill.name}</span>
                  <Confidence value={skill.confidence} />
                  <Evidence items={skill.evidence} />
                </div>
              ))}
            </div>
          </div>
        ) : <EmptyState>No technical skills information extracted.</EmptyState>}
      </Section>

      {/* Experience */}
      <Section title="Work Experience" icon={BriefcaseBusiness}>
        {data.experience?.length ? (
          <div className="space-y-4">
            {data.experience.map((item, i) => <ExperienceCard key={i} item={item} />)}
          </div>
        ) : <EmptyState>No work experience information extracted.</EmptyState>}
      </Section>

      {/* Projects */}
      <Section title="Projects" icon={FolderKanban}>
        {data.projects?.length ? (
          <div className="grid md:grid-cols-2 gap-4">
            {data.projects.map((item, i) => <ProjectCard key={i} item={item} />)}
          </div>
        ) : <EmptyState>No project information extracted.</EmptyState>}
      </Section>

      {/* Certifications */}
      <Section title="Certifications" icon={Award}>
        {data.certifications?.length ? (
          <div className="grid md:grid-cols-2 gap-4">
            {data.certifications.map((item, i) => (
              <div key={i} className="border rounded-xl p-4">
                <h3 className="font-semibold">{item.name}</h3>
                <p className="text-sm text-indigo-600 mt-1">{item.issuer || 'Issuer not provided'}</p>
                <p className="text-xs text-slate-500 mt-2">{item.issue_date || 'Date not provided'}</p>
                <Verification status={item.verification_status} />
                <Confidence value={item.confidence} />
                <Evidence items={item.evidence} />
              </div>
            ))}
          </div>
        ) : <EmptyState>No certifications information extracted.</EmptyState>}
      </Section>

      {/* JD assessments */}
      <section>
        <h2 className="text-lg font-bold text-slate-900 mb-4">
          JD-specific Assessment
        </h2>
        <div className="grid xl:grid-cols-2 gap-5">
          <ScoreCard title="JD1 · LCA Consultant" result={rankings.JD1} />
          <ScoreCard title="JD2 · UI/UX Designer" result={rankings.JD2} />
        </div>
      </section>

      {/* Extraction details */}
      <Section title="Extraction Details" icon={FileText}>
        <div className="grid md:grid-cols-2 gap-5">
          <InfoItem label="Extraction Status" value={resume.extraction_status} />
          <InfoItem label="Page Count" value={resume.page_count ?? 'Not provided'} />
        </div>
        {resume.extraction_error && (
          <p className="text-sm text-amber-700 mt-4">{resume.extraction_error}</p>
        )}
      </Section>
    </div>
  )
}
