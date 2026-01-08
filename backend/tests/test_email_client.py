"""
Tests for email client functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.email_client import EmailClient


class TestEmailClient:
    """Test suite for EmailClient"""
    
    def test_email_client_initialization(self, app):
        """Test email client initializes with config"""
        client = EmailClient(app.config)
        
        assert client.server == 'sandbox.smtp.mailtrap.io'
        assert client.port == 2525
        assert client.username == 'd40245d7b426e6'
        assert client.password == '45a1e4ba8ee3e9'
        assert client.use_tls is True
        assert client.default_sender == 'phishnet@example.com'
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, app):
        """Test sending email successfully"""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        result = client.send_email(
            to=['test@example.com'],
            subject='Test Subject',
            body_text='Test body'
        )
        
        assert result is True
        mock_smtp.assert_called_once_with('sandbox.smtp.mailtrap.io', 2525)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('d40245d7b426e6', '45a1e4ba8ee3e9')
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_email_with_html(self, mock_smtp, app):
        """Test sending email with HTML body"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        result = client.send_email(
            to=['test@example.com'],
            subject='Test Subject',
            body_text='Test body',
            body_html='<h1>Test HTML</h1>'
        )
        
        assert result is True
        # Verify sendmail was called (HTML was attached)
        assert mock_server.sendmail.called
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, app):
        """Test email sending failure handling"""
        # Setup mock to raise exception
        mock_smtp.side_effect = Exception('SMTP error')
        
        client = EmailClient(app.config)
        result = client.send_email(
            to=['test@example.com'],
            subject='Test',
            body_text='Test'
        )
        
        assert result is False
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_phishing_email(self, mock_smtp, app):
        """Test sending phishing email with tracking"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        template_data = {
            'subject': 'Security Alert',
            'body_text': 'Please verify your account',
            'body_html': '<html><body>Please verify</body></html>'
        }
        
        result = client.send_phishing_email(
            to='victim@example.com',
            template_data=template_data,
            campaign_id='test123',
            tracking_url='http://localhost:5000'
        )
        
        assert result is True
        # Verify tracking pixel was added
        call_args = mock_server.sendmail.call_args
        email_content = call_args[0][2]
        assert 'track/pixel/test123' in email_content
        assert 'X-Campaign-ID' in email_content
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_email_with_custom_headers(self, mock_smtp, app):
        """Test sending email with custom headers"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        headers = {'X-Custom-Header': 'test-value'}
        
        result = client.send_email(
            to=['test@example.com'],
            subject='Test',
            body_text='Test',
            headers=headers
        )
        
        assert result is True
        call_args = mock_server.sendmail.call_args
        email_content = call_args[0][2]
        assert 'X-Custom-Header: test-value' in email_content
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_test_connection_success(self, mock_smtp, app):
        """Test SMTP connection test success"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        result = client.test_connection()
        
        assert result is True
        mock_server.login.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_test_connection_failure(self, mock_smtp, app):
        """Test SMTP connection test failure"""
        mock_smtp.side_effect = Exception('Connection failed')
        
        client = EmailClient(app.config)
        result = client.test_connection()
        
        assert result is False
    
    @patch('utils.email_client.smtplib.SMTP')
    def test_send_email_multiple_recipients(self, mock_smtp, app):
        """Test sending email to multiple recipients"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        client = EmailClient(app.config)
        result = client.send_email(
            to=['user1@example.com', 'user2@example.com'],
            subject='Test',
            body_text='Test'
        )
        
        assert result is True
        call_args = mock_server.sendmail.call_args
        recipients = call_args[0][1]
        assert recipients == ['user1@example.com', 'user2@example.com']
