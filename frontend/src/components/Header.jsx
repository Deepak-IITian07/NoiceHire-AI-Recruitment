
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bell, Search, Menu, User, Settings,
  LogOut, X, Info
} from 'lucide-react'

export default function Header({ onMenuClick }) {
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  function handleSearch(event) {
    event.preventDefault()
    const query = search.trim()
    if (query) {
      navigate(`/candidates?search=${encodeURIComponent(query)}`)
    }
  }

  return (
    <header className="app-header">
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onMenuClick}
          className="mobile-menu-button"
          aria-label="Open navigation"
        >
          <Menu size={22} />
        </button>

        <form onSubmit={handleSearch} className="header-search">
          <Search size={18} className="text-slate-400 shrink-0" />
          <input
            type="search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search candidates..."
          />
        </form>
      </div>

      <div className="flex items-center gap-3 sm:gap-5">
        <div className="relative">
          <button
            onClick={() => {
              setNotificationsOpen(!notificationsOpen)
              setProfileOpen(false)
            }}
            className="header-icon-button"
            aria-label="Notifications"
          >
            <Bell size={20} />
            <span className="notification-dot" />
          </button>

          {notificationsOpen && (
            <div className="header-dropdown notification-dropdown">
              <div className="flex justify-between items-center border-b p-4">
                <h3 className="font-semibold text-slate-800">Notifications</h3>
                <button onClick={() => setNotificationsOpen(false)}>
                  <X size={17} />
                </button>
              </div>

              <div className="p-5 text-center">
                <div className="w-11 h-11 mx-auto rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <Info size={21} />
                </div>
                <p className="font-medium text-sm mt-3">Notification center</p>
                <p className="text-xs text-slate-500 mt-1">
                  No live notifications are available yet.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => {
              setProfileOpen(!profileOpen)
              setNotificationsOpen(false)
            }}
            className="flex items-center gap-2 sm:gap-3 text-left"
          >
            <div className="hr-avatar">HR</div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-slate-800">HR Admin</p>
              <p className="text-xs text-slate-500">Recruitment Team</p>
            </div>
          </button>

          {profileOpen && (
            <div className="header-dropdown profile-dropdown">
              <div className="p-4 border-b">
                <p className="font-semibold text-sm text-slate-800">HR Admin</p>
                <p className="text-xs text-slate-500 mt-1">Recruitment Team</p>
              </div>

              <button
                onClick={() => setProfileOpen(false)}
                className="dropdown-action"
              >
                <User size={17} /> Profile
              </button>

              <button
                onClick={() => setProfileOpen(false)}
                className="dropdown-action"
              >
                <Settings size={17} /> Settings
              </button>

              <button
                onClick={() => setProfileOpen(false)}
                className="dropdown-action text-slate-400"
              >
                <LogOut size={17} /> Sign out (not configured)
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
