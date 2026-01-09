import { useEffect, useState } from 'react'
import Button from '../components/Button'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Input from '../components/Input'
import Checkbox from '../components/Checkbox'
import { 
  getInstances, 
  createInstance, 
  updateInstance, 
  deleteInstance, 
  toggleInstanceStatus 
} from '../services/instancesService'
import { formatDate } from '../utils/dateUtils'

export default function Instances() {
  const [instances, setInstances] = useState([])
  const [error, setError] = useState(null)
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [editingInstance, setEditingInstance] = useState(null)
  
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
      const data = await getInstances()
      setInstances(data)
    } catch (err) {
      setError(err.message || 'Failed to load instances')
      console.error('Error fetching instances:', err)
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
    setFormData({
      name: '',
      base_url: '',
      api_key: '',
      redirect_url: '',
      is_active: true,
    })
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
      }
      
      if (formData.api_key.trim()) {
        submitData.api_key = formData.api_key.trim()
      }
      
      submitData.redirect_url = formData.redirect_url.trim()

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

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Gophish Instances</h1>
        <Button onClick={handleOpenCreateModal} fullWidth={false}>
          Add Instance
        </Button>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-500/10 p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-400">Error</h3>
              <div className="mt-2 text-sm text-red-300">{error}</div>
            </div>
          </div>
        </div>
      )}

      {instances.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          No instances found. Create your first instance to get started.
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-white/5">
              <thead className="bg-gray-800">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-white sm:pl-6">
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Base URL
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Redirect URL
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    API Key
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Status
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Created
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {instances.map((instance) => (
                  <tr key={instance.id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-white sm:pl-6">
                      {instance.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      <a 
                        href={instance.base_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-indigo-400 hover:text-indigo-300"
                      >
                        {instance.base_url}
                      </a>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {instance.redirect_url ? (
                        <a 
                          href={instance.redirect_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          {instance.redirect_url}
                        </a>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400 font-mono">
                      {instance.api_key}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      <span
                        className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                          instance.is_active
                            ? 'bg-green-500/10 text-green-400 ring-green-500/20'
                            : 'bg-gray-500/10 text-gray-400 ring-gray-500/20'
                        }`}
                      >
                        {instance.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {formatDate(instance.created_at)}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handleToggleStatus(instance)}
                          className={`${
                            instance.is_active
                              ? 'text-yellow-400 hover:text-yellow-300'
                              : 'text-green-400 hover:text-green-300'
                          }`}
                          title={instance.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {instance.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                        <button
                          onClick={() => handleOpenEditModal(instance)}
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteClick(instance)}
                          className="text-red-400 hover:text-red-300"
                        >
                          Delete
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

      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        title={editingInstance ? 'Edit Instance' : 'Create New Instance'}
        footer={
          <div className="flex gap-3">
            <Button
              type="button"
              onClick={handleCloseModal}
              className="bg-white/10 hover:bg-white/20"
              fullWidth={false}
            >
              Cancel
            </Button>
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
        <form id="instance-form" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-white">
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
                className="mt-1"
              />
            </div>

            <div>
              <label htmlFor="base_url" className="block text-sm font-medium text-white">
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
                className="mt-1"
              />
            </div>

            <div>
              <label htmlFor="api_key" className="block text-sm font-medium text-white">
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
                className="mt-1"
              />
            </div>

            <div>
              <label htmlFor="redirect_url" className="block text-sm font-medium text-white">
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
                className="mt-1"
              />
              <p className="mt-1 text-xs text-gray-400">
                URL to redirect users after they submit the form. This will be applied to all campaigns using this instance.
              </p>
            </div>

            <div className="flex items-center">
              <Checkbox
                id="is_active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
              />
              <label htmlFor="is_active" className="ml-3 text-sm text-white">
                Active
              </label>
            </div>
          </div>
        </form>
      </Modal>

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
            ? `Are you sure you want to delete "${editingInstance.name}"? This action cannot be undone.`
            : 'Are you sure you want to delete this instance?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
