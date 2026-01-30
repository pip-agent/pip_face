#!/usr/bin/env python3
"""
Pip Face - Email Command Processor
Reads inbox and executes commands from emails
"""

import imaplib
import email
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

def get_credentials():
    """Load IMAP credentials from ~/.openclaw/.env"""
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
        return None, None
    
    imap_user = env_data.get('IMAP_USER')
    imap_pass = env_data.get('IMAP_PASS')
    
    if not imap_user or not imap_pass:
        print("❌ Error: IMAP_USER or IMAP_PASS not found")
        return None, None
    
    return imap_user, imap_pass

def connect_imap(user, password):
    """Connect to Gmail IMAP"""
    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        imap.login(user, password)
        imap.select('INBOX')
        return imap
    except Exception as e:
        print(f"❌ IMAP error: {e}")
        return None

def extract_body(msg):
    """Extract email body text"""
    if msg.is_multipart():
        for part in msg.get_payload():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    return ""

def parse_commands(body):
    """
    Parse commands from email body.
    Supported formats:
    - "write to telegram: message" (can be multiline)
    - "escreva no telegram: message" (Portuguese)
    - "send email to X: subject: body"
    """
    commands = []
    
    # Pattern: "write/escreva ... telegram: ..." (multiline)
    telegram_match = re.search(
        r'(?:write|escreva)\s+(?:to\s+)?telegram\s*:\s*["\']?([^"\']+?)["\']?(?:\n|$)',
        body, 
        re.IGNORECASE | re.DOTALL
    )
    if telegram_match:
        msg = telegram_match.group(1).strip().strip('"\'').strip()
        if msg:
            commands.append(('telegram', msg))
    
    # Also look for quoted text in next lines
    if not commands and 'telegram' in body.lower():
        lines = body.split('\n')
        for i, line in enumerate(lines):
            if 'telegram' in line.lower() and ':' in line:
                # Get next non-empty line
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('--'):
                        msg = lines[j].strip().strip('"\'')
                        if msg and len(msg) > 3:
                            commands.append(('telegram', msg))
                            break
    
    # Pattern: "send email to X: subject: body"
    email_match = re.search(r'send\s+email\s+to\s+([^:]+)\s*:\s*([^:]+)\s*:\s*([^\n]+)', body, re.IGNORECASE)
    if email_match:
        commands.append(('email', {
            'to': email_match.group(1).strip(),
            'subject': email_match.group(2).strip(),
            'body': email_match.group(3).strip()
        }))
    
    return commands

def execute_telegram_command(message):
    """Send message to Telegram"""
    try:
        result = subprocess.run(
            ['clawdbot', 'message', 'send', '--channel', 'telegram', 
             '--target', '@NL3M05', '--message', message],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Telegram: {message[:50]}...")
            return True
        else:
            print(f"⚠️ Telegram send failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return False

def execute_email_command(to, subject, body):
    """Send email"""
    try:
        result = subprocess.run(
            ['/home/nl3mos/clawd/scripts/send_email.py', to, subject],
            input=body,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Email sent to {to}")
            return True
        else:
            print(f"⚠️ Email send failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def process_recent_emails(minutes=30):
    """Process emails from last N minutes"""
    user, password = get_credentials()
    if not user or not password:
        return
    
    imap = connect_imap(user, password)
    if not imap:
        return
    
    try:
        # Search for emails from last N minutes
        since_date = (datetime.now() - timedelta(minutes=minutes)).strftime('%d-%b-%Y')
        status, messages = imap.search(None, f'SINCE {since_date}')
        email_ids = messages[0].split()
        
        if not email_ids:
            print("ℹ️ No recent emails to process")
            return
        
        print(f"📧 Processing {len(email_ids)} recent email(s)...")
        
        for email_id in email_ids:
            try:
                status, msg_data = imap.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                from_addr = msg['From']
                subject = msg['Subject']
                body = extract_body(msg)
                
                # Only process emails from Nilson
                if 'nilson' not in from_addr.lower() and 'lemos' not in from_addr.lower():
                    continue
                
                print(f"\n📬 From: {from_addr}")
                print(f"   Subject: {subject}")
                
                # Parse and execute commands
                commands = parse_commands(body)
                
                if commands:
                    for cmd_type, cmd_data in commands:
                        if cmd_type == 'telegram':
                            execute_telegram_command(cmd_data)
                        elif cmd_type == 'email':
                            execute_email_command(cmd_data['to'], cmd_data['subject'], cmd_data['body'])
                else:
                    print("   (No commands found)")
            
            except Exception as e:
                print(f"⚠️ Error processing email: {e}")
        
        imap.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    process_recent_emails(minutes)
