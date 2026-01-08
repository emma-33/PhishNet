import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import AppShell from './components/AppShell'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Team from './pages/Team'
import Campaigns from './pages/Campaigns'
import CreateCampaign from './pages/CreateCampaign'
import Instances from './pages/Instances'
import Templates from './pages/Templates'
import Tenants from './pages/Tenants'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <AppShell>
                <Dashboard />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/team" element={
            <ProtectedRoute>
              <AppShell>
                <Team />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/campaigns" element={
            <ProtectedRoute>
              <AppShell>
                <Campaigns />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/campaigns/create" element={
            <ProtectedRoute>
              <AppShell>
                <CreateCampaign />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/instances" element={
            <ProtectedRoute requireAdmin={true}>
              <AppShell>
                <Instances />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/templates" element={
            <ProtectedRoute requireAdmin={true}>
              <AppShell>
                <Templates />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/tenants" element={
            <ProtectedRoute requireAdmin={true}>
              <AppShell>
                <Tenants />
              </AppShell>
            </ProtectedRoute>
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <AppShell>
                <Dashboard />
              </AppShell>
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
