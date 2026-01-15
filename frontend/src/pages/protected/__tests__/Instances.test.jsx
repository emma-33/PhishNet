import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Instances from '../Instances'
import * as instancesService from '../../../services/instancesService'

// Mock the services
vi.mock('../../../services/instancesService')

// Mock the date utils
vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

const mockInstances = [
  {
    id: 1,
    name: 'Production Instance',
    base_url: 'https://gophish.example.com',
    api_key: '****abcd',
    redirect_url: 'https://example.com/redirect',
    is_active: true,
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Testing Instance',
    base_url: 'https://gophish-test.example.com',
    api_key: '****xyz9',
    redirect_url: 'https://example.com/test-redirect',
    is_active: false,
    created_at: '2024-01-20T14:30:00Z'
  }
]

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Instances Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(instancesService, 'getInstances').mockResolvedValue(mockInstances)
  })

  it('should render instances table', async () => {
    renderWithRouter(<Instances />)

    await waitFor(() => {
      expect(screen.getByText('Production Instance')).toBeInTheDocument()
      expect(screen.getByText('Testing Instance')).toBeInTheDocument()
    })
  })

  it('should display instance details correctly', async () => {
    renderWithRouter(<Instances />)

    await waitFor(() => {
      expect(screen.getByText('https://gophish.example.com')).toBeInTheDocument()
      expect(screen.getByText('****abcd')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })
  })

  it('should show add instance button', async () => {
    renderWithRouter(<Instances />)

    await waitFor(() => {
      expect(screen.getByText('Add Instance')).toBeInTheDocument()
    })
  })

  it('should display empty state when no instances', async () => {
    vi.spyOn(instancesService, 'getInstances').mockResolvedValue([])
    renderWithRouter(<Instances />)

    await waitFor(() => {
      expect(screen.getByText('No instances')).toBeInTheDocument()
      expect(screen.getByText('Get started by adding your first Gophish instance.')).toBeInTheDocument()
    })
  })

  it('should open create modal when add button is clicked', async () => {
    renderWithRouter(<Instances />)

    await waitFor(() => {
      const addButton = screen.getByText('Add Instance')
      fireEvent.click(addButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Create New Instance')).toBeInTheDocument()
    })
  })

  it('should have action buttons for each instance', async () => {
    renderWithRouter(<Instances />)

    await waitFor(() => {
      // Should have toggle, edit, and delete buttons for each instance
      const editButtons = screen.getAllByTitle('Edit')
      const deleteButtons = screen.getAllByTitle('Delete')
      expect(editButtons).toHaveLength(2)
      expect(deleteButtons).toHaveLength(2)
    })
  })

  it('should call toggle status when toggle button is clicked', async () => {
    const toggleSpy = vi.spyOn(instancesService, 'toggleInstanceStatus').mockResolvedValue({})
    renderWithRouter(<Instances />)

    await waitFor(() => {
      const toggleButtons = screen.getAllByTitle(/Activate|Deactivate/)
      fireEvent.click(toggleButtons[0])
    })

    await waitFor(() => {
      expect(toggleSpy).toHaveBeenCalled()
    })
  })

  it('should display error message when fetch fails', async () => {
    vi.spyOn(instancesService, 'getInstances').mockRejectedValue(
      new Error('Failed to load instances')
    )
    
    renderWithRouter(<Instances />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load instances')).toBeInTheDocument()
    })
  })

  it('should show loading state initially', () => {
    renderWithRouter(<Instances />)
    expect(screen.getByText('Loading instances...')).toBeInTheDocument()
  })
})
