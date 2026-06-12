#!/usr/bin/env python3
"""
Email Diagnostic Script
Comprehensive testing of email configuration and connectivity
"""

import os
import smtplib
import logging
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_env_variables():
    """Test if environment variables are properly loaded"""
    print("\n" + "="*60)
    print("STEP 1: Checking Environment Variables")
    print("="*60)
    
    gmail_address = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    print(f"✓ GMAIL_ADDRESS: {gmail_address}")
    print(f"✓ GMAIL_PASSWORD: {'*' * len(gmail_password) if gmail_password else 'NOT SET'}")
    print(f"✓ RECIPIENT_EMAIL: {recipient_email}")
    
    if not all([gmail_address, gmail_password, recipient_email]):
        print("\n❌ ERROR: Missing environment variables!")
        return False
    
    if len(gmail_password.split()) != 4:
        print(f"\n⚠️ WARNING: Password format seems wrong. Expected 4 groups, got {len(gmail_password.split())}")
    
    print("\n✅ All environment variables loaded successfully")
    return True

def test_smtp_connection():
    """Test SMTP connection to Gmail"""
    print("\n" + "="*60)
    print("STEP 2: Testing SMTP Connection to Gmail")
    print("="*60)
    
    gmail_address = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    
    try:
        print("Attempting to connect to smtp.gmail.com:465...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        print("✓ Connected to smtp.gmail.com:465")
        
        print(f"Attempting to login with {gmail_address}...")
        server.login(gmail_address, gmail_password)
        print(f"✓ Successfully logged in as {gmail_address}")
        
        server.quit()
        print("\n✅ SMTP connection and authentication successful!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {str(e)}")
        print("\nPossible causes:")
        print("1. Incorrect app password (should be 16 characters with spaces)")
        print("2. Two-factor authentication not enabled on Gmail account")
        print("3. Gmail account security settings blocking the connection")
        print("\nSolutions:")
        print("- Visit: https://myaccount.google.com/apppasswords")
        print("- Regenerate your app password")
        print("- Ensure two-factor authentication is enabled")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {str(e)}")
        return False

def test_email_send():
    """Test sending an actual email"""
    print("\n" + "="*60)
    print("STEP 3: Testing Email Sending")
    print("="*60)
    
    gmail_address = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    try:
        print("Creating email message...")
        message = MIMEMultipart('alternative')
        message['Subject'] = "🧪 Test Email - Weather Dashboard Diagnostic"
        message['From'] = gmail_address
        message['To'] = recipient_email
        
        # Create HTML content
        html = """
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #667eea;">✅ Email Test Successful!</h2>
                <p>This is a test email from the Weather Dashboard application.</p>
                <p><strong>Test Details:</strong></p>
                <ul>
                    <li>Sender: """ + gmail_address + """</li>
                    <li>Recipient: """ + recipient_email + """</li>
                    <li>Time: """ + str(__import__('datetime').datetime.now()) + """</li>
                </ul>
                <p>If you received this email, your email configuration is working correctly!</p>
                <hr>
                <p style="color: #999; font-size: 12px;">Sent by US Stock Analyzer - Weather Dashboard</p>
            </body>
        </html>
        """
        
        html_part = MIMEText(html, 'html')
        message.attach(html_part)
        
        print("Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            print("Logging in...")
            server.login(gmail_address, gmail_password)
            
            print(f"Sending email to {recipient_email}...")
            server.sendmail(gmail_address, recipient_email, message.as_string())
            print(f"✓ Email sent successfully to {recipient_email}")
        
        print("\n✅ Email sent successfully!")
        print(f"   From: {gmail_address}")
        print(f"   To: {recipient_email}")
        print(f"   Subject: Test Email - Weather Dashboard Diagnostic")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_actual_analyzer():
    """Test using the actual StockAnalyzer and EmailSender"""
    print("\n" + "="*60)
    print("STEP 4: Testing with StockAnalyzer & EmailSender Classes")
    print("="*60)
    
    try:
        print("Importing StockAnalyzer...")
        from analyzer import StockAnalyzer
        print("✓ StockAnalyzer imported successfully")
        
        print("Importing EmailSender...")
        from email_sender import EmailSender
        print("✓ EmailSender imported successfully")
        
        print("\nInitializing EmailSender...")
        email_sender = EmailSender()
        print("✓ EmailSender initialized")
        
        print("\nTesting connection...")
        if email_sender.test_connection():
            print("✓ Email connection test passed!")
        else:
            print("❌ Email connection test failed!")
            return False
        
        print("\nInitializing StockAnalyzer...")
        analyzer = StockAnalyzer()
        print("✓ StockAnalyzer initialized")
        
        print("\nGenerating test report...")
        report = analyzer.generate_postmarket_report()
        print("✓ Report generated")
        
        print("\nFormatting report as HTML...")
        html_email = analyzer.format_report_as_html(report, report_type='postmarket')
        print(f"✓ HTML report generated ({len(html_email)} bytes)")
        
        print("\nSending formatted report email...")
        subject = "🧪 Test Stock Analysis Report"
        if email_sender.send_email(subject, html_email, report):
            print("✓ Formatted report email sent successfully!")
            return True
        else:
            print("❌ Failed to send formatted report email")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("\n" + "="*60)
    print("📧 EMAIL CONFIGURATION DIAGNOSTIC")
    print("="*60)
    
    results = []
    
    # Test 1: Environment Variables
    results.append(("Environment Variables", test_env_variables()))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed - environment variables not properly configured")
        return
    
    # Test 2: SMTP Connection
    results.append(("SMTP Connection", test_smtp_connection()))
    
    if not results[1][1]:
        print("\n❌ Cannot proceed - SMTP connection failed")
        return
    
    # Test 3: Email Send
    results.append(("Email Sending", test_email_send()))
    
    if not results[2][1]:
        print("\n❌ Cannot proceed - Email sending failed")
        return
    
    # Test 4: Analyzer Integration
    results.append(("StockAnalyzer Integration", test_with_actual_analyzer()))
    
    # Summary
    print("\n" + "="*60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your email configuration is working correctly.")
        print("\nNext steps:")
        print("1. Run: python main.py (to start automated analysis)")
        print("2. Or deploy to Google Cloud for 24/7 operation")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Verify your app password at: https://myaccount.google.com/apppasswords")
        print("2. Ensure two-factor authentication is enabled")
        print("3. Check that .env file has correct values")

if __name__ == "__main__":
    main()
