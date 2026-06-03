import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Server, Power, PowerOff } from 'lucide-react'
import Button from '../../components/Button'
import Modal from '../../components/Modal'
import ConfirmDialog from '../../components/ConfirmDialog'
import Input from '../../components/Input'
import {
  getInstances,
  createInstance,
  updateInstance,
  deleteInstance,
  toggleInstanceStatus
} from '../../services/instancesService'
import { formatDate } from '../../utils/dateUtils'

export default function Instances() {
  const [instances, setInstances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [editingInstance, setEditingInstance] = useState(null)
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    base_url: '',
    api_key: '',
    redirect_url: '',
    is_active: true,
  })

  useEffect(() => {
    fetchInstances()
  }, [])

  const fetchInstances = async () => {
    try {
      setError(null)
      setLoading(true)
      const data = await getInstances()
      setInstances(data)
    } catch (err) {
      setError(err.message || 'Failed to load instances')
      console.error('Error fetching instances:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingInstance(null)
    setFormData({
      name: '',
      base_url: '',
      api_key: '',
      redirect_url: '',
      is_active: true,
    })
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (instance) => {
    setEditingInstance(instance)
    setFormData({
      name: instance.name,
      base_url: instance.base_url,
      api_key: '',
      redirect_url: instance.redirect_url || '',
      is_active: instance.is_active,
    })
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingInstance(null)
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      
      const submitData = {
        name: formData.name.trim(),
        base_url: formData.base_url.trim(),
        is_active: formData.is_active,
        redirect_url: formData.redirect_url.trim(),
      }
      
      if (formData.api_key.trim()) {
        submitData.api_key = formData.api_key.trim()
      } else if (!editingInstance) {
        setError('API key is required when creating a new instance')
        return
      }

      if (editingInstance) {
        await updateInstance(editingInstance.id, submitData)
      } else {
        await createInstance(submitData)
      }

      handleCloseModal()
      await fetchInstances()
    } catch (err) {
      const errorMessage = err.message || 'Failed to save instance'
      setError(errorMessage)
      console.error('Error saving instance:', err)
    }
  }

  const handleDeleteClick = (instance) => {
    setEditingInstance(instance)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteInstance(editingInstance.id)
      setIsDeleteDialogOpen(false)
      setEditingInstance(null)
      await fetchInstances()
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete instance'
      setError(errorMessage)
      console.error('Error deleting instance:', err)
      setIsDeleteDialogOpen(false)
      setEditingInstance(null)
    }
  }

  const handleToggleStatus = async (instance) => {
    try {
      setError(null)
      await toggleInstanceStatus(instance.id)
      await fetchInstances()
    } catch (err) {
      const errorMessage = err.message || 'Failed to toggle instance status'
      setError(errorMessage)
      console.error('Error toggling instance status:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading instances...</div>
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gophish Instances</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage Gophish server instances for your campaigns
          </p>
        </div>
        <Button onClick={handleOpenCreateModal} fullWidth={false}>
          <Plus className="w-5 h-5 mr-2" />
          Add Instance
        </Button>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {instances.length === 0 ? (
        <div className="text-center py-12">
          <Server className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No instances</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by adding your first Gophish instance.
          </p>
          <div className="mt-6">
            <Button onClick={handleOpenCreateModal} fullWidth={false}>
              <Plus className="w-5 h-5 mr-2" />
              Add Instance
            </Button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg overflow-hidden shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Base URL
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Redirect URL
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    API Key
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Status
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Created
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {instances.map((instance) => (
                  <tr key={instance.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                      {instance.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      <a 
                        href={instance.base_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-500"
                      >
                        {instance.base_url}
                      </a>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {instance.redirect_url ? (
                        <a 
                          href={instance.redirect_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-500"
                        >
                          {instance.redirect_url}
                        </a>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">
                      {instance.api_key}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      <span
                        className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                          instance.is_active
                            ? 'bg-green-50 text-green-700 ring-green-600/20'
                            : 'bg-gray-50 text-gray-600 ring-gray-500/10'
                        }`}
                      >
                        {instance.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {formatDate(instance.created_at)}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleToggleStatus(instance)}
                          className={`p-2 rounded-md transition-colors ${
                            instance.is_active
                              ? 'text-orange-600 hover:text-orange-700 hover:bg-orange-50'
                              : 'text-green-600 hover:text-green-700 hover:bg-green-50'
                          }`}
                          title={instance.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {instance.is_active ? (
                            <PowerOff className="h-5 w-5" />
                          ) : (
                            <Power className="h-5 w-5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleOpenEditModal(instance)}
                          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-md transition-colors"
                          title="Edit"
                        >
                          <Pencil className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(instance)}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded-md transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        title={editingInstance ? 'Edit Instance' : 'Create New Instance'}
        footer={
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleCloseModal}
              className="inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Cancel
            </button>
            <Button
              type="submit"
              form="instance-form"
              fullWidth={false}
            >
              {editingInstance ? 'Update' : 'Create'}
            </Button>
          </div>
        }
        size="md"
      >
        <form id="instance-form" onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Production Gophish"
            />
          </div>

          <div>
            <label htmlFor="base_url" className="block text-sm font-medium text-gray-700">
              Base URL
            </label>
            <Input
              id="base_url"
              name="base_url"
              type="url"
              required
              value={formData.base_url}
              onChange={handleInputChange}
              placeholder="https://gophish.example.com"
            />
            <p className="mt-1 text-xs text-gray-500">
              The URL of your Gophish server
            </p>
          </div>

          <div>
            <label htmlFor="api_key" className="block text-sm font-medium text-gray-700">
              API Key {editingInstance && <span className="text-gray-500">(leave empty to keep current)</span>}
            </label>
            <Input
              id="api_key"
              name="api_key"
              type="password"
              required={!editingInstance}
              value={formData.api_key}
              onChange={handleInputChange}
              placeholder="Enter API key"
            />
            <p className="mt-1 text-xs text-gray-500">
              Your Gophish API key for authentication
            </p>
          </div>

          <div>
            <label htmlFor="redirect_url" className="block text-sm font-medium text-gray-700">
              Redirect URL
            </label>
            <Input
              id="redirect_url"
              name="redirect_url"
              type="url"
              required
              value={formData.redirect_url}
              onChange={handleInputChange}
              placeholder="https://example.com/redirect"
            />
            <p className="mt-1 text-xs text-gray-500">
              URL to redirect users after they submit the form
            </p>
          </div>

          <div className="flex items-center">
            <input
              id="is_active"
              name="is_active"
              type="checkbox"
              checked={formData.is_active}
              onChange={handleInputChange}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="ml-3 text-sm text-gray-700">
              Active
            </label>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setEditingInstance(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Instance"
        message={
          editingInstance
            ? `Are you sure you want to delete "${editingInstance.name}"? This action cannot be undone and will fail if there are campaigns or templates using this instance.`
            : 'Are you sure you want to delete this instance?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
