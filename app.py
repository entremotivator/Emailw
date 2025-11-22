import streamlit as st
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------
# 🔧 CONFIGURATION
# ------------------------------

SHEET_ID = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"

# ------------------------------
# 🎨 CUSTOM CSS STYLING
# ------------------------------

def load_custom_css():
    """Load custom CSS for a beautiful card-based UI."""
    st.markdown("""
    <style>
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #000000;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Stats container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.25);
    }
    
    .stat-card.teal {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .stat-card.purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stat-card.orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .stat-card.blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .stat-card.green {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    .stat-number {
        font-size: 48px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 16px;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Email cards */
    .email-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #667eea;
        color: #000000;
    }
    
    .email-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .email-card.priority-high {
        border-left-color: #f5576c;
        background: linear-gradient(to right, #fff5f5 0%, white 100%);
    }
    
    .email-card.priority-medium {
        border-left-color: #f093fb;
        background: linear-gradient(to right, #fff8fd 0%, white 100%);
    }
    
    .email-card.priority-low {
        border-left-color: #38ef7d;
        background: linear-gradient(to right, #f0fff4 0%, white 100%);
    }
    
    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .sender-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 20px;
        margin-right: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .sender-details {
        flex: 1;
    }
    
    .sender-name {
        font-size: 18px;
        font-weight: 700;
        color: #000000;
        margin-bottom: 3px;
    }
    
    .sender-email {
        font-size: 13px;
        color: #000000;
        opacity: 0.8;
    }
    
    .subject {
        font-size: 16px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 10px;
    }
    
    .summary {
        font-size: 14px;
        color: #000000;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    
    .ai-reply-preview {
        background: linear-gradient(135deg, #e0f7fa 0%, #e1f5fe 100%);
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 13px;
        border-left: 3px solid #00bcd4;
        color: #000000;
    }
    
    .email-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
    }
    
    .date {
        font-size: 13px;
        color: #000000;
        font-weight: 500;
    }
    
    .tag {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .tag.attachment {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    .tag.no-attachment {
        background: #e0e0e0;
        color: #000000;
    }
    
    .tag.ai {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Draft cards */
    .draft-card {
        background: linear-gradient(to right, #fff9e6 0%, white 100%);
        border: 2px solid #ffc107;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(255,193,7,0.2);
        color: #000000;
    }
    
    .draft-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .draft-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 18px;
        margin-right: 12px;
    }
    
    .draft-badge {
        background: #ffc107;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        margin-left: 8px;
    }
    
    .draft-field {
        margin-bottom: 8px;
        font-size: 14px;
        color: #000000;
    }
    
    .draft-field strong {
        color: #000000;
        font-weight: 600;
    }
    
    /* Horizontal menu */
    .horizontal-menu {
        background: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* Analytics cards */
    .analytics-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        color: #000000;
    }
    
    .contact-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .contact-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    }
    </style>
    """, unsafe_allow_html=True)

# ... existing code ...

def get_gmail_credentials():
    """Get Gmail credentials from Streamlit secrets."""
    try:
        gmail_email = st.secrets["gmail"]["email"]
        gmail_password = st.secrets["gmail"]["password"]
        return gmail_email, gmail_password
    except Exception as e:
        return None, None

