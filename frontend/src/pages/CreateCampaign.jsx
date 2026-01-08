import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import FormLayout, { FormSection, FormField, FormActions } from '../components/FormLayout'
import Input from '../components/Input'
import Textarea from '../components/Textarea'
import Select from '../components/Select'
import { createCampaign } from '../services/campaignsService'
import { getTemplates } from '../services/templatesService'

export default function CreateCampaign() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_id: '',
  })
  const [templates, setTemplates] = useState([])
  const [loadingTemplates, setLoadingTemplates] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      setLoadingTemplates(true)
      const data = await getTemplates()
      setTemplates(data)
    } catch (err) {
      setError(err.message || 'Failed to load templates')
      console.error('Error fetching templates:', err)
    } finally {
      setLoadingTemplates(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleTemplateChange = (templateId) => {
    setFormData(prev => ({
      ...prev,
      template_id: templateId
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!formData.template_id) {
      setError('Please select a template')
      return
    }

    try {
      const response = await createCampaign({
        name: formData.name,
        template_id: formData.template_id,
      })
      navigate('/campaigns')
    } catch (error) {
      setError(error.message)
    }
  }

  const handleCancel = () => {
    navigate('/campaigns')
  }

  return (
    <>
      <h1 className="text-3xl font-bold text-white mb-8">Create Campaign</h1>
      <div className="bg-gray-800 rounded-lg p-6">
      {error && (
          <div className="mb-6 rounded-md bg-red-500/10 p-4 border border-red-500/20">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
        <FormLayout onSubmit={handleSubmit} actions={<FormActions onCancel={handleCancel} submitLabel="Create Campaign" />}>
          <FormSection
            title="Campaign Details"
            description="Enter the basic information for your phishing awareness campaign."
          >
            <FormField label="Campaign Name" id="name" required colSpan="col-span-full">
              <Input
                id="name"
                name="name"
                type="text"
                required
                placeholder="e.g., Q4 Security Awareness Training"
                value={formData.name}
                onChange={handleChange}
              />
            </FormField>

            <FormField
              label="Description"
              id="description"
              description="Provide a brief description of what this campaign aims to achieve."
              colSpan="col-span-full"
            >
              <Textarea
                id="description"
                name="description"
                rows={4}
                placeholder="Describe the purpose and goals of this campaign..."
                value={formData.description}
                onChange={handleChange}
              />
            </FormField>

            <FormField 
              label="Template" 
              id="template_id" 
              required 
              colSpan="col-span-full"
              description="Select a template to use for this campaign."
            >
              {loadingTemplates ? (
                <div className="mt-2 rounded-md bg-white/5 px-3 py-2 text-sm text-gray-400 border border-white/10">
                  Loading templates...
                </div>
              ) : templates.length === 0 ? (
                <div className="mt-2 rounded-md bg-yellow-500/10 px-3 py-2 text-sm text-yellow-400 border border-yellow-500/20">
                  No templates available. Please create a template first.
                </div>
              ) : (
                <div className="mt-2">
                  <Select
                    options={templates.map(template => ({
                      value: template.id.toString(),
                      label: template.name
                    }))}
                    value={formData.template_id}
                    onChange={handleTemplateChange}
                    placeholder="Select a template"
                  />
                </div>
              )}
            </FormField>
          </FormSection>

          <FormSection
            title="Campaign Configuration"
            description="Configure the settings for your campaign. You can edit these later."
            borderBottom={false}
          >
            <FormField
              label="Status"
              id="status"
              description="New campaigns are created as drafts. You can launch them when ready."
              colSpan="sm:col-span-3"
            >
              <div className="mt-2">
                <div className="rounded-md bg-white/5 px-3 py-2 text-sm text-gray-400 border border-white/10">
                  Draft
                </div>
              </div>
            </FormField>
          </FormSection>
        </FormLayout>
      </div>
    </>
  )
}
