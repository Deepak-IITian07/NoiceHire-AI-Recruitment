
import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { authAPI } from '../services/api'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [loggingOut, setLoggingOut] = useState(false)
  const navigate = useNavigate()

  const handleLogout = async () => {
    setLoggingOut(true)

    try {
      await authAPI.logout()
    } finally {
      navigate('/login', { replace: true })
      setLoggingOut(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="dashboard-main">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <div className="flex justify-end items-center gap-3 px-6 py-2 bg-white border-b">
          <span className="text-sm text-gray-600">
            {localStorage.getItem('admin_username')}
          </span>

          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="text-sm font-medium text-red-600 hover:text-red-800 disabled:opacity-50"
          >
            {loggingOut ? 'Logging out...' : 'Logout'}
          </button>
        </div>

        <main className="dashboard-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