def authenticate_gsheets(credentials_dict):
    """Authenticate with Google Sheets using service account credentials."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return None

# ... existing code ...

def load_data_from_gsheet(gc, sheet_id=SHEET_ID):
    """Load data from Google Sheets."""
    try:
        worksheet = gc.open_by_key(sheet_id).sheet1
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        if 'priority' not in df.columns:
            df['priority'] = 'medium'
        
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {str(e)}")
        return generate_mock_data(num_emails=25)

def get_initials(name):
    """Extract initials from a name."""
    if not name or name == "Unknown Sender":
        return "?"
    
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "?"

def generate_mock_data(num_emails=25):
    """Generate comprehensive mock email data for demonstration."""
    departments = ["Sales", "Support", "Marketing", "HR", "Engineering", "Finance", "Operations"]
    priorities = ["high", "medium", "low"]
    
    senders = [
        ("John Smith", "john.smith@example.com"),
        ("Sarah Johnson", "sarah.j@company.com"),
        ("Michael Chen", "m.chen@business.com"),
        ("Emily Davis", "emily.davis@corp.com"),
        ("Robert Wilson", "r.wilson@enterprise.com"),
        ("Jennifer Garcia", "j.garcia@firm.com"),
        ("David Martinez", "david.m@organization.com"),
        ("Lisa Anderson", "lisa.anderson@group.com"),
        ("James Taylor", "james.t@company.com"),
        ("Maria Rodriguez", "maria.r@business.com"),
        ("Custom All Stars", "customallstars@gmail.com"),
        ("Blogz.life Community", "info@blogz.life"),
        ("Team Lead", "team.lead@company.com"),
        ("Project Manager", "pm@organization.com"),
        ("CEO Office", "ceo@enterprise.com")
    ]
    
    subjects = [
        "Q4 Sales Report Review",
        "Urgent: Customer Issue Resolution",
        "Marketing Campaign Performance",
        "Employee Onboarding Schedule",
        "System Update Deployment",
        "Budget Approval Request",
        "Monthly Operations Report",
        "Client Meeting Follow-up",
        "Product Launch Timeline",
        "Training Session Confirmation",
        "ai_systems_checklist",
        "[Blogz- The Blogging Community] A new subscriber has (been) registered!",
        "Project Status Update",
        "Quarterly Review Meeting",
        "Contract Renewal Discussion"
    ]
    
    ai_replies = [
        "<p>Dear {name},</p><p>Thank you for reaching out. I've reviewed the materials and have prepared a comprehensive response. Let's schedule a brief call to discuss the next steps and ensure we're aligned on all deliverables.</p><p>Best regards</p>",
        "<p>Hi {name},</p><p>I appreciate you bringing this to my attention. I've analyzed the situation and recommend the following approach: 1) Immediate action on critical items, 2) Weekly progress reviews, 3) Final assessment by month-end.</p><p>Looking forward to your feedback.</p>",
        "<p>Hello {name},</p><p>Thanks for the update. I've reviewed the documentation and everything looks good. I approve moving forward with the proposed timeline. Please keep me posted on any developments.</p><p>Best</p>",
        "<p>Dear {name},</p><p>I've received your request and need some additional information before proceeding: project scope, timeline expectations, and resource requirements. Could you provide these details at your earliest convenience?</p><p>Thank you</p>",
        "heythere who are you",
        "New subscriber on Blogz: yaralennon29 (ys4058319@gmail.com).",
        "<p>Hi {name},</p><p>Following up on our previous discussion. I've completed the analysis and have some recommendations. Would you be available for a quick meeting this week?</p><p>Thanks</p>"
    ]
    
    emails = []
    for i in range(num_emails):
        sender_name, sender_email = random.choice(senders)
        subject = random.choice(subjects)
        department = random.choice(departments)
        priority = random.choice(priorities)
        has_attachment = random.choice([True, False])
        has_ai_reply = random.choice([True, True, False])
        
        # Generate date within last 60 days
        days_ago = random.randint(0, 60)
        email_date = datetime.now() - pd.Timedelta(days=days_ago)
        
        summary = f"This is regarding {subject.lower()}. The matter requires attention from the {department} department. Please review the details and provide your feedback at your earliest convenience."
        
        ai_reply = ""
        if has_ai_reply:
            reply_template = random.choice(ai_replies)
            ai_reply = reply_template.replace("{name}", sender_name.split()[0])
        
        emails.append({
            "sender name": sender_name,
            "sender email": sender_email,
            "subject": subject,
            "summary": summary,
            "date": email_date.strftime("%Y-%m-%d"),
            "attachment": "Yes" if has_attachment else "No",
            "aireply": ai_reply,
            "department": department,
            "priority": priority
        })
    
    return pd.DataFrame(emails)

# ... existing code ...

def send_real_email(to_address, subject, body, cc_address=None, attachments=None, use_html=True):
    """Send a real email using Gmail SMTP."""
    try:
        gmail_email, gmail_password = get_gmail_credentials()
        
        if not gmail_email or not gmail_password:
            st.error("Gmail credentials not configured. Please add them to .streamlit/secrets.toml")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_email
        msg['To'] = to_address
        msg['Subject'] = subject
        
        if cc_address:
            msg['Cc'] = cc_address
        
        if use_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
                msg.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_email, gmail_password)
            recipients = [to_address]
            if cc_address:
                recipients.append(cc_address)
            server.sendmail(gmail_email, recipients, msg.as_string())
        
        return True
        
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def save_to_sent_items(email_data, credentials_dict=None):
    """Save sent email to Google Sheets and session state."""
    try:
        if 'sent_items' not in st.session_state:
            st.session_state['sent_items'] = []
        
        sent_email = {
            'sender name': email_data.get('from_name', 'Me'),
            'sender email': email_data.get('from_email', ''),
            'subject': email_data.get('subject', ''),
            'summary': email_data.get('body', '')[:200] + '...' if len(email_data.get('body', '')) > 200 else email_data.get('body', ''),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'attachment': 'Yes' if email_data.get('attachments') else 'No',
            'aireply': '',
            'department': email_data.get('department', 'Sent'),
            'priority': email_data.get('priority', 'medium'),
            'to_address': email_data.get('to', ''),
            'sent_at': datetime.now().isoformat()
        }
        
        st.session_state['sent_items'].append(sent_email)
        
        if credentials_dict:
            try:
                gc = authenticate_gsheets(credentials_dict)
                if gc:
                    worksheet = gc.open_by_key(SHEET_ID).worksheet('Sent')
                    
                    row_data = [
                        sent_email['sender name'],
                        sent_email['sender email'],
                        sent_email['subject'],
                        sent_email['summary'],
                        sent_email['date'],
                        sent_email['attachment'],
                        sent_email['aireply'],
                        sent_email['department'],
                        sent_email['priority'],
                        sent_email['to_address'],
                        sent_email['sent_at']
                    ]
                    worksheet.append_row(row_data)
            except Exception as sheet_error:
                st.warning(f"Could not save to Google Sheets: {sheet_error}")
        
        return True
    except Exception as e:
        st.error(f"Error saving sent email: {e}")
        return False

# ... existing code ...

def display_stats(df):
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    # <CHANGE> Fixed the KeyError by safely checking column existence
    with_attachments = df[df['attachment'].str.lower().isin(['yes', 'true', '1'])].shape[0] if 'attachment' in df.columns else 0
    high_priority = df[df['priority'] == 'high'].shape[0] if 'priority' in df.columns else 0
    ai_replies_ready = df[df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))].shape[0] if 'aireply' in df.columns else 0
    
    # <CHANGE> Added more statistics
    medium_priority = df[df['priority'] == 'medium'].shape[0] if 'priority' in df.columns else 0
    low_priority = df[df['priority'] == 'low'].shape[0] if 'priority' in df.columns else 0
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{total_emails}</div>
            <div class="stat-label">Total Emails</div>
        </div>
        <div class="stat-card teal">
            <div class="stat-number">{with_attachments}</div>
            <div class="stat-label">With Attachments</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{high_priority}</div>
            <div class="stat-label">High Priority</div>
        </div>
        <div class="stat-card purple">
            <div class="stat-number">{ai_replies_ready}</div>
            <div class="stat-label">AI Replies Ready</div>
        </div>
        <div class="stat-card blue">
            <div class="stat-number">{medium_priority}</div>
            <div class="stat-label">Medium Priority</div>
        </div>
        <div class="stat-card green">
            <div class="stat-number">{low_priority}</div>
            <div class="stat-label">Low Priority</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_email_card(email_data, index, credentials_dict=None):
    """Render one email entry as a colorful card with action buttons."""
    sender_name = email_data.get("sender name", "Unknown Sender")
    sender_email = email_data.get("sender email", "")
    subject = email_data.get("subject", "No Subject")
    summary = email_data.get("summary", "No summary available")
    date = email_data.get("date", "")
    attachment = email_data.get("attachment", "No")
    ai_reply = email_data.get("aireply", "")
    department = email_data.get("department", "General")
    priority = email_data.get("priority", "low")
    
    initials = get_initials(sender_name)

    try:
        formatted_date = datetime.strptime(str(date), "%Y-%m-%d").strftime("%b %d, %Y")
    except:
        formatted_date = str(date)

    has_attachment = str(attachment).lower() in ["yes", "true", "1"]
    has_ai_reply = bool(ai_reply and str(ai_reply).strip() not in ["", "nan", "None", "null"])
    
    attachment_tag = f'<span class="tag attachment">📎 Attachment</span>' if has_attachment else f'<span class="tag no-attachment">No Attachment</span>'
    ai_tag = f'<span class="tag ai">🤖 AI Suggestion</span>' if has_ai_reply else ''
    
    ai_reply_preview = ""
    if has_ai_reply:
        preview_text = re.sub('<[^<]+?>', '', str(ai_reply))
        preview_text = preview_text.replace('\n', ' ').strip()
        preview_text = preview_text[:150] + "..." if len(preview_text) > 150 else preview_text
        ai_reply_preview = f'<div class="ai-reply-preview"><strong>AI Suggestion:</strong> {preview_text}</div>'

    card_html = f"""
    <div class="email-card priority-{priority}">
        <div class="sender-info">
            <div class="sender-avatar">{initials}</div>
            <div class="sender-details">
                <div class="sender-name">{sender_name}</div>
                <div class="sender-email">&lt;{sender_email}&gt;</div>
            </div>
        </div>
        <div class="subject">{subject}</div>
        <div class="summary">{summary}</div>
        {ai_reply_preview}
        <div class="email-meta">
            <div class="date">📅 {formatted_date} | 🏢 {department} | ⚡ Priority: {priority.upper()}</div>
            <div>{ai_tag} {attachment_tag}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        if st.button("✉️ Reply", key=f"reply_{index}", use_container_width=True):
            st.session_state['selected_email'] = email_data
            st.session_state['page'] = 'compose'
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col2:
        if st.button("🤖 Use AI Reply", key=f"ai_reply_{index}", disabled=not has_ai_reply, use_container_width=True, type="primary"):
            st.session_state['selected_email'] = email_data
            st.session_state['page'] = 'compose'
            st.session_state['use_ai_reply'] = True
            st.rerun()
    with col3:
        if st.button("💾 Save as Draft", key=f"draft_{index}", use_container_width=True):
            if 'drafts' not in st.session_state:
                st.session_state['drafts'] = []
            
            draft = {
                'sender name': sender_name,
                'sender email': sender_email,
                'subject': f"Re: {subject}",
                'summary': summary,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'attachment': attachment,
                'aireply': ai_reply,
                'department': department,
                'priority': priority,
                'original_email': email_data
            }
            st.session_state['drafts'].append(draft)
            st.toast("Draft saved successfully!", icon="✅")
    with col4:
        if st.button("🗄️ Archive", key=f"archive_{index}", use_container_width=True):
            st.toast(f"Archived email from {sender_name}!", icon="✅")
    
    st.markdown("---")

