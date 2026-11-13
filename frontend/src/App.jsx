
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'

import DashboardLayout from './layouts/DashboardLayout'
import Dashboard from './pages/Dashboard'
import JobRankings from './pages/JobRankings'
import JobProfiles from './pages/JobProfiles'
import Candidates from './pages/Candidates'
import ResumeUpload from './pages/ResumeUpload'
import CandidateDetails from './pages/CandidateDetails'
import Login from './pages/Login'

function ProtectedRoute() {
  return localStorage.getItem('admin_token')
    ? <Outlet />
    : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<JobProfiles />} />
            <Route path="/jobs/:jobId" element={<JobRankings />} />
            <Route path="/candidates" element={<Candidates />} />
            <Route path="/candidates/:id" element={<CandidateDetails />} />
            <Route path="/upload" element={<ResumeUpload />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
