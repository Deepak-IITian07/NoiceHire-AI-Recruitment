
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  BriefcaseBusiness,
  Users,
  Upload,
  Sparkles,
  X,
  Leaf
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Job Profiles', path: '/jobs', icon: BriefcaseBusiness },
  { name: 'Candidates', path: '/candidates', icon: Users },
  { name: 'Upload Resumes', path: '/upload', icon: Upload },
]

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {isOpen && (
        <button
          aria-label="Close navigation"
          onClick={onClose}
          className="sidebar-overlay"
        />
      )}

      <aside className={`app-sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Sparkles size={23} />
          </div>
          <div>
            <h1>NoiceHire</h1>
            <p>AI Recruitment Platform</p>
          </div>

          <button
            onClick={onClose}
            className="sidebar-close md:hidden"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-navigation">
          <p className="sidebar-label">WORKSPACE</p>

          {navigation.map(({ name, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
              }
            >
              <Icon size={19} />
              <span>{name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="flex items-center gap-2 mb-2">
            <Leaf size={15} className="text-emerald-400" />
            <span className="text-slate-300">Responsible AI Hiring</span>
          </div>
          <p>AI-powered recruitment</p>
          <p>Growth For Impact</p>
        </div>
      </aside>
    </>
  )
}