# ... existing code ...

def render_compose(email_data=None):
    """Renders the compose page for replying to an email or drafting a new one."""
    st.markdown("## ✍️ Compose Email")
    
    gmail_email, gmail_password = get_gmail_credentials()
    gmail_configured = bool(gmail_email and gmail_password)
    
    if not gmail_configured:
        st.warning("⚠️ Gmail not configured. Add credentials to .streamlit/secrets.toml to send real emails.")
        with st.expander("📖 How to configure Gmail"):
            st.markdown("""
            Create a file `.streamlit/secrets.toml` with:
            ```toml
            [gmail]
            email = "your-email@gmail.com"
            password = "your-app-password"
            ```
            
            **Note:** Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail, not your regular password.
            """)
    else:
        st.success(f"✅ Gmail configured: {gmail_email}")
    
    if st.session_state.get('use_ai_reply') and email_data:
        initial_body = email_data.get('aireply', '')
    else:
        initial_body = ""
    
    if email_data:
        st.info(f"**Replying to:** {email_data.get('sender name', 'Unknown')} - {email_data.get('subject', 'No Subject')}")
        
        reply_subject = f"Re: {email_data.get('subject', '')}"
        recipient = email_data.get('sender email', '')
        
        with st.expander("📧 View Original Email", expanded=False):
            st.markdown(f"**From:** {email_data.get('sender name', 'Unknown')} ({email_data.get('sender email', '')})")
            st.markdown(f"**Department:** {email_data.get('department', 'N/A')}")
            st.markdown(f"**Date:** {email_data.get('date', 'N/A')}")
            st.markdown(f"**Summary:** {email_data.get('summary', 'No summary available')}")
            if email_data.get('aireply'):
                st.markdown("---")
                st.markdown("**AI Suggestion:**")
                st.markdown(email_data.get('aireply', ''), unsafe_allow_html=True)
        
        st.markdown("### Choose Reply Method")
        reply_method = st.radio(
            "How would you like to reply?",
            options=["Custom Message", "Use Template", "Use AI Suggestion"],
            horizontal=True
        )
        
        if reply_method == "Use AI Suggestion":
            ai_reply_body = email_data.get('aireply', '')
            initial_body = ai_reply_body if ai_reply_body else "No AI suggestion available for this email."
        elif reply_method == "Use Template":
            st.markdown("**Select a Template:**")
            templates = {
                "Acknowledgment": f"<p>Dear {email_data.get('sender name', 'there')},</p><p>Thank you for your email regarding <strong>{email_data.get('subject', 'this matter')}</strong>. I have reviewed the details and will follow up with specific action items by end of day.</p><p>In the meantime, please let me know if you need any additional information.</p><p>Best regards</p>",
                "Schedule Meeting": f"<p>Dear {email_data.get('sender name', 'there')},</p><p>Regarding <strong>{email_data.get('subject', 'this matter')}</strong>, I suggest we schedule a brief meeting to discuss this in detail. I have availability tomorrow afternoon or Thursday morning.</p><p>Please let me know what works best for you.</p><p>Best regards</p>",
                "Request More Info": f"<p>Dear {email_data.get('sender name', 'there')},</p><p>Thank you for reaching out about <strong>{email_data.get('subject', 'this matter')}</strong>. To better assist you, could you please provide additional details about:</p><ul><li>Specific requirements</li><li>Timeline expectations</li><li>Any relevant documentation</li></ul><p>Looking forward to your response.</p><p>Best regards</p>",
                "Approval": f"<p>Dear {email_data.get('sender name', 'there')},</p><p>Thank you for the update on <strong>{email_data.get('subject', 'this matter')}</strong>. I've reviewed the information and approve the proposed approach.</p><p>Let's proceed as discussed and reconvene next week to review progress.</p><p>Best regards</p>",
                "Follow Up": f"<p>Dear {email_data.get('sender name', 'there')},</p><p>I've received your email about <strong>{email_data.get('subject', 'this matter')}</strong> and am currently reviewing the details. I should have feedback for you by tomorrow morning.</p><p>Thanks for your patience on this matter.</p><p>Best regards</p>"
            }
            
            template_choice = st.selectbox(
                "Choose a template:",
                options=list(templates.keys())
            )
            
            if template_choice:
                initial_body = templates[template_choice]
                st.markdown("**Template Preview:**")
                st.markdown(f"<div style='background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; color: #000000;'>{initial_body}</div>", unsafe_allow_html=True)
    else:
        st.info("📝 Composing a new email.")
        reply_subject = ""
        recipient = ""
    
    st.markdown("---")
    st.markdown("### Compose Your Message")
    
    with st.form("compose_form"):
        to_address = st.text_input("To:", value=recipient, placeholder="recipient@example.com")
        cc_address = st.text_input("CC:", placeholder="cc@example.com (optional)")
        subject = st.text_input("Subject:", value=reply_subject, placeholder="Email subject")
        
        st.markdown("**Message Body:**")
        
        col_editor1, col_editor2 = st.columns([1, 4])
        with col_editor1:
            editor_mode = st.selectbox("Editor Mode:", ["Plain Text", "HTML"])
        with col_editor2:
            if editor_mode == "HTML":
                st.info("HTML mode: You can use HTML tags for formatting")
        
        body = st.text_area(
            "Body:", 
            value=initial_body, 
            height=400,
            placeholder="Type your message here..." if editor_mode == "Plain Text" else "Type your message here using HTML formatting...",
            label_visibility="collapsed"
        )
        
        if editor_mode == "HTML":
            st.markdown("""
            <div style='background: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 13px; color: #000000;'>
            <strong>Quick HTML Tips:</strong> 
            &lt;strong&gt;bold&lt;/strong&gt;, 
            &lt;em&gt;italic&lt;/em&gt;, 
            &lt;p&gt;paragraph&lt;/p&gt;, 
            &lt;ul&gt;&lt;li&gt;bullet&lt;/li&gt;&lt;/ul&gt;
            </div>
            """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Attachments (optional):",
            accept_multiple_files=True,
            help="You can attach multiple files"
        )
        
        if uploaded_files:
            st.info(f"📎 {len(uploaded_files)} file(s) attached: {', '.join([f.name for f in uploaded_files])}")
        
        st.markdown("---")
        st.markdown("### 👀 Email Preview")
        preview_container = st.container()
        with preview_container:
            st.markdown(f"**To:** {to_address or '[No recipient]'}")
            if cc_address:
                st.markdown(f"**CC:** {cc_address}")
            st.markdown(f"**Subject:** {subject or '[No subject]'}")
            st.markdown("**Body:**")
            if editor_mode == "HTML":
                st.markdown(f"<div style='background: #f9f9f9; padding: 15px; border-radius: 8px; color: #000000;'>{body or '[Empty body]'}</div>", unsafe_allow_html=True)
            else:
                st.text(body or "[Empty body]")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            send_button = st.form_submit_button("📤 Send Email", type="primary", use_container_width=True)
        with col2:
            save_draft_button = st.form_submit_button("💾 Save Draft", use_container_width=True)
        with col3:
            clear_button = st.form_submit_button("🧹 Clear", use_container_width=True)
        with col4:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if send_button:
            if not to_address:
                st.error("Please enter a recipient email address!")
            elif not subject:
                st.error("Please enter an email subject!")
            elif not body:
                st.error("Please enter email body!")
            elif not gmail_configured:
                st.error("Gmail credentials not configured. Cannot send email.")
            else:
                with st.spinner("Sending email..."):
                    use_html = (editor_mode == "HTML")
                    success = send_real_email(
                        to_address=to_address,
                        subject=subject,
                        body=body,
                        cc_address=cc_address if cc_address else None,
                        attachments=uploaded_files if uploaded_files else None,
                        use_html=use_html
                    )
                    
                    if success:
                        st.success("✅ Email sent successfully!")
                        
                        credentials_dict = st.session_state.get('credentials', None)
                        email_sent_data = {
                            'from_name': 'Me',
                            'from_email': gmail_email,
                            'to': to_address,
                            'subject': subject,
                            'body': body,
                            'attachments': uploaded_files,
                            'department': 'Sent',
                            'priority': 'medium'
                        }
                        save_to_sent_items(email_sent_data, credentials_dict)
                        
                        time.sleep(2)
                        st.session_state['page'] = 'sent'
                        st.rerun()
                    else:
                        st.error("Failed to send email. Please check your credentials and try again.")
        
        if save_draft_button:
            if not subject and not body:
                st.error("Cannot save empty draft!")
            else:
                if 'drafts' not in st.session_state:
                    st.session_state['drafts'] = []
                
                draft = {
                    'sender name': 'Me',
                    'sender email': gmail_email or 'your-email@gmail.com',
                    'subject': subject or '(No Subject)',
                    'summary': body[:200] + '...' if len(body) > 200 else body,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'attachment': 'Yes' if uploaded_files else 'No',
                    'aireply': '',
                    'department': 'Draft',
                    'priority': 'medium',
                    'to_address': to_address,
                    'cc_address': cc_address,
                    'body': body,
                    'editor_mode': editor_mode,
                    'original_email': email_data
                }
                st.session_state['drafts'].append(draft)
                st.success("✅ Draft saved successfully!")
                time.sleep(1)
                st.session_state['page'] = 'drafts'
                st.rerun()
        
        if clear_button:
            st.rerun()
        
        if cancel_button:
            st.session_state['page'] = 'inbox'
            st.rerun()

