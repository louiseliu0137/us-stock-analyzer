#!/usr/bin/env python3
"""
US Stock Market Analyzer
Automated daily pre-market and post-market analysis with email reports
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time
import logging
from analyzer import StockAnalyzer
from email_sender import EmailSender

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockAnalyzerScheduler:
    def __init__(self):
        self.analyzer = StockAnalyzer()
        self.email_sender = EmailSender()
        self.timezone = os.getenv('TIME_ZONE', 'Asia/Shanghai')
        
    def run_premarket_analysis(self):
        """Run pre-market analysis at 21:00 Beijing Time"""
        logger.info("Starting pre-market analysis...")
        try:
            report = self.analyzer.generate_premarket_report()
            html_email = self.analyzer.format_report_as_html(report, report_type='premarket')
            subject = f"美股盘前分析 - {datetime.now().strftime('%Y-%m-%d')}"
            
            self.email_sender.send_email(
                subject=subject,
                html_content=html_email,
                report_data=report
            )
            logger.info("Pre-market analysis email sent successfully")
        except Exception as e:
            logger.error(f"Error in pre-market analysis: {str(e)}")
            
    def run_postmarket_analysis(self):
        """Run post-market analysis at 05:30 Beijing Time"""
        logger.info("Starting post-market analysis...")
        try:
            report = self.analyzer.generate_postmarket_report()
            html_email = self.analyzer.format_report_as_html(report, report_type='postmarket')
            subject = f"美股收盘分析 - {datetime.now().strftime('%Y-%m-%d')}"
            
            self.email_sender.send_email(
                subject=subject,
                html_content=html_email,
                report_data=report
            )
            logger.info("Post-market analysis email sent successfully")
        except Exception as e:
            logger.error(f"Error in post-market analysis: {str(e)}")
    
    def schedule_tasks(self):
        """Schedule the analysis tasks"""
        # Pre-market analysis at 21:00 (9 PM) Beijing Time
        schedule.every().monday.at("21:00").do(self.run_premarket_analysis)
        schedule.every().tuesday.at("21:00").do(self.run_premarket_analysis)
        schedule.every().wednesday.at("21:00").do(self.run_premarket_analysis)
        schedule.every().thursday.at("21:00").do(self.run_premarket_analysis)
        schedule.every().friday.at("21:00").do(self.run_premarket_analysis)
        logger.info("Scheduled pre-market analysis at 21:00 Beijing Time (Mon-Fri)")
        
        # Post-market analysis at 05:30 (5:30 AM) Beijing Time
        schedule.every().monday.at("05:30").do(self.run_postmarket_analysis)
        schedule.every().tuesday.at("05:30").do(self.run_postmarket_analysis)
        schedule.every().wednesday.at("05:30").do(self.run_postmarket_analysis)
        schedule.every().thursday.at("05:30").do(self.run_postmarket_analysis)
        schedule.every().friday.at("05:30").do(self.run_postmarket_analysis)
        logger.info("Scheduled post-market analysis at 05:30 Beijing Time (Mon-Fri)")
        
    def start(self):
        """Start the scheduler"""
        logger.info("Stock Analyzer Scheduler Started")
        self.schedule_tasks()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = StockAnalyzerScheduler()
    scheduler.start()
