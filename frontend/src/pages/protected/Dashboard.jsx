import React, { useState, useEffect } from 'react';
import { dashboardAPI, trackingAPI } from '../../services/api';
import { 
  Activity, 
  Users, 
  Mail, 
  Database, 
  TrendingUp, 
  FileText,
  Send,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  X,
  BarChart,
  Eye,
  EyeOff
} from 'lucide-react';

function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [recentVisits, setRecentVisits] = useState([]);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [groups, setGroups] = useState([]);
  const [landingPages, setLandingPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Modal & feature states
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [campaignMetrics, setCampaignMetrics] = useState(null);
  const [showMetricsModal, setShowMetricsModal] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [selectedCampaignIds, setSelectedCampaignIds] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [emailForm, setEmailForm] = useState({
    to: '',
    subject: '',
    body_text: '',
    body_html: '',
    campaign_id: '',
    landing_page_id: ''
  });
  const [emailSending, setEmailSending] = useState(false);
  const [emailResult, setEmailResult] = useState(null);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [showSubmissionModal, setShowSubmissionModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [selectedLandingPage, setSelectedLandingPage] = useState(null);
  const [showLandingPageModal, setShowLandingPageModal] = useState(false);
  const [showAddTargetForm, setShowAddTargetForm] = useState(false);
  const [newTarget, setNewTarget] = useState({
    email: '',
    first_name: '',
    last_name: '',
    position: ''
  });
  const [addingTarget, setAddingTarget] = useState(false);

  // Fetch all data
  const fetchAllData = async () => {
    try {
      setError(null);
      setRefreshing(true);

      // Fetch overview data
      const overviewData = await dashboardAPI.getOverview();
      setOverview(overviewData);

      // Fetch campaigns
      try {
        const campaignsData = await dashboardAPI.getCampaigns();
        setCampaigns(campaignsData.campaigns || []);
      } catch (err) {
        console.log('Campaigns disabled or unavailable');
        setCampaigns([]);
      }

      // Fetch templates
      try {
        const templatesData = await dashboardAPI.getTemplates();
        setTemplates(templatesData.templates || []);
      } catch (err) {
        console.log('Templates disabled or unavailable');
        setTemplates([]);
      }

      // Fetch groups
      try {
        const groupsData = await dashboardAPI.getGroups();
        setGroups(groupsData.groups || []);
      } catch (err) {
        console.log('Groups disabled or unavailable');
        setGroups([]);
      }

      // Fetch landing pages
      try {
        const landingPagesData = await dashboardAPI.getLandingPages();
        setLandingPages(landingPagesData.landing_pages || []);
      } catch (err) {
        console.log('Landing pages disabled or unavailable');
        setLandingPages([]);
      }

      // Fetch recent tracking data
      try {
        const visitsData = await trackingAPI.getVisits();
        setRecentVisits((visitsData.visits || []).slice(0, 5));
      } catch (err) {
        setRecentVisits([]);
      }

      try {
        const submissionsData = await trackingAPI.getSubmissions(true); // Reveal passwords for security analysts
        setRecentSubmissions((submissionsData.submissions || []).slice(0, 5));
      } catch (err) {
        setRecentSubmissions([]);
      }

    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to load dashboard data';
      setError(errorMessage);
      console.error('Dashboard error:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        fullError: err
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Campaign metrics handler
  const handleViewMetrics = async (campaignId) => {
    try {
      const metrics = await dashboardAPI.getCampaignMetrics(campaignId);
      setCampaignMetrics(metrics);
      setSelectedCampaign(campaigns.find(c => c.id === campaignId));
      setShowMetricsModal(true);
    } catch (err) {
      alert('Failed to load campaign metrics: ' + (err.response?.data?.error || err.message || 'Unknown error'));
    }
  };

  // Campaign comparison handler
  const toggleCampaignSelection = (campaignId) => {
    setSelectedCampaignIds(prev => 
      prev.includes(campaignId) 
        ? prev.filter(id => id !== campaignId)
        : [...prev, campaignId]
    );
  };

  const handleCompareCampaigns = async () => {
    if (selectedCampaignIds.length < 2) {
      alert('Please select at least 2 campaigns to compare');
      return;
    }
    try {
      const comparison = await dashboardAPI.compareCampaigns(selectedCampaignIds);
      setComparisonData(comparison);
      setShowCompareModal(true);
    } catch (err) {
      alert('Failed to compare campaigns: ' + (err.response?.data?.error || err.message || 'Unknown error'));
    }
  };

  // Email sending handler
  const handleSendEmail = async (e) => {
    e.preventDefault();
    setEmailSending(true);
    setEmailResult(null);
    try {
      const result = await dashboardAPI.sendEmail(emailForm);
      setEmailResult({ success: true, data: result });
      // Reset form
      setEmailForm({
        to: '',
        subject: '',
        body_text: '',
        body_html: '',
        campaign_id: '',
        landing_page_id: ''
      });
    } catch (err) {
      setEmailResult({ 
        success: false, 
        error: err.response?.data?.error || 'Failed to send email' 
      });
    } finally {
      setEmailSending(false);
    }
  };

  const handleAddTarget = async (e) => {
    e.preventDefault();
    setAddingTarget(true);

    try {
      // TODO: Add backend endpoint POST /api/dashboard/groups/{groupId}/targets
      // For now, simulate success
      alert(`Adding target to group: ${selectedGroup.name}\n\nEmail: ${newTarget.email}\nName: ${newTarget.first_name} ${newTarget.last_name}\nPosition: ${newTarget.position}\n\nNote: Backend endpoint needed to persist this change.`);
      
      // Reset form
      setNewTarget({
        email: '',
        first_name: '',
        last_name: '',
        position: ''
      });
      setShowAddTargetForm(false);
      
      // Refresh data once backend endpoint is ready
      // await fetchAllData();
    } catch (err) {
      alert('Error adding target: ' + (err.message || 'Unknown error'));
    } finally {
      setAddingTarget(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    
    // Auto-refresh every 30 seconds only if no error
    const interval = setInterval(() => {
      if (!error) {
        fetchAllData();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [error]); // Re-setup interval when error state changes

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 font-semibold mb-2">Error Loading Dashboard</p>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchAllData}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Status indicator component
  const StatusBadge = ({ status }) => {
    const getStatusColor = () => {
      if (status === 'connected' || status === 'operational') return 'text-green-600 bg-green-100';
      if (status === 'disabled') return 'text-yellow-600 bg-yellow-100';
      return 'text-red-600 bg-red-100';
    };

    const getStatusIcon = () => {
      if (status === 'connected' || status === 'operational') return <CheckCircle className="w-4 h-4" />;
      if (status === 'disabled') return <AlertCircle className="w-4 h-4" />;
      return <XCircle className="w-4 h-4" />;
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
        {getStatusIcon()}
        {status}
      </span>
    );
  };

  // Statistics card component
  const StatCard = ({ icon: Icon, title, value, color }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">PhishNet Dashboard</h1>
          <p className="text-gray-600 mt-1">Phishing simulation and security awareness training</p>
        </div>
        <button
          onClick={fetchAllData}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">GoPhish</span>
            <StatusBadge status={overview?.system_status?.gophish || 'unknown'} />
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">Email System</span>
            <StatusBadge status={overview?.system_status?.email || 'unknown'} />
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">Database</span>
            <StatusBadge status={overview?.system_status?.database || 'unknown'} />
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-3">
          Last updated: {new Date(overview?.timestamp).toLocaleString()}
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          icon={TrendingUp}
          title="Total Campaigns"
          value={overview?.statistics?.total_campaigns || 0}
          color="bg-blue-500"
        />
        <StatCard
          icon={Activity}
          title="Active Campaigns"
          value={overview?.statistics?.active_campaigns || 0}
          color="bg-green-500"
        />
        <StatCard
          icon={Users}
          title="Total Visits"
          value={overview?.statistics?.total_visits || 0}
          color="bg-purple-500"
        />
        <StatCard
          icon={FileText}
          title="Form Submissions"
          value={overview?.statistics?.total_submissions || 0}
          color="bg-red-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaigns List */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Campaigns ({campaigns.length})
            </h2>
            <div className="flex gap-2">
              {selectedCampaignIds.length > 0 && (
                <button
                  onClick={handleCompareCampaigns}
                  className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 flex items-center gap-1"
                >
                  <BarChart className="w-4 h-4" />
                  Compare ({selectedCampaignIds.length})
                </button>
              )}
            </div>
          </div>
          {campaigns.length > 0 ? (
            <div className="space-y-3">
              {campaigns.slice(0, 10).map((campaign) => (
                <div key={campaign.id} className="p-3 border rounded hover:bg-gray-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={selectedCampaignIds.includes(campaign.id)}
                      onChange={() => toggleCampaignSelection(campaign.id)}
                      className="w-4 h-4"
                    />
                    <div 
                      className="flex-1 cursor-pointer"
                      onClick={() => handleViewMetrics(campaign.id)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium hover:text-blue-600">{campaign.name}</h3>
                          <p className="text-sm text-gray-500">{campaign.status}</p>
                        </div>
                        <span className="text-sm text-gray-600">
                          {campaign.statistics?.targets || 0} targets
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No campaigns available</p>
          )}
        </div>

        {/* Templates */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Email Templates ({templates.length})
          </h2>
          {templates.length > 0 ? (
            <div className="space-y-3">
              {templates.slice(0, 5).map((template) => (
                <div 
                  key={template.id} 
                  className="p-3 border rounded hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedTemplate(template);
                    setShowTemplateModal(true);
                  }}
                >
                  <h3 className="font-medium">{template.name}</h3>
                  <p className="text-sm text-gray-500 truncate">{template.subject}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No templates available</p>
          )}
        </div>

        {/* Target Groups */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5" />
            Target Groups ({groups.length})
          </h2>
          {groups.length > 0 ? (
            <div className="space-y-3">
              {groups.slice(0, 5).map((group) => (
                <div 
                  key={group.id} 
                  className="p-3 border rounded hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedGroup(group);
                    setShowGroupModal(true);
                  }}
                >
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium">{group.name}</h3>
                    <span className="text-sm text-gray-600">
                      {group.targets?.length || 0} targets
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No groups available</p>
          )}
        </div>

        {/* Landing Pages */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5" />
            Landing Pages ({landingPages.length})
          </h2>
          {landingPages.length > 0 ? (
            <div className="space-y-3">
              {landingPages.slice(0, 5).map((page) => (
                <div 
                  key={page.id} 
                  className="p-3 border rounded hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedLandingPage(page);
                    setShowLandingPageModal(true);
                  }}
                >
                  <h3 className="font-medium">{page.name}</h3>
                  <p className="text-xs text-gray-500 mt-1 truncate">
                    {page.capture_credentials ? '✓ Captures credentials' : 'No credential capture'}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No landing pages available</p>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Recent Activity
          </h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-sm text-gray-700 mb-2">Recent Visits</h3>
              {recentVisits.length > 0 ? (
                <div className="space-y-2">
                  {recentVisits.map((visit, index) => (
                    <div key={index} className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                      <p className="truncate">{visit.page_url}</p>
                      <p className="text-xs text-gray-500">{new Date(visit.timestamp).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent visits</p>
              )}
            </div>

            <div className="pt-4 border-t">
              <h3 className="font-medium text-sm text-gray-700 mb-2">Recent Submissions</h3>
              {recentSubmissions.length > 0 ? (
                <div className="space-y-2">
                  {recentSubmissions.map((submission, index) => (
                    <div 
                      key={index} 
                      className="text-sm text-gray-600 p-2 bg-gray-50 rounded hover:bg-blue-50 cursor-pointer transition-colors"
                      onClick={() => {
                        setSelectedSubmission(submission);
                        setShowSubmissionModal(true);
                      }}
                    >
                      <p className="font-medium">{submission.username || 'N/A'}</p>
                      <p className="text-xs text-gray-500">{new Date(submission.timestamp).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent submissions</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* API Endpoints Quick Access */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">API Endpoints</h2>
          <button
            onClick={() => setShowEmailForm(true)}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send Email
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/overview</code>
            <p className="text-xs text-gray-500 mt-1">System status & stats</p>
          </div>
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/campaigns</code>
            <p className="text-xs text-gray-500 mt-1">List all campaigns</p>
          </div>
          <div className="p-3 border rounded cursor-pointer hover:bg-gray-50" onClick={() => campaigns[0] && handleViewMetrics(campaigns[0].id)}>
            <code className="text-xs text-blue-600">GET /api/dashboard/campaigns/:id/metrics</code>
            <p className="text-xs text-gray-500 mt-1">Campaign metrics & rates</p>
          </div>
          <div className="p-3 border rounded cursor-pointer hover:bg-gray-50" onClick={selectedCampaignIds.length >= 2 ? handleCompareCampaigns : null}>
            <code className="text-xs text-blue-600">POST /api/dashboard/campaigns/compare</code>
            <p className="text-xs text-gray-500 mt-1">Compare campaigns</p>
          </div>
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/templates</code>
            <p className="text-xs text-gray-500 mt-1">Email templates</p>
          </div>
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/groups</code>
            <p className="text-xs text-gray-500 mt-1">Target groups</p>
          </div>
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/landing-pages</code>
            <p className="text-xs text-gray-500 mt-1">Landing pages list</p>
          </div>
          <div className="p-3 border rounded cursor-pointer hover:bg-gray-50" onClick={() => setShowEmailForm(true)}>
            <code className="text-xs text-blue-600">POST /api/dashboard/email/send</code>
            <p className="text-xs text-gray-500 mt-1">Send phishing email</p>
          </div>
          <div className="p-3 border rounded">
            <code className="text-xs text-blue-600">GET /api/dashboard/analytics/timeline</code>
            <p className="text-xs text-gray-500 mt-1">Timeline analytics</p>
          </div>
        </div>
      </div>

      {/* Campaign Metrics Modal */}
      {showMetricsModal && campaignMetrics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">{selectedCampaign?.name} - Metrics</h2>
                <button onClick={() => setShowMetricsModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-blue-50 rounded">
                  <p className="text-sm text-gray-600">Open Rate</p>
                  <p className="text-2xl font-bold">{campaignMetrics.metrics?.open_rate?.toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">{campaignMetrics.metrics?.opens_count} / {campaignMetrics.metrics?.emails_sent}</p>
                </div>
                <div className="p-4 bg-yellow-50 rounded">
                  <p className="text-sm text-gray-600">Click Rate</p>
                  <p className="text-2xl font-bold">{campaignMetrics.metrics?.click_rate?.toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">{campaignMetrics.metrics?.clicks_count} clicks</p>
                </div>
                <div className="p-4 bg-orange-50 rounded">
                  <p className="text-sm text-gray-600">Submission Rate</p>
                  <p className="text-2xl font-bold">{campaignMetrics.metrics?.submission_rate?.toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">{campaignMetrics.metrics?.submissions_count} submissions</p>
                </div>
                <div className="p-4 bg-red-50 rounded">
                  <p className="text-sm text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold">{campaignMetrics.metrics?.success_rate?.toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">Overall effectiveness</p>
                </div>
              </div>

              {/* Recommendations */}
              {campaignMetrics.recommendations && campaignMetrics.recommendations.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-3">Security Recommendations</h3>
                  <div className="space-y-2">
                    {campaignMetrics.recommendations.map((rec, idx) => (
                      <div 
                        key={idx} 
                        className={`p-3 rounded border-l-4 ${
                          rec.severity === 'critical' ? 'bg-red-50 border-red-500' :
                          rec.severity === 'warning' ? 'bg-yellow-50 border-yellow-500' :
                          'bg-green-50 border-green-500'
                        }`}
                      >
                        <p className="font-medium">{rec.message}</p>
                        <p className="text-xs text-gray-600 mt-1">Category: {rec.category}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Campaign Comparison Modal */}
      {showCompareModal && comparisonData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">Campaign Comparison</h2>
                <button onClick={() => setShowCompareModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Comparison Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="p-2 text-left">Campaign</th>
                      <th className="p-2 text-right">Open Rate</th>
                      <th className="p-2 text-right">Click Rate</th>
                      <th className="p-2 text-right">Submission Rate</th>
                      <th className="p-2 text-right">Success Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData.campaigns?.map((campaign) => (
                      <tr key={campaign.campaign_id} className="border-b">
                        <td className="p-2 font-medium">{campaign.campaign_name}</td>
                        <td className="p-2 text-right">{campaign.metrics.open_rate.toFixed(1)}%</td>
                        <td className="p-2 text-right">{campaign.metrics.click_rate.toFixed(1)}%</td>
                        <td className="p-2 text-right">{campaign.metrics.submission_rate.toFixed(1)}%</td>
                        <td className="p-2 text-right">{campaign.metrics.success_rate.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Analysis */}
              {comparisonData.analysis && (
                <div className="mt-6 space-y-4">
                  <div className="p-4 bg-green-50 rounded">
                    <p className="font-semibold">Most Effective</p>
                    <p className="text-sm">{comparisonData.analysis.most_effective}</p>
                  </div>
                  <div className="p-4 bg-red-50 rounded">
                    <p className="font-semibold">Least Effective</p>
                    <p className="text-sm">{comparisonData.analysis.least_effective}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Email Sending Form Modal */}
      {showEmailForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">Send Phishing Email</h2>
                <button onClick={() => setShowEmailForm(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSendEmail} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Recipient Email *</label>
                  <input
                    type="email"
                    required
                    value={emailForm.to}
                    onChange={(e) => setEmailForm({...emailForm, to: e.target.value})}
                    className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="victim@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Subject *</label>
                  <input
                    type="text"
                    required
                    value={emailForm.subject}
                    onChange={(e) => setEmailForm({...emailForm, subject: e.target.value})}
                    className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="Urgent: Account Verification Required"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Body Text *</label>
                  <textarea
                    required
                    value={emailForm.body_text}
                    onChange={(e) => setEmailForm({...emailForm, body_text: e.target.value})}
                    className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    rows="4"
                    placeholder="Plain text email body..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Body HTML (optional)</label>
                  <textarea
                    value={emailForm.body_html}
                    onChange={(e) => setEmailForm({...emailForm, body_html: e.target.value})}
                    className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    rows="4"
                    placeholder="<p>HTML email body...</p>"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Campaign ID</label>
                    <select
                      value={emailForm.campaign_id}
                      onChange={(e) => setEmailForm({...emailForm, campaign_id: e.target.value})}
                      className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select campaign...</option>
                      {campaigns.map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Landing Page</label>
                    <select
                      value={emailForm.landing_page_id}
                      onChange={(e) => setEmailForm({...emailForm, landing_page_id: e.target.value})}
                      className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select landing page...</option>
                      {landingPages.map(lp => (
                        <option key={lp.id} value={lp.id}>{lp.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {emailResult && (
                  <div className={`p-4 rounded ${emailResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                    {emailResult.success ? (
                      <div>
                        <p className="font-semibold">Email sent successfully!</p>
                        <p className="text-sm mt-1">Tracking Pixel ID: {emailResult.data?.tracking_pixel_id}</p>
                        <p className="text-sm">Tracking URL: {emailResult.data?.tracking_url}</p>
                      </div>
                    ) : (
                      <p>{emailResult.error}</p>
                    )}
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowEmailForm(false)}
                    className="px-4 py-2 border rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={emailSending}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 flex items-center gap-2"
                  >
                    {emailSending ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Send Email
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Submission Details Modal */}
      {showSubmissionModal && selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">Submission Details</h2>
                <button onClick={() => setShowSubmissionModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Credentials Section */}
                <div className="p-4 bg-red-50 border border-red-200 rounded">
                  <h3 className="font-semibold text-red-800 mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Captured Credentials
                  </h3>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-gray-600 uppercase">Username</p>
                      <p className="font-mono text-sm bg-white p-2 rounded border">{selectedSubmission.username || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 uppercase flex items-center justify-between">
                        <span>Password</span>
                        <button
                          onClick={() => setShowPassword(!showPassword)}
                          className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-xs"
                        >
                          {showPassword ? (
                            <>
                              <EyeOff className="w-3 h-3" />
                              Hide
                            </>
                          ) : (
                            <>
                              <Eye className="w-3 h-3" />
                              Show
                            </>
                          )}
                        </button>
                      </p>
                      <p className="font-mono text-sm bg-white p-2 rounded border">
                        {showPassword 
                          ? (selectedSubmission.password || 'N/A')
                          : '••••••••'
                        }
                      </p>
                    </div>
                  </div>
                </div>

                {/* Metadata Section */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">IP Address</p>
                    <p className="font-medium">{selectedSubmission.ip_address || 'Unknown'}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Submitted At</p>
                    <p className="font-medium text-sm">
                      {selectedSubmission.timestamp || selectedSubmission.created_at
                        ? new Date(selectedSubmission.timestamp || selectedSubmission.created_at).toLocaleString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })
                        : 'Unknown'}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Landing Page ID</p>
                    <p className="font-medium">{selectedSubmission.page_id || 'N/A'}</p>
                    <p className="text-xs text-gray-500 mt-1">Which page captured this</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Campaign ID</p>
                    <p className="font-medium">{selectedSubmission.campaign_id || 'N/A'}</p>
                    <p className="text-xs text-gray-500 mt-1">Associated campaign</p>
                  </div>
                </div>

                {/* User Agent */}
                {selectedSubmission.user_agent && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">User Agent</p>
                    <p className="text-sm break-all">{selectedSubmission.user_agent}</p>
                  </div>
                )}

                {/* All Form Data */}
                {selectedSubmission.form_data && Object.keys(selectedSubmission.form_data).length > 0 && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-2">Additional Form Data</p>
                    <div className="space-y-1">
                      {Object.entries(selectedSubmission.form_data).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="font-medium">{key}:</span> <span className="font-mono">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowSubmissionModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Template Details Modal */}
      {showTemplateModal && selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <FileText className="w-6 h-6" />
                  Template Details
                </h2>
                <button
                  onClick={() => setShowTemplateModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-600 uppercase mb-1">Template Name</p>
                  <p className="font-medium text-lg">{selectedTemplate.name}</p>
                </div>

                <div>
                  <p className="text-xs text-gray-600 uppercase mb-1">Subject Line</p>
                  <p className="font-medium">{selectedTemplate.subject}</p>
                </div>

                {selectedTemplate.html && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-2">HTML Preview</p>
                    <div className="border rounded p-4 bg-gray-50 max-h-96 overflow-y-auto">
                      <iframe
                        srcDoc={selectedTemplate.html}
                        className="w-full h-64 border-0"
                        title="Template Preview"
                        sandbox="allow-same-origin"
                      />
                    </div>
                  </div>
                )}

                {selectedTemplate.text && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-2">Text Content</p>
                    <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto whitespace-pre-wrap">
                      {selectedTemplate.text}
                    </pre>
                  </div>
                )}

                {selectedTemplate.modified_date && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Last Modified</p>
                    <p className="text-sm">
                      {new Date(selectedTemplate.modified_date).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowTemplateModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Target Group Details Modal */}
      {showGroupModal && selectedGroup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <Users className="w-6 h-6" />
                  Target Group Details
                </h2>
                <button
                  onClick={() => setShowGroupModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-600 uppercase mb-1">Group Name</p>
                  <p className="font-medium text-lg">{selectedGroup.name}</p>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-1">Total Targets</p>
                    <p className="font-medium text-2xl text-blue-600">{selectedGroup.targets?.length || 0}</p>
                  </div>
                  <button
                    onClick={() => setShowAddTargetForm(!showAddTargetForm)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
                  >
                    <Users className="w-4 h-4" />
                    {showAddTargetForm ? 'Cancel' : 'Add Target'}
                  </button>
                </div>

                {/* Add Target Form */}
                {showAddTargetForm && (
                  <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                    <h3 className="font-semibold text-blue-900 mb-3">Add New Target</h3>
                    <form onSubmit={handleAddTarget} className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Email Address <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="email"
                          required
                          value={newTarget.email}
                          onChange={(e) => setNewTarget({ ...newTarget, email: e.target.value })}
                          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                          placeholder="user@example.com"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            First Name
                          </label>
                          <input
                            type="text"
                            value={newTarget.first_name}
                            onChange={(e) => setNewTarget({ ...newTarget, first_name: e.target.value })}
                            className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                            placeholder="John"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Last Name
                          </label>
                          <input
                            type="text"
                            value={newTarget.last_name}
                            onChange={(e) => setNewTarget({ ...newTarget, last_name: e.target.value })}
                            className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                            placeholder="Doe"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Position
                        </label>
                        <input
                          type="text"
                          value={newTarget.position}
                          onChange={(e) => setNewTarget({ ...newTarget, position: e.target.value })}
                          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                          placeholder="Manager, IT Department"
                        />
                      </div>
                      <button
                        type="submit"
                        disabled={addingTarget || !newTarget.email}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {addingTarget ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Adding...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-4 h-4" />
                            Add Target
                          </>
                        )}
                      </button>
                      <p className="text-xs text-gray-600 italic">
                        Note: Backend endpoint needed to persist changes to GoPhish
                      </p>
                    </form>
                  </div>
                )}

                {selectedGroup.targets && selectedGroup.targets.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-2">Target List</p>
                    <div className="border rounded overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Email</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">First Name</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Last Name</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Position</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {selectedGroup.targets.map((target, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-4 py-2 text-sm">{target.email}</td>
                              <td className="px-4 py-2 text-sm">{target.first_name || '-'}</td>
                              <td className="px-4 py-2 text-sm">{target.last_name || '-'}</td>
                              <td className="px-4 py-2 text-sm">{target.position || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {selectedGroup.modified_date && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Last Modified</p>
                    <p className="text-sm">
                      {new Date(selectedGroup.modified_date).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowGroupModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Landing Page Details Modal */}
      {showLandingPageModal && selectedLandingPage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <Database className="w-6 h-6" />
                  Landing Page Details
                </h2>
                <button
                  onClick={() => setShowLandingPageModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-600 uppercase mb-1">Page Name</p>
                  <p className="font-medium text-lg">{selectedLandingPage.name}</p>
                </div>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-sm font-medium text-blue-800">
                    {selectedLandingPage.capture_credentials 
                      ? '✓ This page captures user credentials' 
                      : 'This page does not capture credentials'}
                  </p>
                </div>

                {selectedLandingPage.html && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-2">HTML Preview</p>
                    <div className="border rounded p-4 bg-gray-50 max-h-96 overflow-y-auto">
                      <iframe
                        srcDoc={selectedLandingPage.html}
                        className="w-full h-96 border-0"
                        title="Landing Page Preview"
                        sandbox="allow-same-origin"
                      />
                    </div>
                  </div>
                )}

                {selectedLandingPage.capture_data && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase mb-2">Captured Fields</p>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm font-mono">{JSON.stringify(selectedLandingPage.capture_data, null, 2)}</p>
                    </div>
                  </div>
                )}

                {selectedLandingPage.redirect_url && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Redirect URL</p>
                    <p className="text-sm font-mono break-all">{selectedLandingPage.redirect_url}</p>
                  </div>
                )}

                {selectedLandingPage.modified_date && (
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 uppercase mb-1">Last Modified</p>
                    <p className="text-sm">
                      {new Date(selectedLandingPage.modified_date).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowLandingPageModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