def render_drafts():
    """Renders the drafts page showing saved draft emails."""
    st.markdown("## 📝 Drafts")
    
    if 'drafts' not in st.session_state or len(st.session_state['drafts']) == 0:
        st.info("📭 No drafts saved yet. Compose an email and save it as a draft to see it here!")
        
        if st.button("✍️ Compose New Email"):
            st.session_state['page'] = 'compose'
            st.session_state['selected_email'] = None
            st.rerun()
        return
    
    st.success(f"You have **{len(st.session_state['drafts'])}** saved draft(s).")
    st.markdown("---")
    
    for idx, draft in enumerate(st.session_state['drafts']):
        sender_name = draft.get('sender name', 'Draft')
        sender_email = draft.get('sender email', '')
        subject = draft.get('subject', 'No Subject')
        summary = draft.get('summary', 'No content')
        date = draft.get('date', datetime.now().strftime("%Y-%m-%d"))
        attachment = draft.get('attachment', 'No')
        aireply = draft.get('aireply', '')
        department = draft.get('department', 'General')
        
        initials = get_initials(sender_name)
        
        try:
            formatted_date = datetime.strptime(str(date), "%Y-%m-%d").strftime("%b %d, %Y")
        except:
            formatted_date = str(date)
        
        draft_html = f"""
        <div class="draft-card">
            <div class="draft-header">
                <div class="draft-avatar">{initials}</div>
                <div>
                    <div style="font-weight: 700; font-size: 16px; color: #000000;">{sender_name} <span class="draft-badge">DRAFT</span></div>
                    <div style="font-size: 13px; color: #000000;">&lt;{sender_email}&gt;</div>
                </div>
            </div>
            <div class="draft-field"><strong>Subject:</strong> {subject}</div>
            <div class="draft-field"><strong>Summary:</strong> {summary}</div>
            <div class="draft-field"><strong>Date:</strong> {formatted_date}</div>
            <div class="draft-field"><strong>Department:</strong> {department}</div>
            <div class="draft-field"><strong>Attachment:</strong> {attachment}</div>
        </div>
        """
        st.markdown(draft_html, unsafe_allow_html=True)
        
        with st.expander("👁️ View Full Draft"):
            st.markdown(f"**To:** {draft.get('to_address', 'N/A')}")
            st.markdown(f"**CC:** {draft.get('cc_address', 'N/A')}")
            st.markdown(f"**Editor Mode:** {draft.get('editor_mode', 'Plain Text')}")
            st.markdown("---")
            st.markdown("**Body:**")
            st.markdown(draft.get('body', 'No content'), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("✏️ Edit", key=f"edit_draft_{idx}", use_container_width=True):
                st.session_state['selected_email'] = draft.get('original_email')
                st.session_state['page'] = 'compose'
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", key=f"delete_draft_{idx}", use_container_width=True):
                st.session_state['drafts'].pop(idx)
                st.toast("Draft deleted!", icon="🗑️")
                st.rerun()
        
        st.markdown("---")

def render_sent():
    """Renders the sent items page."""
    st.markdown("## 📤 Sent Items")
    
    if 'sent_items' not in st.session_state or len(st.session_state['sent_items']) == 0:
        st.info("📭 No sent items yet. Send an email to see it here!")
        return
    
    st.success(f"You have sent **{len(st.session_state['sent_items'])}** email(s).")
    st.markdown("---")
    
    for idx, sent in enumerate(st.session_state['sent_items']):
        display_email_card(sent, f"sent_{idx}")

def render_inbox(df, credentials_dict=None):
    """Renders the inbox page with email cards and stats."""
    st.markdown("## 📨 Inbox")
    
    display_stats(df)
    
    st.markdown("---")
    
    # <CHANGE> Enhanced filtering with search functionality
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        priority_filter = st.selectbox("🎯 Filter by Priority:", ["All", "High", "Medium", "Low"])
    with col2:
        department_filter = st.selectbox("🏢 Filter by Department:", ["All"] + list(df['department'].unique()) if 'department' in df.columns else ["All"])
    with col3:
        attachment_filter = st.selectbox("📎 Attachments:", ["All", "With Attachments", "Without Attachments"])
    with col4:
        search_query = st.text_input("🔍 Search:", placeholder="Search sender or subject...")
    
    filtered_df = df.copy()
    
    # Apply filters
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter.lower()]
    if department_filter != "All" and 'department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['department'] == department_filter]
    if attachment_filter == "With Attachments":
        filtered_df = filtered_df[filtered_df['attachment'].str.lower().isin(['yes', 'true', '1'])]
    elif attachment_filter == "Without Attachments":
        filtered_df = filtered_df[~filtered_df['attachment'].str.lower().isin(['yes', 'true', '1'])]
    
    # Apply search filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df['sender name'].str.contains(search_query, case=False, na=False) |
            filtered_df['subject'].str.contains(search_query, case=False, na=False)
        ]
    
    st.markdown(f"### {len(filtered_df)} Email(s)")
    
    if len(filtered_df) == 0:
        st.info("📭 No emails to display with the current filters.")
        return
    
    for idx, row in filtered_df.iterrows():
        display_email_card(row.to_dict(), idx, credentials_dict)

