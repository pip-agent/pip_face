#!/usr/bin/env python3
"""
Pip Face - Email Sender Script
Sends emails using Gmail SMTP credentials from ~/.openclaw/.env
"""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

def send_email(recipient, subject, body, sender=None):
    """
    Send email via Gmail SMTP.
    
    Args:
        recipient (str): Email address to send to
        subject (str): Email subject
        body (str): Email body (plain text)
        sender (str, optional): Override sender email
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Load credentials
    env_file = Path.home() / '.openclaw' / '.env'
    env_data = {}
    
    try:
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    env_data[key.strip()] = val.strip().strip("'\"")
    except FileNotFoundError:
        print(f"❌ Error: {env_file} not found")
        return False
    
    smtp_user = env_data.get('SMTP_USER')
    smtp_pass = env_data.get('SMTP_PASS')
    
    if not smtp_user or not smtp_pass:
        print("❌ Error: SMTP_USER or SMTP_PASS not found in .env")
        return False
    
    sender = sender or smtp_user
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send via Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully!")
        print(f"   To: {recipient}")
        print(f"   Subject: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: send_email.py <recipient> <subject> [body_file]")
        print("")
        print("Examples:")
        print("  send_email.py user@example.com 'Test' 'This is a test'")
        print("  send_email.py user@example.com 'Report' message.txt")
        sys.exit(1)
    
    recipient = sys.argv[1]
    subject = sys.argv[2]
    
    if len(sys.argv) >= 4:
        # Read body from file
        try:
            with open(sys.argv[3]) as f:
                body = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {sys.argv[3]}")
            sys.exit(1)
    else:
        # Read from stdin
        print("Enter email body (Ctrl+D to send):")
        body = sys.stdin.read()
    
    success = send_email(recipient, subject, body)
    sys.exit(0 if success else 1)
