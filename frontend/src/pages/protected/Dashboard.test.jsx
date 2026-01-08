import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from './Dashboard';
import * as api from '../../services/api';

// Mock the API modules
vi.mock('../../services/api', () => ({
  dashboardAPI: {
    getOverview: vi.fn(),
    getCampaigns: vi.fn(),
    getTemplates: vi.fn(),
    getGroups: vi.fn(),
  },
  trackingAPI: {
    getVisits: vi.fn(),
    getSubmissions: vi.fn(),
  },
}));

describe('Dashboard Component', () => {
  const mockOverviewData = {
    timestamp: '2024-01-01T00:00:00Z',
    system_status: {
      gophish: 'connected',
      email: 'operational',
      database: 'operational',
    },
    statistics: {
      total_campaigns: 5,
      active_campaigns: 2,
      total_visits: 100,
      total_submissions: 25,
    },
  };

  const mockCampaignsData = {
    campaigns: [
      {
        id: 1,
        name: 'Test Campaign 1',
        status: 'In Progress',
        statistics: { targets: 50 },
      },
      {
        id: 2,
        name: 'Test Campaign 2',
        status: 'Completed',
        statistics: { targets: 30 },
      },
    ],
  };

  const mockTemplatesData = {
    templates: [
      {
        id: 1,
        name: 'Phishing Template 1',
        subject: 'Urgent Security Update',
      },
      {
        id: 2,
        name: 'Phishing Template 2',
        subject: 'Account Verification Required',
      },
    ],
  };

  const mockGroupsData = {
    groups: [
      {
        id: 1,
        name: 'IT Department',
        targets: [{ email: 'user1@test.com' }, { email: 'user2@test.com' }],
      },
      {
        id: 2,
        name: 'HR Department',
        targets: [{ email: 'user3@test.com' }],
      },
    ],
  };

  const mockVisitsData = {
    visits: [
      {
        page_url: '/landing/test1',
        timestamp: '2024-01-01T10:00:00Z',
      },
      {
        page_url: '/landing/test2',
        timestamp: '2024-01-01T11:00:00Z',
      },
    ],
  };

  const mockSubmissionsData = {
    submissions: [
      {
        username: 'testuser1',
        timestamp: '2024-01-01T12:00:00Z',
      },
      {
        username: 'testuser2',
        timestamp: '2024-01-01T13:00:00Z',
      },
    ],
  };

  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    
    // Set up default successful responses
    api.dashboardAPI.getOverview.mockResolvedValue(mockOverviewData);
    api.dashboardAPI.getCampaigns.mockResolvedValue(mockCampaignsData);
    api.dashboardAPI.getTemplates.mockResolvedValue(mockTemplatesData);
    api.dashboardAPI.getGroups.mockResolvedValue(mockGroupsData);
    api.trackingAPI.getVisits.mockResolvedValue(mockVisitsData);
    api.trackingAPI.getSubmissions.mockResolvedValue(mockSubmissionsData);
  });

  it('should display loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('should load and display overview data', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('PhishNet Dashboard')).toBeInTheDocument();
    });

    // Check statistics cards
    expect(screen.getByText('5')).toBeInTheDocument(); // Total campaigns
    expect(screen.getByText('2')).toBeInTheDocument(); // Active campaigns
    expect(screen.getByText('100')).toBeInTheDocument(); // Total visits
    expect(screen.getByText('25')).toBeInTheDocument(); // Form submissions
  });

  it('should display system status correctly', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument();
    });

    expect(screen.getByText('connected')).toBeInTheDocument(); // GoPhish status
    expect(screen.getAllByText('operational')).toHaveLength(2); // Email & Database status
  });

  it('should display campaigns list', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Test Campaign 1')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Campaign 2')).toBeInTheDocument();
    expect(screen.getByText('50 targets')).toBeInTheDocument();
    expect(screen.getByText('30 targets')).toBeInTheDocument();
  });

  it('should display templates list', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Phishing Template 1')).toBeInTheDocument();
    });

    expect(screen.getByText('Urgent Security Update')).toBeInTheDocument();
    expect(screen.getByText('Phishing Template 2')).toBeInTheDocument();
    expect(screen.getByText('Account Verification Required')).toBeInTheDocument();
  });

  it('should display target groups', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('IT Department')).toBeInTheDocument();
    });

    expect(screen.getByText('HR Department')).toBeInTheDocument();
    expect(screen.getByText('2 targets')).toBeInTheDocument();
    expect(screen.getByText('1 targets')).toBeInTheDocument();
  });

  it('should display recent visits', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Recent Visits')).toBeInTheDocument();
    });

    expect(screen.getByText('/landing/test1')).toBeInTheDocument();
    expect(screen.getByText('/landing/test2')).toBeInTheDocument();
  });

  it('should display recent submissions', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Recent Submissions')).toBeInTheDocument();
    });

    expect(screen.getByText('testuser1')).toBeInTheDocument();
    expect(screen.getByText('testuser2')).toBeInTheDocument();
  });

  it('should handle API errors gracefully', async () => {
    api.dashboardAPI.getOverview.mockRejectedValue({
      response: { data: { error: 'API Error' } },
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText('API Error')).toBeInTheDocument();
  });

  it('should allow retry on error', async () => {
    api.dashboardAPI.getOverview.mockRejectedValueOnce({
      response: { data: { error: 'API Error' } },
    }).mockResolvedValue(mockOverviewData);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Retry');
    await userEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('PhishNet Dashboard')).toBeInTheDocument();
    });
  });

  it('should refresh data when refresh button is clicked', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('PhishNet Dashboard')).toBeInTheDocument();
    });

    const refreshButton = screen.getByText('Refresh');
    await userEvent.click(refreshButton);

    // Should call all APIs again
    await waitFor(() => {
      expect(api.dashboardAPI.getOverview).toHaveBeenCalledTimes(2);
    });
  });

  it('should handle missing campaigns gracefully', async () => {
    api.dashboardAPI.getCampaigns.mockRejectedValue(new Error('Campaigns disabled'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('No campaigns available')).toBeInTheDocument();
    });
  });

  it('should handle missing templates gracefully', async () => {
    api.dashboardAPI.getTemplates.mockRejectedValue(new Error('Templates disabled'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('No templates available')).toBeInTheDocument();
    });
  });

  it('should handle missing groups gracefully', async () => {
    api.dashboardAPI.getGroups.mockRejectedValue(new Error('Groups disabled'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('No groups available')).toBeInTheDocument();
    });
  });

  it('should display API endpoints section', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('API Endpoints')).toBeInTheDocument();
    });

    expect(screen.getByText('GET /api/dashboard/overview')).toBeInTheDocument();
    expect(screen.getByText('GET /api/dashboard/campaigns')).toBeInTheDocument();
    expect(screen.getByText('POST /api/dashboard/email/send')).toBeInTheDocument();
  });

  it('should call all API endpoints on mount', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(api.dashboardAPI.getOverview).toHaveBeenCalled();
      expect(api.dashboardAPI.getCampaigns).toHaveBeenCalled();
      expect(api.dashboardAPI.getTemplates).toHaveBeenCalled();
      expect(api.dashboardAPI.getGroups).toHaveBeenCalled();
      expect(api.trackingAPI.getVisits).toHaveBeenCalled();
      expect(api.trackingAPI.getSubmissions).toHaveBeenCalled();
    });
  });

  it('should display correct campaign count', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Campaigns (2)')).toBeInTheDocument();
    });
  });

  it('should display correct template count', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Email Templates (2)')).toBeInTheDocument();
    });
  });

  it('should display correct group count', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Target Groups (2)')).toBeInTheDocument();
    });
  });
});
