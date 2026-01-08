import Topbar from './Topbar'

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-gray-900">
      <Topbar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  )
}
