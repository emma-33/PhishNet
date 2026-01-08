"""
Email sending utility using SMTP (MailTrap for development)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EmailClient:
    """
    SMTP Email client for sending emails via MailTrap (development) or other SMTP servers.
    """
    
    def __init__(self, config):
        """
        Initialize email client with configuration.
        
        Args:
            config: Flask config object with MAIL_* settings
        """
        self.server = config.get('MAIL_SERVER')
        self.port = config.get('MAIL_PORT')
        self.username = config.get('MAIL_USERNAME')
        self.password = config.get('MAIL_PASSWORD')
        self.use_tls = config.get('MAIL_USE_TLS', True)
        self.use_ssl = config.get('MAIL_USE_SSL', False)
        self.default_sender = config.get('MAIL_DEFAULT_SENDER')
        
    def send_email(
        self,
        to: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            from_email: Optional sender email (uses default if not provided)
            headers: Optional custom headers
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.default_sender
            msg['To'] = ', '.join(to)
            
            # Add custom headers
            if headers:
                for key, value in headers.items():
                    msg[key] = value
            
            # Add text part
            text_part = MIMEText(body_text, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server and send
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.server, self.port)
            else:
                smtp = smtplib.SMTP(self.server, self.port)
                if self.use_tls:
                    smtp.starttls()
            
            # Login if credentials provided
            if self.username and self.password:
                smtp.login(self.username, self.password)
            
            # Send email
            smtp.sendmail(msg['From'], to, msg.as_string())
            smtp.quit()
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_phishing_email(
        self,
        to: str,
        template_data: Dict,
        campaign_id: str,
        tracking_url: str
    ) -> bool:
        """
        Send a phishing simulation email with tracking.
        
        Args:
            to: Recipient email address
            template_data: Email template data (subject, body_text, body_html)
            campaign_id: Campaign identifier for tracking
            tracking_url: URL to landing page with tracking
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = template_data.get('subject', 'Important Security Update')
            body_text = template_data.get('body_text', '')
            body_html = template_data.get('body_html', '')
            
            # Add tracking pixel to HTML body
            tracking_pixel = f'<img src="{tracking_url}/track/pixel/{campaign_id}?email={to}" width="1" height="1" style="display:none" />'
            if body_html:
                # Insert before closing body tag
                if '</body>' in body_html:
                    body_html = body_html.replace('</body>', f'{tracking_pixel}</body>')
                else:
                    body_html += tracking_pixel
            
            # Add custom headers for tracking
            headers = {
                'X-Campaign-ID': campaign_id,
                'X-PhishNet-Tracking': 'enabled'
            }
            
            return self.send_email(
                to=[to],
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Failed to send phishing email: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection without sending an email.
        
        Returns:
            bool: True if connection successful
        """
        try:
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.server, self.port, timeout=10)
            else:
                smtp = smtplib.SMTP(self.server, self.port, timeout=10)
                if self.use_tls:
                    smtp.starttls()
            
            if self.username and self.password:
                smtp.login(self.username, self.password)
            
            smtp.quit()
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
