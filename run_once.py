#!/usr/bin/env python3
"""
Run analysis and send email once (for testing)
"""

import os
from dotenv import load_dotenv
from analyzer import StockAnalyzer
from email_sender import EmailSender
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    try:
        logger.info("Initializing analyzer and email sender...")
        analyzer = StockAnalyzer()
        email_sender = EmailSender()
        
        # Test email connection
        logger.info("Testing email connection...")
        if not email_sender.test_connection():
            logger.error("Email connection failed. Please check your credentials.")
            return False
        
        logger.info("Email connection successful!")
        
        # Generate post-market report
        logger.info("Generating post-market analysis report...")
        report = analyzer.generate_postmarket_report()
        html_email = analyzer.format_report_as_html(report, report_type='postmarket')
        
        subject = f"美股收盘分析测试 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Send email
        logger.info("Sending email...")
        if email_sender.send_email(
            subject=subject,
            html_content=html_email,
            report_data=report
        ):
            logger.info("✅ Test email sent successfully!")
            logger.info(f"Email should arrive at {os.getenv('RECIPIENT_EMAIL')} shortly.")
            return True
        else:
            logger.error("❌ Failed to send email")
            return False
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
