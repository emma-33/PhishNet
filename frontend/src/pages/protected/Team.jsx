import { useEffect, useState } from 'react'
import { 
  Users, 
  UserCheck, 
  Shield, 
  UserPlus, 
  Search, 
  Mail, 
  MoreVertical,
  Calendar,
  Copy,
  Check
} from 'lucide-react'
import { getTeamMembers } from '../../services/teamService'
import { createInvitation } from '../../services/invitationsService'
import { useUser } from '../../contexts/UserContext'
import { formatDateShort } from '../../utils/dateUtils'
import { generateAvatarUrl } from '../../utils/avatarUtils'

function getRoleColor(role) {
  switch (role) {
    case 'Operator':
      return 'bg-purple-100 text-purple-800'
    case 'Admin':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getStatusColor(isActive) {
  return isActive 
    ? 'bg-green-100 text-green-800'
    : 'bg-gray-100 text-gray-800'
}

export default function Team() {
  const { user } = useUser()
  const [teamMembers, setTeamMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const [invitationCode, setInvitationCode] = useState(null)
  const [inviteLoading, setInviteLoading] = useState(false)
  const [inviteError, setInviteError] = useState(null)
  const [copiedCode, setCopiedCode] = useState(false)

  useEffect(() => {
    fetchTeamMembers()
  }, [])

  const fetchTeamMembers = async () => {
    try {
      setLoading(true)
      const members = await getTeamMembers()
      setTeamMembers(members || [])
    } catch (error) {
      console.error('Error fetching team members:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInviteMember = async () => {
    if (!user?.tenant_id) {
      setInviteError('Unable to determine tenant. Please try again.')
      return
    }

    try {
      setInviteError(null)
      setInviteLoading(true)
      const response = await createInvitation(user.tenant_id)
      setInvitationCode(response.invitation.invitation_code)
      setIsInviteModalOpen(true)
    } catch (err) {
      const errorMessage = err.message || 'Failed to create invitation'
      setInviteError(errorMessage)
      setIsInviteModalOpen(true)
      console.error('Error creating invitation:', err)
    } finally {
      setInviteLoading(false)
    }
  }

  const handleCopyCode = () => {
    if (invitationCode) {
      navigator.clipboard.writeText(invitationCode)
      setCopiedCode(true)
      setTimeout(() => setCopiedCode(false), 2000)
    }
  }

  const handleCloseModal = () => {
    setIsInviteModalOpen(false)
    setInvitationCode(null)
    setInviteError(null)
    setCopiedCode(false)
  }

  // Check if current user is operator
  const isOperator = teamMembers.find(m => m.id === user?.id)?.is_operator || false

  // Calculate statistics
  const totalMembers = teamMembers.length
  const activeMembers = teamMembers.filter(m => m.is_active).length
  const operators = teamMembers.filter(m => m.is_operator).length

  // Filter team members by search query
  const filteredMembers = teamMembers.filter(member => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    const fullName = `${member.first_name} ${member.last_name}`.toLowerCase()
    return fullName.includes(query) ||
           member.email.toLowerCase().includes(query) ||
           member.role.toLowerCase().includes(query)
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading team members...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Team</h1>
        <p className="text-gray-600">Manage and monitor your team members</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Members</p>
              <p className="text-3xl font-bold text-gray-900">{totalMembers}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Members</p>
              <p className="text-3xl font-bold text-gray-900">{activeMembers}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <UserCheck className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Operators</p>
              <p className="text-3xl font-bold text-gray-900">{operators}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Shield className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Invite Button */}
      <div className="flex items-center justify-between mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search team members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        {isOperator && (
          <button
            onClick={handleInviteMember}
            disabled={inviteLoading}
            className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <UserPlus className="w-5 h-5" />
            {inviteLoading ? 'Creating...' : 'Invite Member'}
          </button>
        )}
      </div>

      {/* Team Members Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Joined Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMembers.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    {searchQuery ? 'No team members found matching your search.' : 'No team members yet.'}
                  </td>
                </tr>
              ) : (
                filteredMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <img
                          src={generateAvatarUrl(member.first_name, member.last_name, member.email)}
                          alt={`${member.first_name} ${member.last_name}`}
                          className="w-10 h-10 rounded-full mr-3"
                        />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {member.first_name} {member.last_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        <Mail className="w-4 h-4 text-gray-400 mr-2" />
                        {member.email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(member.role)}`}>
                        {member.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(member.is_active)}`}>
                        {member.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1 text-sm text-gray-900">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        {formatDateShort(member.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        className="text-gray-600 hover:text-gray-900"
                        title="More options"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invitation Modal */}
      {isInviteModalOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={handleCloseModal}
          />
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Invitation Code</h2>
                  <button
                    onClick={handleCloseModal}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {inviteError ? (
                  <div className="text-red-600 bg-red-50 border border-red-200 rounded-md p-4">
                    {inviteError}
                  </div>
                ) : invitationCode ? (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Share this invitation code with the person you want to invite. They can use it during registration.
                    </p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 rounded-md bg-gray-50 px-4 py-3 font-mono text-lg font-semibold text-gray-900 border border-gray-300">
                        {invitationCode}
                      </div>
                      <button
                        onClick={handleCopyCode}
                        className="flex items-center gap-2 px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium transition-colors"
                      >
                        {copiedCode ? (
                          <>
                            <Check className="w-5 h-5" />
                            Copied
                          </>
                        ) : (
                          <>
                            <Copy className="w-5 h-5" />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500">
                      This code can be used once. Make sure to share it securely.
                    </p>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
