import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getCampaign, getCampaignSummary } from '../services/campaignsService'
import { formatDate } from '../utils/dateUtils'
import Button from '../components/Button'

function getStatusColor(status) {
  switch (status) {
    case 'running':
      return 'bg-green-500/10 text-green-400 ring-green-500/20'
    case 'draft':
      return 'bg-gray-500/10 text-gray-400 ring-gray-500/20'
    case 'stopped':
      return 'bg-yellow-500/10 text-yellow-400 ring-yellow-500/20'
    case 'archived':
      return 'bg-blue-500/10 text-blue-400 ring-blue-500/20'
    default:
      return 'bg-gray-500/10 text-gray-400 ring-gray-500/20'
  }
}

export default function ViewCampaign() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [campaign, setCampaign] = useState(null)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        setLoading(true)
        const data = await getCampaign(id)
        setCampaign(data)
      } catch (err) {
        setError(err.message || 'Failed to load campaign')
        console.error('Error fetching campaign:', err)
      } finally {
        setLoading(false)
      }
    }

    const fetchSummary = async () => {
      try {
        setLoadingSummary(true)
        const data = await getCampaignSummary(id)
        setSummary(data)
      } catch (err) {
        console.error('Error fetching campaign summary:', err)
        // Don't set error state for summary failures, just log it
      } finally {
        setLoadingSummary(false)
      }
    }

    if (id) {
      fetchCampaign()
      fetchSummary()
    }
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-400">Loading campaign...</div>
      </div>
    )
  }

  if (error || !campaign) {
    return (
      <>
        <div className="mb-8">
          <Link to="/campaigns" className="text-indigo-400 hover:text-indigo-300 text-sm">
            ← Back to Campaigns
          </Link>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-400 mb-2">Error</h2>
          <p className="text-gray-400">{error || 'Campaign not found'}</p>
        </div>
      </>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link to="/campaigns" className="text-indigo-400 hover:text-indigo-300 text-sm mb-2 inline-block">
            ← Back to Campaigns
          </Link>
          <h1 className="text-3xl font-bold text-white">{campaign.name}</h1>
        </div>
        <div className="flex gap-3">
          <Link to="/campaigns">
            <Button fullWidth={false}>
              Back
            </Button>
          </Link>
        </div>
      </div>

      <div className="space-y-6">
        {/* Campaign Overview */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Campaign Overview</h2>
          <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <dt className="text-sm font-medium text-gray-400">Status</dt>
              <dd className="mt-1">
                <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getStatusColor(campaign.status)}`}>
                  {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-400">Campaign ID</dt>
              <dd className="mt-1 text-sm text-white">{campaign.id}</dd>
            </div>
            {campaign.template_id && (
              <div>
                <dt className="text-sm font-medium text-gray-400">Template ID</dt>
                <dd className="mt-1 text-sm text-white">{campaign.template_id}</dd>
              </div>
            )}
          </dl>
        </div>

        {/* Timeline */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Timeline</h2>
          <dl className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div>
              <dt className="text-sm font-medium text-gray-400">Created</dt>
              <dd className="mt-1 text-sm text-white">
                {campaign.created_at ? formatDate(campaign.created_at) : 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-400">Launched</dt>
              <dd className="mt-1 text-sm text-white">
                {campaign.launched_at ? formatDate(campaign.launched_at) : 'Not launched'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-400">Stopped</dt>
              <dd className="mt-1 text-sm text-white">
                {campaign.stopped_at ? formatDate(campaign.stopped_at) : 'Not stopped'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Campaign Summary */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Campaign Summary</h2>
          {loadingSummary ? (
            <div className="text-gray-400">Loading summary...</div>
          ) : summary ? (
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {summary.total && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Total Recipients</dt>
                  <dd className="mt-1 text-2xl font-semibold text-white">{summary.total}</dd>
                </div>
              )}
              {typeof summary.sent !== 'undefined' && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Emails Sent</dt>
                  <dd className="mt-1 text-2xl font-semibold text-white">{summary.sent}</dd>
                </div>
              )}
              {typeof summary.opened !== 'undefined' && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Emails Opened</dt>
                  <dd className="mt-1 text-2xl font-semibold text-green-400">{summary.opened}</dd>
                  {summary.total > 0 && (
                    <dd className="mt-1 text-xs text-gray-400">
                      {((summary.opened / summary.total) * 100).toFixed(1)}%
                    </dd>
                  )}
                </div>
              )}
              {typeof summary.clicked !== 'undefined' && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Links Clicked</dt>
                  <dd className="mt-1 text-2xl font-semibold text-yellow-400">{summary.clicked}</dd>
                  {summary.total > 0 && (
                    <dd className="mt-1 text-xs text-gray-400">
                      {((summary.clicked / summary.total) * 100).toFixed(1)}%
                    </dd>
                  )}
                </div>
              )}
              {typeof summary.submitted_data !== 'undefined' && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Submitted Data</dt>
                  <dd className="mt-1 text-2xl font-semibold text-red-400">{summary.submitted_data}</dd>
                  {summary.total > 0 && (
                    <dd className="mt-1 text-xs text-gray-400">
                      {((summary.submitted_data / summary.total) * 100).toFixed(1)}%
                    </dd>
                  )}
                </div>
              )}
              {typeof summary.email_reported !== 'undefined' && (
                <div>
                  <dt className="text-sm font-medium text-gray-400">Emails Reported</dt>
                  <dd className="mt-1 text-2xl font-semibold text-orange-400">{summary.email_reported}</dd>
                </div>
              )}
            </dl>
          ) : (
            <div className="text-gray-400">No summary data available</div>
          )}
        </div>

        {/* Additional Metadata */}
        {campaign.meta && Object.keys(campaign.meta).length > 0 && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Additional Information</h2>
            <div className="bg-gray-900/50 rounded-md p-4">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                {JSON.stringify(campaign.meta, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
