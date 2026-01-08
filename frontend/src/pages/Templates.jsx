import { useEffect, useState } from 'react'
import Button from '../components/Button'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Input from '../components/Input'
import Textarea from '../components/Textarea'
import Checkbox from '../components/Checkbox'
import { 
  getTemplates, 
  getTemplate,
  createTemplate, 
  updateTemplate, 
  deleteTemplate 
} from '../services/templatesService'
import { formatDate } from '../utils/dateUtils'

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [error, setError] = useState(null)
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  
  const [formData, setFormData] = useState({
    name: '',
    email_template_data: {
      subject: '',
      html: '',
    },
    landing_page_data: {
      html: '',
      capture_credentials: false,
      capture_passwords: false,
      redirect_url: '',
    },
  })

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      setError(null)
      const data = await getTemplates()
      setTemplates(data)
    } catch (err) {
      setError(err.message || 'Failed to load templates')
      console.error('Error fetching templates:', err)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingTemplate(null)
    setFormData({
      name: '',
      email_template_data: {
        subject: '',
        html: '',
      },
      landing_page_data: {
        html: '',
        capture_credentials: false,
        capture_passwords: false,
        redirect_url: '',
      },
    })
    setIsModalOpen(true)
  }

  const handleOpenEditModal = async (template) => {
    try {
      setError(null)
      const fullTemplate = await getTemplate(template.id)
      
      setEditingTemplate(template)
      setFormData({
        name: fullTemplate.name,
        email_template_data: {
          subject: fullTemplate.email_template.subject || '',
          html: fullTemplate.email_template.html,
        },
        landing_page_data: {
          html: fullTemplate.landing_page.html,
          capture_credentials: fullTemplate.landing_page.capture_credentials || false,
          capture_passwords: fullTemplate.landing_page.capture_passwords || false,
          redirect_url: fullTemplate.landing_page.redirect_url || '',
        },
      })
      setIsModalOpen(true)
    } catch (err) {
      setError(err.message || 'Failed to load template details')
      console.error('Error fetching template details:', err)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTemplate(null)
    setFormData({
      name: '',
      email_template_data: {
        subject: '',
        html: '',
      },
      landing_page_data: {
        html: '',
        capture_credentials: false,
        capture_passwords: false,
        redirect_url: '',
      },
    })
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    const [section, field] = name.includes('.') ? name.split('.') : [null, name]
    
    if (section === 'email_template_data' || section === 'landing_page_data') {
      setFormData(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: type === 'checkbox' ? checked : value,
        },
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      
      if (!formData.email_template_data.subject || !formData.email_template_data.subject.trim()) {
        setError('Email template subject is required')
        return
      }
      
      if (!formData.email_template_data.html || !formData.email_template_data.html.trim()) {
        setError('Email template HTML is required')
        return
      }
      
      const submitData = {
        name: formData.name.trim(),
        email_template_data: {
          subject: formData.email_template_data.subject.trim(),
          html: formData.email_template_data.html.trim(),
        },
        landing_page_data: {
          html: formData.landing_page_data.html.trim(),
          capture_credentials: formData.landing_page_data.capture_credentials,
          capture_passwords: formData.landing_page_data.capture_passwords,
          redirect_url: formData.landing_page_data.redirect_url.trim(),
        },
      }

      if (editingTemplate) {
        await updateTemplate(editingTemplate.id, submitData)
      } else {
        await createTemplate(submitData)
      }

      handleCloseModal()
      await fetchTemplates()
    } catch (err) {
      const errorMessage = err.message || 'Failed to save template'
      setError(errorMessage)
      console.error('Error saving template:', err)
    }
  }

  const handleDeleteClick = (template) => {
    setEditingTemplate(template)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteTemplate(editingTemplate.id)
      setIsDeleteDialogOpen(false)
      setEditingTemplate(null)
      await fetchTemplates()
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete template'
      setError(errorMessage)
      console.error('Error deleting template:', err)
    }
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Templates</h1>
        <Button onClick={handleOpenCreateModal} fullWidth={false}>
          Create Template
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

      {templates.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          No templates found. Create your first template to get started.
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
                    Created
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {templates.map((template) => (
                  <tr key={template.id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-white sm:pl-6">
                      {template.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {template.gophish_email_template_id}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {template.gophish_landing_page_id}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                      {formatDate(template.created_at)}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handleOpenEditModal(template)}
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteClick(template)}
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
        title={editingTemplate ? 'Edit Template' : 'Create New Template'}
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
              form="template-form"
              fullWidth={false}
            >
              {editingTemplate ? 'Update' : 'Create'}
            </Button>
          </div>
        }
        size="xl"
      >
        <form id="template-form" onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-white">
                Template Name
              </label>
              <Input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Phishing Email Template"
                className="mt-1"
              />
            </div>

            <div className="border-t border-white/10 pt-6">
              <h3 className="text-lg font-semibold text-white mb-4">Email Template</h3>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="email_template_data.subject" className="block text-sm font-medium text-white">
                    Subject <span className="text-red-400">*</span>
                  </label>
                  <Input
                    id="email_template_data.subject"
                    name="email_template_data.subject"
                    type="text"
                    required
                    value={formData.email_template_data.subject}
                    onChange={handleInputChange}
                    placeholder="e.g., Important: Action Required"
                    className="mt-1"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    Use {'{{.FirstName}}'} or {'{{.LastName}}'} for personalization
                  </p>
                </div>

                <div>
                  <label htmlFor="email_template_data.html" className="block text-sm font-medium text-white">
                    HTML Content <span className="text-red-400">*</span>
                  </label>
                  <Textarea
                    id="email_template_data.html"
                    name="email_template_data.html"
                    rows={8}
                    required
                    value={formData.email_template_data.html}
                    onChange={handleInputChange}
                    placeholder="<html><body>Click <a href='{{.URL}}'>here</a></body></html>"
                    className="mt-1 font-mono text-sm"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    Use {'{{.URL}}'} for the phishing link placeholder
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t border-white/10 pt-6">
              <h3 className="text-lg font-semibold text-white mb-4">Landing Page</h3>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="landing_page_data.html" className="block text-sm font-medium text-white">
                    HTML Content <span className="text-red-400">*</span>
                  </label>
                  <Textarea
                    id="landing_page_data.html"
                    name="landing_page_data.html"
                    rows={10}
                    required
                    value={formData.landing_page_data.html}
                    onChange={handleInputChange}
                    placeholder="<html><body><h1>Welcome</h1><form>...</form></body></html>"
                    className="mt-1 font-mono text-sm"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <Checkbox
                      id="landing_page_data.capture_credentials"
                      name="landing_page_data.capture_credentials"
                      checked={formData.landing_page_data.capture_credentials}
                      onChange={handleInputChange}
                    />
                    <label htmlFor="landing_page_data.capture_credentials" className="ml-3 text-sm text-white">
                      Capture Credentials
                    </label>
                  </div>

                  <div className="flex items-center">
                    <Checkbox
                      id="landing_page_data.capture_passwords"
                      name="landing_page_data.capture_passwords"
                      checked={formData.landing_page_data.capture_passwords}
                      onChange={handleInputChange}
                    />
                    <label htmlFor="landing_page_data.capture_passwords" className="ml-3 text-sm text-white">
                      Capture Passwords
                    </label>
                  </div>
                </div>

                <div>
                  <label htmlFor="landing_page_data.redirect_url" className="block text-sm font-medium text-white">
                    Redirect URL (Optional)
                  </label>
                  <Input
                    id="landing_page_data.redirect_url"
                    name="landing_page_data.redirect_url"
                    type="url"
                    value={formData.landing_page_data.redirect_url}
                    onChange={handleInputChange}
                    placeholder="https://example.com"
                    className="mt-1"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    URL to redirect users after they submit the form
                  </p>
                </div>
              </div>
            </div>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setEditingTemplate(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Template"
        message={
          editingTemplate
            ? `Are you sure you want to delete "${editingTemplate.name}"? This will also delete the associated email template and landing page in Gophish. This action cannot be undone.`
            : 'Are you sure you want to delete this template?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
