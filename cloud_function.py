#!/usr/bin/env python3
"""
Google Cloud Functions Entry Point
Cloud Function for stock market analysis
"""

import functions_framework
import os
from dotenv import load_dotenv
from analyzer import StockAnalyzer
from email_sender import EmailSender
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def analyze_market(request):
    """
    HTTP Cloud Function for stock market analysis.
    Triggered by Cloud Scheduler.
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with status
    """
    try:
        # Get analysis type from request parameter
        analysis_type = request.args.get('type', 'postmarket')
        
        logger.info(f"Starting {analysis_type} analysis...")
        
        # Initialize services
        analyzer = StockAnalyzer()
        email_sender = EmailSender()
        
        # Generate appropriate report
        if analysis_type == 'premarket':
            report = analyzer.generate_premarket_report()
            subject = f"美股盘前分析 - {datetime.now().strftime('%Y-%m-%d')}"
        else:
            report = analyzer.generate_postmarket_report()
            subject = f"美股收盘分析 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Format and send email
        html_email = analyzer.format_report_as_html(report, report_type=analysis_type)
        
        if email_sender.send_email(subject, html_email, report):
            logger.info(f"{analysis_type.capitalize()} analysis email sent successfully")
            return {
                'status': 'success',
                'message': f'{analysis_type.capitalize()} analysis completed and email sent',
                'timestamp': datetime.now().isoformat()
            }, 200
        else:
            logger.error(f"Failed to send {analysis_type} analysis email")
            return {
                'status': 'error',
                'message': f'Failed to send {analysis_type} analysis email',
                'timestamp': datetime.now().isoformat()
            }, 500
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500
