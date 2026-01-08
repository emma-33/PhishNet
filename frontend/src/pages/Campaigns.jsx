import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import { getCampaigns } from '../services/campaignsService'
import { formatDate } from '../utils/dateUtils'

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

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])

  useEffect(() => {
    const fetchCampaigns = async () => {
      const campaigns = await getCampaigns()
      setCampaigns(campaigns)
    }
    fetchCampaigns()
  }, [])

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Campaigns</h1>
        <Link to="/campaigns/create">
          <Button fullWidth={false}>
            Create Campaign
          </Button>
        </Link>
      </div>
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/5">
            <thead className="bg-gray-800">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-white sm:pl-6">
                  Name
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                  Status
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                  Created
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                  Launched
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                  Stopped
                </th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-white sm:pl-6">
                    {campaign.name}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm">
                    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getStatusColor(campaign.status)}`}>
                      {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                    {formatDate(campaign.created_at)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                    {formatDate(campaign.launched_at)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                    {formatDate(campaign.stopped_at)}
                  </td>
                  <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button className="text-indigo-400 hover:text-indigo-300">
                      View<span className="sr-only">, {campaign.name}</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
