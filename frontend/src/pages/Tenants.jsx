import { useEffect, useState } from 'react'
import Button from '../components/Button'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Input from '../components/Input'
import { 
  getTenants, 
  createTenant, 
  updateTenant, 
  deleteTenant
} from '../services/tenantsService'
import { formatDate } from '../utils/dateUtils'

export default function Tenants() {
  const [tenants, setTenants] = useState([])
  const [error, setError] = useState(null)
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [editingTenant, setEditingTenant] = useState(null)
  
  const [formData, setFormData] = useState({
    name: '',
  })

  useEffect(() => {
    fetchTenants()
  }, [])

  const fetchTenants = async () => {
    try {
      setError(null)
      const data = await getTenants()
      setTenants(data)
    } catch (err) {
      setError(err.message || 'Failed to load tenants')
      console.error('Error fetching tenants:', err)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingTenant(null)
    setFormData({
      name: '',
    })
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (tenant) => {
    setEditingTenant(tenant)
    setFormData({
      name: tenant.name,
    })
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTenant(null)
    setFormData({
      name: '',
    })
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      
      const submitData = {
        name: formData.name.trim(),
      }

      if (editingTenant) {
        await updateTenant(editingTenant.id, submitData)
      } else {
        await createTenant(submitData)
      }

      handleCloseModal()
      await fetchTenants()
    } catch (err) {
      const errorMessage = err.message || 'Failed to save tenant'
      setError(errorMessage)
      console.error('Error saving tenant:', err)
    }
  }

  const handleDeleteClick = (tenant) => {
    setEditingTenant(tenant)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteTenant(editingTenant.id)
      setIsDeleteDialogOpen(false)
      setEditingTenant(null)
      await fetchTenants()
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete tenant'
      setError(errorMessage)
      console.error('Error deleting tenant:', err)
    }
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Tenants</h1>
        <Button onClick={handleOpenCreateModal} fullWidth={false}>
          Create Tenant
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

      {tenants.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          No tenants found. Create your first tenant to get started.
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-white/5">
              <thead className="bg-gray-800">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-white sm:pl-6">
                    ID
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-white">
                    Gophish Group ID
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
                {tenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-white sm:pl-6">
                      {tenant.id}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm font-medium text-white">
                      {tenant.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {tenant.gophish_group_id || 'N/A'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {formatDate(tenant.created_at)}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handleOpenEditModal(tenant)}
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteClick(tenant)}
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
        title={editingTenant ? 'Edit Tenant' : 'Create New Tenant'}
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
              form="tenant-form"
              fullWidth={false}
            >
              {editingTenant ? 'Update' : 'Create'}
            </Button>
          </div>
        }
        size="md"
      >
        <form id="tenant-form" onSubmit={handleSubmit}>
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
                placeholder="e.g., Acme Corporation"
                className="mt-1"
              />
            </div>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setEditingTenant(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Tenant"
        message={
          editingTenant
            ? `Are you sure you want to delete "${editingTenant.name}"? This action cannot be undone and will delete all associated users and data.`
            : 'Are you sure you want to delete this tenant?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
