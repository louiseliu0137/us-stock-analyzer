#!/usr/bin/env python3
"""
Email Sender Module
Handles sending HTML email reports
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.gmail_address = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([self.gmail_address, self.gmail_password, self.recipient_email]):
            raise ValueError("Missing email configuration in .env file")
    
    def send_email(self, subject: str, html_content: str, report_data: Optional[Dict] = None) -> bool:
        """
        Send HTML email with the report
        
        Args:
            subject: Email subject
            html_content: HTML content of the email
            report_data: Optional report data for logging
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.gmail_address
            message['To'] = self.recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_address, self.gmail_password)
                server.sendmail(
                    self.gmail_address,
                    self.recipient_email,
                    message.as_string()
                )
            
            logger.info(f"Email sent successfully to {self.recipient_email}")
            logger.info(f"Subject: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            logger.error("Make sure you are using an App Password, not your regular Gmail password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test email connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_address, self.gmail_password)
            logger.info("Email connection test successful")
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {str(e)}")
            return False
