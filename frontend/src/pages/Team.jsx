import { useEffect, useState } from 'react'
import StackedList from '../components/StackedList'
import Button from '../components/Button'
import Modal from '../components/Modal'
import { getTeamMembers } from '../services/teamService'
import { createInvitation } from '../services/invitationsService'
import { useUser } from '../contexts/UserContext'

export default function Team() {
  const { user } = useUser()
  const [teamMembers, setTeamMembers] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const [invitationCode, setInvitationCode] = useState(null)
  const [inviteLoading, setInviteLoading] = useState(false)
  const [inviteError, setInviteError] = useState(null)
  
  const isOperator = teamMembers.find(m => m.id === user?.id)?.is_operator || false

  useEffect(() => {
    fetchTeamMembers()
  }, [])

  const fetchTeamMembers = async () => {
    try {
      setError(null)
      setLoading(true)
      const members = await getTeamMembers()
      setTeamMembers(members)
    } catch (err) {
      setError(err.message || 'Failed to load team members')
      console.error('Error fetching team members:', err)
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
      const errorMessage = err.response?.data?.message || err.message || 'Failed to create invitation'
      setInviteError(errorMessage)
      if (errorMessage.includes('operator')) {
        setIsInviteModalOpen(true)
      }
      console.error('Error creating invitation:', err)
    } finally {
      setInviteLoading(false)
    }
  }

  const handleCopyCode = () => {
    if (invitationCode) {
      navigator.clipboard.writeText(invitationCode)
    }
  }

  const handleCloseModal = () => {
    setIsInviteModalOpen(false)
    setInvitationCode(null)
    setInviteError(null)
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Team</h1>
        {isOperator && (
          <Button fullWidth={false} onClick={handleInviteMember} disabled={inviteLoading}>
            {inviteLoading ? 'Creating...' : 'Invite a member'}
          </Button>
        )}
      </div>
      <div className="bg-gray-800 rounded-lg p-6">
        {loading && (
          <div className="text-center text-gray-400 py-8">Loading team members...</div>
        )}
        {error && (
          <div className="text-center text-red-400 py-8">{error}</div>
        )}
        {!loading && !error && (
          <>
            {teamMembers.length === 0 ? (
              <div className="text-center text-gray-400 py-8">No team members found</div>
            ) : (
              <StackedList items={teamMembers} />
            )}
          </>
        )}
      </div>

      <Modal
        open={isInviteModalOpen}
        onClose={handleCloseModal}
        title="Invitation Code"
        size="md"
      >
        {inviteError ? (
          <div className="text-red-400">{inviteError}</div>
        ) : invitationCode ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              Share this invitation code with the person you want to invite. They can use it during registration.
            </p>
            <div className="flex items-center gap-2">
              <div className="flex-1 rounded-md bg-gray-900 px-4 py-3 font-mono text-lg font-semibold text-white border border-white/10">
                {invitationCode}
              </div>
              <Button onClick={handleCopyCode} fullWidth={false}>
                Copy
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              This code can be used once. Make sure to share it securely.
            </p>
          </div>
        ) : null}
      </Modal>
    </>
  )
}