# <CHANGE> Added new Analytics page
def render_analytics(df):
    """Renders the analytics dashboard with charts and insights."""
    st.markdown("## 📊 Email Analytics Dashboard")
    
    st.markdown("Get insights into your email patterns, response times, and communication trends.")
    st.markdown("---")
    
    # Time-based analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("### 📅 Emails Over Time")
        
        if 'date' in df.columns:
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            emails_by_date = df_copy.groupby(df_copy['date'].dt.date).size().reset_index(name='count')
            
            fig = px.line(emails_by_date, x='date', y='count', 
                         title='Email Volume Trend',
                         labels={'date': 'Date', 'count': 'Number of Emails'})
            fig.update_traces(line_color='#667eea', line_width=3)
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Date information not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Priority Distribution")
        
        if 'priority' in df.columns:
            priority_counts = df['priority'].value_counts()
            
            fig = px.pie(values=priority_counts.values, names=priority_counts.index,
                        title='Emails by Priority',
                        color_discrete_sequence=['#f5576c', '#f093fb', '#38ef7d'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Priority information not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Department analysis
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 Emails by Department")
        
        if 'department' in df.columns:
            dept_counts = df['department'].value_counts().head(10)
            
            fig = px.bar(x=dept_counts.index, y=dept_counts.values,
                        title='Top 10 Departments',
                        labels={'x': 'Department', 'y': 'Email Count'},
                        color=dept_counts.values,
                        color_continuous_scale='Viridis')
            fig.update_layout(template='plotly_white', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Department information not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.markdown("### 📎 Attachment Statistics")
        
        if 'attachment' in df.columns:
            attachment_counts = df['attachment'].str.lower().isin(['yes', 'true', '1']).value_counts()
            labels = ['With Attachments', 'Without Attachments']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=[attachment_counts.get(True, 0), attachment_counts.get(False, 0)],
                hole=.4,
                marker_colors=['#11998e', '#e0e0e0']
            )])
            fig.update_layout(title='Attachment Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Attachment information not available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Reply analysis
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Reply Coverage")
    
    col5, col6, col7 = st.columns(3)
    
    if 'aireply' in df.columns:
        ai_replies = df[df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))].shape[0]
        ai_percentage = (ai_replies / len(df) * 100) if len(df) > 0 else 0
        
        with col5:
            st.metric("AI Replies Available", ai_replies, f"{ai_percentage:.1f}%")
        with col6:
            st.metric("Pending Replies", len(df) - ai_replies)
        with col7:
            st.metric("Coverage Rate", f"{ai_percentage:.1f}%", "Good" if ai_percentage > 60 else "Needs Improvement")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Top senders
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown("### 👥 Top Email Senders")
    
    if 'sender name' in df.columns:
        top_senders = df['sender name'].value_counts().head(10)
        
        fig = px.bar(x=top_senders.values, y=top_senders.index,
                    orientation='h',
                    title='Top 10 Email Senders',
                    labels={'x': 'Number of Emails', 'y': 'Sender'},
                    color=top_senders.values,
                    color_continuous_scale='Blues')
        fig.update_layout(template='plotly_white', showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sender information not available")
    
    st.markdown('</div>', unsafe_allow_html=True)

# <CHANGE> Added new Contacts page
def render_contacts(df):
    """Renders the contacts management page."""
    st.markdown("## 👥 Contacts Management")
    
    st.markdown("Manage and organize your email contacts.")
    st.markdown("---")
    
    if 'sender name' not in df.columns or 'sender email' not in df.columns:
        st.error("Contact information not available in the dataset")
        return
    
    # Extract unique contacts
    contacts = df[['sender name', 'sender email']].drop_duplicates()
    contacts = contacts.sort_values('sender name')
    
    st.success(f"📇 You have **{len(contacts)}** unique contacts")
    
    # Search contacts
    search = st.text_input("🔍 Search contacts:", placeholder="Search by name or email...")
    
    if search:
        contacts = contacts[
            contacts['sender name'].str.contains(search, case=False, na=False) |
            contacts['sender email'].str.contains(search, case=False, na=False)
        ]
    
    st.markdown(f"### Showing {len(contacts)} contact(s)")
    st.markdown("---")
    
    # Display contacts
    for idx, row in contacts.iterrows():
        name = row['sender name']
        email = row['sender email']
        initials = get_initials(name)
        
        # Count emails from this contact
        email_count = len(df[df['sender email'] == email])
        
        # Get department if available
        dept = df[df['sender email'] == email]['department'].mode()[0] if 'department' in df.columns else 'N/A'
        
        contact_html = f"""
        <div class="contact-card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="sender-avatar">{initials}</div>
                <div style="flex: 1;">
                    <div style="font-size: 18px; font-weight: 700; color: #000000;">{name}</div>
                    <div style="font-size: 14px; color: #666; margin: 5px 0;">✉️ {email}</div>
                    <div style="font-size: 13px; color: #888;">🏢 {dept} | 📧 {email_count} email(s)</div>
                </div>
            </div>
        </div>
        """
        st.markdown(contact_html, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"✉️ Email", key=f"email_{idx}", use_container_width=True):
                st.session_state['page'] = 'compose'
                st.session_state['selected_email'] = {'sender name': name, 'sender email': email}
                st.rerun()

def render_settings():
    """Renders the settings page."""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    st.markdown("---")
    
    # Gmail settings
    st.markdown("### 📧 Gmail Configuration")
    with st.expander("Gmail SMTP Settings", expanded=True):
        gmail_email, gmail_password = get_gmail_credentials()
        
        if gmail_email and gmail_password:
            st.success(f"✅ Gmail configured: {gmail_email}")
            st.info("To update credentials, edit your `.streamlit/secrets.toml` file")
        else:
            st.warning("⚠️ Gmail not configured")
            st.markdown("""
            Create a file `.streamlit/secrets.toml` with:
            ```toml
            [gmail]
            email = "your-email@gmail.com"
            password = "your-app-password"
            ```
            
            **Note:** Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail, not your regular password.
            """)
    
    st.markdown("---")
    
    # Google Sheets settings
    st.markdown("### 📊 Google Sheets Integration")
    with st.expander("Sheet Configuration", expanded=True):
        credentials_dict = st.session_state.get('credentials', None)
        
        if credentials_dict:
            st.success("✅ Google Sheets credentials loaded")
            if 'client_email' in credentials_dict:
                st.info(f"Service Account: {credentials_dict['client_email']}")
            st.markdown(f"**Sheet ID:** `{SHEET_ID}`")
        else:
            st.warning("⚠️ No Google Sheets credentials loaded")
            st.info("Upload your Service Account JSON in the sidebar to connect")
    
    st.markdown("---")
    
    # Display preferences
    st.markdown("### 🎨 Display Preferences")
    with st.expander("Customize Your Experience", expanded=True):
        st.markdown("Coming soon: Theme customization, notification preferences, and more!")
        
        # Placeholder for future settings
        st.checkbox("Enable desktop notifications", value=False, disabled=True)
        st.checkbox("Dark mode", value=False, disabled=True)
        st.selectbox("Emails per page", [10, 25, 50, 100], index=1, disabled=True)
    
    st.markdown("---")
    
    # Data management
    st.markdown("### 🗄️ Data Management")
    with st.expander("Manage Your Data", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                credentials_dict = st.session_state.get('credentials', None)
                if credentials_dict:
                    gc = authenticate_gsheets(credentials_dict)
                    if gc:
                        st.session_state['df'] = load_data_from_gsheet(gc, SHEET_ID)
                        st.success("Data refreshed!")
                        st.rerun()
                else:
                    st.error("No credentials available")
        
        with col2:
            if st.button("🗑️ Clear Drafts", use_container_width=True):
                st.session_state['drafts'] = []
                st.success("Drafts cleared!")
                st.rerun()
        
        with col3:
            if st.button("📥 Export Data", use_container_width=True, disabled=True):
                st.info("Export feature coming soon!")
    
    st.markdown("---")
    
    # About
    st.markdown("### ℹ️ About InboxKeep Pro")
    st.markdown("""
    **Version:** 2.0 Enhanced
    
    **Features:**
    - 📨 Advanced email management with AI-powered suggestions
    - 📊 Comprehensive analytics and insights
    - 👥 Contact management system
    - 📝 Draft management with templates
    - 🔄 Google Sheets integration
    - 📤 Real email sending via Gmail SMTP
    
    **Created with:** Streamlit, Pandas, Plotly, gspread
    """)

# ... existing code ...

def main():
    """Main application function for InboxKeep Pro."""
    
    st.set_page_config(
        page_title="InboxKeep Pro - Advanced Email Management",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_custom_css()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'inbox'
    if 'selected_email' not in st.session_state:
        st.session_state['selected_email'] = None
    if 'use_ai_reply' not in st.session_state:
        st.session_state['use_ai_reply'] = False
    if 'df' not in st.session_state:
        st.session_state['df'] = generate_mock_data(num_emails=25)
    if 'credentials' not in st.session_state:
        st.session_state['credentials'] = None
    if 'drafts' not in st.session_state:
        st.session_state['drafts'] = []
    if 'sent_items' not in st.session_state:
        st.session_state['sent_items'] = []
    
    # Sidebar for credentials
    with st.sidebar:
        st.markdown("## 🔐 Service Account JSON")
        st.markdown("Upload your Google Service Account JSON credentials to connect to Google Sheets and enable full functionality.")
        
        uploaded_json_file = st.file_uploader(
            "Upload JSON File",
            type=['json'],
            help="Upload your Google Cloud Service Account JSON file"
        )
        
        if uploaded_json_file is not None:
            try:
                credentials_dict = json.load(uploaded_json_file)
                st.session_state['credentials'] = credentials_dict
                
                st.success("✅ Credentials loaded successfully!")
                
                if 'client_email' in credentials_dict:
                    st.info(f"Service Account: {credentials_dict['client_email']}")
                
                gc = authenticate_gsheets(credentials_dict)
                if gc:
                    st.success("✅ Connected to Google Sheets!")
                    
                    with st.spinner("Loading data from Google Sheets..."):
                        st.session_state['df'] = load_data_from_gsheet(gc, SHEET_ID)
                        st.success(f"Loaded {len(st.session_state['df'])} emails from Google Sheets!")
                else:
                    st.warning("Using mock data - could not connect to Google Sheets")
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid Service Account JSON.")
            except Exception as e:
                st.error(f"Error processing credentials: {str(e)}")
        else:
            st.info("📝 No credentials loaded. Using mock data for demonstration.")
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("💾 Drafts", len(st.session_state.get('drafts', [])))
        st.metric("📤 Sent Items", len(st.session_state.get('sent_items', [])))
        st.metric("📧 Total Emails", len(st.session_state.get('df', [])))
    
    # Main content
    st.title("📧 InboxKeep Pro: Advanced Email Management")
    st.markdown("A comprehensive email management application with AI-powered suggestions, analytics, and Google Sheets integration.")
    st.markdown("---")
    
    # <CHANGE> Enhanced horizontal navigation with icons and Analytics + Contacts pages
    st.markdown('<div class="horizontal-menu">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("📨 Inbox", use_container_width=True, type="primary" if st.session_state['page'] == 'inbox' else "secondary"):
            st.session_state['page'] = 'inbox'
            st.session_state['selected_email'] = None
            st.rerun()
    with col2:
        if st.button("✍️ Compose", use_container_width=True, type="primary" if st.session_state['page'] == 'compose' else "secondary"):
            st.session_state['page'] = 'compose'
            st.session_state['selected_email'] = None
            st.rerun()
    with col3:
        if st.button("📝 Drafts", use_container_width=True, type="primary" if st.session_state['page'] == 'drafts' else "secondary"):
            st.session_state['page'] = 'drafts'
            st.rerun()
    with col4:
        if st.button("📤 Sent", use_container_width=True, type="primary" if st.session_state['page'] == 'sent' else "secondary"):
            st.session_state['page'] = 'sent'
            st.rerun()
    with col5:
        if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state['page'] == 'analytics' else "secondary"):
            st.session_state['page'] = 'analytics'
            st.rerun()
    with col6:
        if st.button("👥 Contacts", use_container_width=True, type="primary" if st.session_state['page'] == 'contacts' else "secondary"):
            st.session_state['page'] = 'contacts'
            st.rerun()
    with col7:
        if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state['page'] == 'settings' else "secondary"):
            st.session_state['page'] = 'settings'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Page routing
    credentials_dict = st.session_state.get('credentials', None)
    
    if st.session_state['page'] == 'inbox':
        render_inbox(st.session_state['df'], credentials_dict)
    elif st.session_state['page'] == 'compose':
        render_compose(st.session_state.get('selected_email'))
    elif st.session_state['page'] == 'drafts':
        render_drafts()
    elif st.session_state['page'] == 'sent':
        render_sent()
    elif st.session_state['page'] == 'analytics':
        render_analytics(st.session_state['df'])
    elif st.session_state['page'] == 'contacts':
        render_contacts(st.session_state['df'])
    elif st.session_state['page'] == 'settings':
        render_settings()

if __name__ == "__main__":
    main()
