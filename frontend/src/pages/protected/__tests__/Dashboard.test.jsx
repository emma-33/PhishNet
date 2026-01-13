import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../Dashboard'
import * as UserContext from '../../../contexts/UserContext'
import * as campaignsService from '../../../services/campaignsService'
import * as templatesService from '../../../services/templatesService'
import * as instancesService from '../../../services/instancesService'
import * as tenantsService from '../../../services/tenantsService'

// Mock all services
vi.mock('../../../contexts/UserContext')
vi.mock('../../../services/campaignsService')
vi.mock('../../../services/templatesService')
vi.mock('../../../services/instancesService')
vi.mock('../../../services/tenantsService')

// Mock the date utils
vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

const mockCampaigns = [
  {
    id: 1,
    name: 'Campaign 1',
    status: 'running',
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Campaign 2',
    status: 'completed',
    created_at: '2024-01-20T14:30:00Z'
  }
]

const mockTemplates = [
  { id: 1, name: 'Template 1' },
  { id: 2, name: 'Template 2' }
]

const mockInstances = [
  { id: 1, name: 'Instance 1', is_active: true }
]

const mockTenants = [
  { id: 1, name: 'Tenant 1' }
]

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(campaignsService, 'getCampaigns').mockResolvedValue(mockCampaigns)
    vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
    vi.spyOn(instancesService, 'getInstances').mockResolvedValue(mockInstances)
    vi.spyOn(tenantsService, 'getTenants').mockResolvedValue(mockTenants)
  })

  describe('Regular User View', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John', email: 'john@example.com' },
        isAdmin: () => false
      })
    })

    it('should render welcome message with user name', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Welcome back, John!')).toBeInTheDocument()
      })
    })

    it('should display campaigns and templates stats', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Total Campaigns')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument()
        expect(screen.getByText('Templates')).toBeInTheDocument()
      })
    })

    it('should not show admin-only cards', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.queryByText('Active Instances')).not.toBeInTheDocument()
        expect(screen.queryByText('Tenants')).not.toBeInTheDocument()
      })
    })

    it('should show team card for non-admin users', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        const teamLinks = screen.getAllByText('Team')
        expect(teamLinks.length).toBeGreaterThan(0)
      })
    })

    it('should display recent campaigns', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Recent Campaigns')).toBeInTheDocument()
        expect(screen.getByText('Campaign 1')).toBeInTheDocument()
        expect(screen.getByText('Campaign 2')).toBeInTheDocument()
      })
    })
  })

  describe('Admin User View', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'Admin', email: 'admin@example.com' },
        isAdmin: () => true
      })
    })

    it('should display all stat cards including admin cards', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Total Campaigns')).toBeInTheDocument()
        expect(screen.getByText('Templates')).toBeInTheDocument()
        expect(screen.getByText('Active Instances')).toBeInTheDocument()
        expect(screen.getByText('Tenants')).toBeInTheDocument()
      })
    })

    it('should display correct counts for admin resources', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument() // instances count
      })
    })

    it('should show admin quick links', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Gophish Instances')).toBeInTheDocument()
        expect(screen.getByText('1 active instances')).toBeInTheDocument()
        expect(screen.getByText('Tenant Organizations')).toBeInTheDocument()
        expect(screen.getByText('1 tenants configured')).toBeInTheDocument()
      })
    })
  })

  describe('Quick Actions', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John' },
        isAdmin: () => false
      })
    })

    it('should show create campaign call-to-action', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Ready to create a new campaign?')).toBeInTheDocument()
        expect(screen.getByText('Launch a phishing simulation to test your team\'s awareness')).toBeInTheDocument()
      })
    })

    it('should display quick links section', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Quick Links')).toBeInTheDocument()
        expect(screen.getByText('Browse Templates')).toBeInTheDocument()
        expect(screen.getByText('Team Management')).toBeInTheDocument()
      })
    })
  })

  describe('Empty States', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John' },
        isAdmin: () => false
      })
      vi.spyOn(campaignsService, 'getCampaigns').mockResolvedValue([])
    })

    it('should show empty state for campaigns', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('No campaigns yet')).toBeInTheDocument()
        expect(screen.getByText('Create your first campaign')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John' },
        isAdmin: () => false
      })
    })

    it('should handle campaigns fetch error gracefully', async () => {
      vi.spyOn(campaignsService, 'getCampaigns').mockRejectedValue(
        new Error('Failed to fetch campaigns')
      )

      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        // Dashboard should still render with other data
        expect(screen.getByText('Welcome back, John!')).toBeInTheDocument()
      })
    })

    it('should display error message when critical error occurs', async () => {
      vi.spyOn(campaignsService, 'getCampaigns').mockRejectedValue(
        new Error('Critical error')
      )
      vi.spyOn(templatesService, 'getTemplates').mockRejectedValue(
        new Error('Critical error')
      )

      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Critical error')).toBeInTheDocument()
      })
    })
  })

  describe('Loading State', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John' },
        isAdmin: () => false
      })
    })

    it('should show loading state initially', () => {
      renderWithRouter(<Dashboard />)
      expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
    })
  })

  describe('Info Section', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'John' },
        isAdmin: () => false
      })
    })

    it('should display getting started information', async () => {
      renderWithRouter(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Getting Started with PhishNet')).toBeInTheDocument()
        expect(screen.getByText(/PhishNet helps you run phishing simulations/)).toBeInTheDocument()
      })
    })
  })
})
