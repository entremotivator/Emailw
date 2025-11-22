import streamlit as st
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ------------------------------
# 🔧 PAGE CONFIGURATION
# ------------------------------
st.set_page_config(
    page_title="InboxKeep Pro - Full Email Suite",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# 🎨 CUSTOM CSS - Enhanced Colorful Card Theme
# ------------------------------
CUSTOM_CSS = """
<style>
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }

    /* Header Styling */
    h1 {
        color: #1e3a8a;
        font-weight: 800;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Stats Cards */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 35px;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        flex: 1;
        box-shadow: 0 8px 25px rgba(30, 58, 138, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 8px solid #60a5fa;
    }
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(30, 58, 138, 0.5);
    }
    .stat-card.teal {
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
        border-left: 8px solid #5eead4;
    }
    .stat-card.purple {
        background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
        border-left: 8px solid #c4b5fd;
    }
    .stat-card.orange {
        background: linear-gradient(135deg, #c2410c 0%, #f97316 100%);
        border-left: 8px solid #fdba74;
    }
    .stat-number {
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 5px;
        line-height: 1;
    }
    .stat-label {
        font-size: 16px;
        opacity: 0.95;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Email Cards */
    .email-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .email-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
        border-color: #3b82f6;
    }
    
    .email-card.priority-high::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #ef4444;
    }
    .email-card.priority-medium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #f59e0b;
    }
    .email-card.priority-low::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #10b981;
    }

    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-left: 15px;
    }
    .sender-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 20px;
        margin-right: 15px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .sender-name {
        font-weight: 700;
        font-size: 18px;
        color: #1f2937;
    }
    .sender-email {
        color: #6b7280;
        font-size: 13px;
    }
    .subject {
        font-size: 20px;
        font-weight: 800;
        color: #111827;
        margin: 10px 0 8px 0;
        line-height: 1.3;
        padding-left: 15px;
    }
    .summary {
        color: #4b5563;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 15px;
        padding-left: 15px;
    }
    .email-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: #9ca3af;
        border-top: 1px solid #f3f4f6;
        padding-top: 10px;
        margin-top: 10px;
        padding-left: 15px;
    }
    .date {
        font-weight: 600;
        color: #3b82f6;
    }
    .tag {
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
    }
    .tag.ai {
        background: #d1fae5;
        color: #065f46;
    }
    .tag.attachment {
        background: #eff6ff;
        color: #1e40af;
    }
    .tag.no-attachment {
        background: #f3f4f6;
        color: #6b7280;
    }

    .ai-reply-preview {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        margin: 10px 0 20px 15px;
        border-radius: 8px;
        font-size: 14px;
        color: #1e3a8a;
        line-height: 1.6;
        box-shadow: 0 1px 5px rgba(59, 130, 246, 0.1);
    }
    .ai-reply-preview strong {
        color: #1e3a8a;
    }

    /* Template Cards */
    .template-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 2px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .template-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    .template-card.selected {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    .template-title {
        font-weight: 700;
        font-size: 18px;
        color: #1f2937;
        margin-bottom: 8px;
    }
    .template-description {
        color: #6b7280;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Draft Card */
    .draft-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #fcd34d;
        border-radius: 14px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(252, 211, 77, 0.3);
        transition: all 0.3s ease;
    }
    .draft-card:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 20px rgba(252, 211, 77, 0.5);
    }
    .draft-badge {
        background: #f59e0b;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
    }

    /* Email Canvas */
    .email-canvas {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        min-height: 400px;
    }
    .email-canvas-header {
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .email-canvas-body {
        font-family: Arial, sans-serif;
        font-size: 15px;
        line-height: 1.8;
        color: #374151;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------
# 📧 EMAIL TEMPLATES
# ------------------------------
EMAIL_TEMPLATES = {
    "professional_reply": {
        "name": "Professional Reply",
        "description": "A formal response suitable for business communications",
        "template": """Dear {sender_name},

Thank you for your email regarding {subject}.

I have carefully reviewed your message and would like to provide the following response:

{custom_content}

Should you have any questions or require further clarification, please do not hesitate to contact me.

Best regards,
{your_name}"""
    },
    "friendly_reply": {
        "name": "Friendly Reply",
        "description": "A warm, approachable response for casual communications",
        "template": """Hi {sender_name},

Thanks for reaching out about {subject}!

{custom_content}

Let me know if you need anything else. Always happy to help!

Cheers,
{your_name}"""
    },
    "meeting_request": {
        "name": "Meeting Request",
        "description": "Request a meeting or discussion",
        "template": """Dear {sender_name},

Thank you for your email regarding {subject}.

I would like to schedule a meeting to discuss this matter in more detail. Would you be available for a call or video conference in the coming days?

{custom_content}

Please let me know your availability, and I will send a calendar invitation.

Best regards,
{your_name}"""
    },
    "follow_up": {
        "name": "Follow-up",
        "description": "Follow up on a previous conversation or request",
        "template": """Hi {sender_name},

I wanted to follow up on your email about {subject}.

{custom_content}

Looking forward to hearing from you soon.

Best,
{your_name}"""
    },
    "acknowledgment": {
        "name": "Quick Acknowledgment",
        "description": "Brief acknowledgment that you received the message",
        "template": """Hi {sender_name},

Thank you for your email about {subject}. I have received your message and will review it carefully.

{custom_content}

I will get back to you shortly with a detailed response.

Best regards,
{your_name}"""
    },
    "thank_you": {
        "name": "Thank You",
        "description": "Express gratitude for assistance or information",
        "template": """Dear {sender_name},

Thank you so much for {subject}.

{custom_content}

Your assistance is greatly appreciated, and I look forward to working with you again.

Warm regards,
{your_name}"""
    }
}

# ------------------------------
# 🔧 UTILITY FUNCTIONS
# ------------------------------
SHEET_ID = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"

def get_initials(name):
    """Extract initials from sender name."""
    if not name or name == "Unknown Sender":
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[0].upper() if name else "?"

def load_data_from_gsheet(credentials_dict):
    """Load data from Google Sheet using provided credentials."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(SHEET_ID).sheet1
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df.columns = [col.lower() for col in df.columns]
        
        if 'priority' not in df.columns:
            df['priority'] = 'medium'
        if 'aireply' not in df.columns:
            df['aireply'] = ''
        if 'department' not in df.columns:
            df['department'] = 'General'
        
        st.success(f"✅ Data loaded from Google Sheet (Sheet ID: {SHEET_ID})")
        return df
        
    except Exception as e:
        st.error(f"Error loading data from Google Sheet: {e}")
        return generate_mock_data(num_emails=0)

def generate_mock_data(num_emails=25):
    """Generates mock email data for demonstration."""
    mock_senders = [
        ("John Smith", "john.s@sales.com", "Sales"),
        ("Sarah Johnson", "sarah.j@marketing.com", "Marketing"),
        ("Mike Chen", "m.chen@tech.io", "IT"),
        ("Lisa Rodriguez", "lisa.r@hr.company.com", "HR"),
        ("David Wilson", "d.wilson@finance.com", "Finance"),
        ("Emily Brown", "emily.b@support.com", "Support"),
        ("Alex Green", "alex.g@product.com", "Product"),
        ("Jessica Lee", "jessica.l@legal.com", "Legal"),
    ]
    
    mock_subjects = [
        "Urgent: Q4 Sales Report Review",
        "Marketing Campaign Results for Q1 Launch",
        "System Maintenance Scheduled for Weekend",
        "Team Building Event - Save the Date",
        "Budget Approval Request for Project Alpha",
        "Follow-up on Customer Ticket #4567",
        "New Feature Proposal: Dark Mode Implementation",
        "Contract Review for Vendor X",
        "Feedback on the latest UI/UX changes",
        "Request for time-off approval",
        "Invoice #2024-987 payment status",
        "Security vulnerability report",
        "Welcome to the new team member!",
        "Quarterly performance review schedule",
        "Important: Policy update on remote work",
    ]
    
    mock_summaries = [
        "The Q4 sales figures are attached for your review. Please provide feedback by EOD.",
        "The campaign exceeded expectations with a 25% increase in engagement. Full report inside.",
        "Server maintenance scheduled this weekend. Expected downtime: 2–4 hours. Details attached.",
        "Annual team building event next month. Please confirm your attendance and dietary restrictions.",
        "Requesting approval for additional project budget. ROI details attached for your consideration.",
        "The customer is still experiencing login issues. Need your technical input on the solution.",
        "Detailed proposal for implementing a dark mode theme across all platforms.",
        "Legal review required for the new vendor contract before signing.",
        "We've gathered user feedback on the recent design changes. Mostly positive, but a few concerns.",
        "Requesting two days off next week for a personal appointment.",
        "Checking on the status of the latest vendor invoice payment.",
        "A critical security flaw was identified in the login module. Immediate action required.",
        "Introducing our newest team member who will be joining the team.",
        "Your QPR meeting is scheduled for next Tuesday. Please prepare your self-assessment.",
        "New guidelines for remote work eligibility and office attendance.",
    ]
    
    emails = []
    priorities = ["high", "medium", "low"]
    
    for i in range(num_emails):
        sender_name, sender_email, department = random.choice(mock_senders)
        subject = random.choice(mock_subjects)
        summary = random.choice(mock_summaries)
        
        date_offset = random.randint(0, 30)
        date = (datetime.now() - pd.Timedelta(days=date_offset)).strftime("%Y-%m-%d")
        
        has_attachment = random.choice(["Yes", "No"])
        has_ai_reply = random.choice([True, False, False])
        priority = random.choice(priorities)
        
        ai_reply = ""
        if has_ai_reply:
            ai_reply = f"""Dear {sender_name},

Thank you for your email regarding {subject}. I have reviewed the summary and the proposed next steps.

I suggest we proceed with the following action: [Specific AI-suggested action based on the content].

I will follow up with a detailed response shortly.

Best regards"""
        
        emails.append({
            "sender name": sender_name,
            "sender email": sender_email,
            "subject": subject,
            "summary": summary,
            "date": date,
            "attachment": has_attachment,
            "aireply": ai_reply,
            "department": department,
            "priority": priority
        })
        
    return pd.DataFrame(emails)

# ------------------------------
# 📤 EMAIL SENDING FUNCTION
# ------------------------------
def send_real_email(smtp_settings, to_email, subject, body_html, from_name="InboxKeep User"):
    """Send a real email using SMTP settings."""
    try:
        smtp_server = smtp_settings.get('server', 'smtp.gmail.com')
        smtp_port = smtp_settings.get('port', 587)
        smtp_user = smtp_settings.get('user', '')
        smtp_password = smtp_settings.get('password', '')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML body
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully!"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# ------------------------------
# 🎨 UI COMPONENTS
# ------------------------------
def display_stats(df):
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    ai_replies = df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"])).sum()
    with_attachments = df[df['attachment'].str.lower().isin(['yes', 'true', '1'])].shape[0]
    high_priority = df[df['priority'] == 'high'].shape[0]
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{total_emails}</div>
            <div class="stat-label">📧 Total Emails</div>
        </div>
        <div class="stat-card teal">
            <div class="stat-number">{ai_replies}</div>
            <div class="stat-label">🤖 AI Replies Ready</div>
        </div>
        <div class="stat-card purple">
            <div class="stat-number">{high_priority}</div>
            <div class="stat-label">🔥 High Priority</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{with_attachments}</div>
            <div class="stat-label">📎 With Attachments</div>
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
            <div class="date">📅 {formatted_date} | 🏢 {department} | Priority: {priority.upper()}</div>
            <div>{ai_tag} {attachment_tag}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        if st.button("✉️ Reply", key=f"reply_{index}", use_container_width=True):
            st.session_state['selected_email'] = email_data
            st.session_state['mode'] = 'compose'
            st.session_state['use_ai_reply'] = False
            st.session_state['use_template'] = False
            st.rerun()
    with col2:
        if st.button("🤖 Use AI Reply", key=f"ai_reply_{index}", disabled=not has_ai_reply, use_container_width=True, type="primary"):
            st.session_state['selected_email'] = email_data
            st.session_state['mode'] = 'compose'
            st.session_state['use_ai_reply'] = True
            st.session_state['use_template'] = False
            st.rerun()
    with col3:
        if st.button("📝 Use Template", key=f"template_{index}", use_container_width=True):
            st.session_state['selected_email'] = email_data
            st.session_state['mode'] = 'compose'
            st.session_state['use_template'] = True
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col4:
        if st.button("✅ Archive", key=f"archive_{index}", use_container_width=True):
            st.toast(f"Archived email from {sender_name}!", icon="✅")
    
    st.markdown("---")

def render_template_selector(email_data):
    """Render template selection UI."""
    st.markdown("### 📝 Choose an Email Template")
    
    selected_template = st.session_state.get('selected_template', None)
    
    for template_key, template_data in EMAIL_TEMPLATES.items():
        is_selected = selected_template == template_key
        card_class = "template-card selected" if is_selected else "template-card"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="template-title">{template_data['name']}</div>
            <div class="template-description">{template_data['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select {template_data['name']}", key=f"select_template_{template_key}", use_container_width=True):
            st.session_state['selected_template'] = template_key
            st.rerun()
    
    if selected_template:
        template = EMAIL_TEMPLATES[selected_template]['template']
        sender_name = email_data.get('sender name', 'Unknown') if email_data else 'Recipient'
        subject = email_data.get('subject', 'your email') if email_data else 'your inquiry'
        
        custom_content = st.text_area(
            "Add your custom content:",
            height=150,
            placeholder="Enter the main content of your email here...",
            key="template_custom_content"
        )
        
        your_name = st.text_input("Your name:", value="", placeholder="Enter your name")
        
        if custom_content and your_name:
            filled_template = template.format(
                sender_name=sender_name,
                subject=subject,
                custom_content=custom_content,
                your_name=your_name
            )
            
            st.markdown("### 📧 Email Preview")
            st.markdown(f"""
            <div class="email-canvas">
                <div class="email-canvas-body">
                    {filled_template.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            return filled_template
    
    return None

def render_compose(email_data=None):
    """Renders the compose page with templates and email canvas."""
    st.markdown("## ✉️ Compose Email")
    
    # Initialize SMTP settings in session state if not present
    if 'smtp_settings' not in st.session_state:
        st.session_state['smtp_settings'] = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'user': '',
            'password': ''
        }
    
    if email_data:
        st.info(f"**Replying to:** {email_data.get('sender name', 'Unknown')} ({email_data.get('sender email', '')})")
        st.markdown(f"**Original Subject:** {email_data.get('subject', 'No Subject')}")
        
        reply_subject = f"Re: {email_data.get('subject', '')}"
        recipient = email_data.get('sender email', '')
        
        if st.session_state.get('use_ai_reply', False):
            ai_reply_body = email_data.get('aireply', '')
            initial_body = ai_reply_body if ai_reply_body else ""
            use_template_mode = False
        elif st.session_state.get('use_template', False):
            initial_body = ""
            use_template_mode = True
        else:
            initial_body = ""
            use_template_mode = False
    else:
        st.info("Composing a new email.")
        reply_subject = ""
        recipient = ""
        initial_body = ""
        use_template_mode = st.session_state.get('use_template', False)
    
    # SMTP Configuration Expander
    with st.expander("⚙️ SMTP Email Settings (Configure to send real emails)", expanded=False):
        st.markdown("Configure your SMTP settings to send real emails. For Gmail, use an App Password.")
        
        col1, col2 = st.columns(2)
        with col1:
            smtp_server = st.text_input("SMTP Server:", value=st.session_state['smtp_settings']['server'])
            smtp_user = st.text_input("Email Address:", value=st.session_state['smtp_settings']['user'])
        with col2:
            smtp_port = st.number_input("SMTP Port:", value=st.session_state['smtp_settings']['port'], min_value=1, max_value=65535)
            smtp_password = st.text_input("Password:", value=st.session_state['smtp_settings']['password'], type="password")
        
        if st.button("💾 Save SMTP Settings"):
            st.session_state['smtp_settings'] = {
                'server': smtp_server,
                'port': smtp_port,
                'user': smtp_user,
                'password': smtp_password
            }
            st.success("SMTP settings saved!")
    
    # Template Mode
    if use_template_mode:
        template_body = render_template_selector(email_data)
        
        if template_body:
            to_address = st.text_input("To:", value=recipient)
            subject = st.text_input("Subject:", value=reply_subject)
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("📤 Send Email", use_container_width=True, type="primary"):
                    if to_address and subject and template_body:
                        # Check if SMTP is configured
                        if st.session_state['smtp_settings']['user'] and st.session_state['smtp_settings']['password']:
                            success, message = send_real_email(
                                st.session_state['smtp_settings'],
                                to_address,
                                subject,
                                template_body.replace('\n', '<br>')
                            )
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                                time.sleep(2)
                                st.session_state['mode'] = 'inbox'
                                st.session_state['selected_email'] = None
                                st.session_state['use_template'] = False
                                st.session_state['selected_template'] = None
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.warning("⚠️ SMTP not configured. Configure SMTP settings above to send real emails.")
                            st.info(f"📧 Email would be sent to: {to_address}")
                    else:
                        st.error("Please fill in all fields before sending.")
            
            with col2:
                if st.button("📋 Save as Draft", use_container_width=True):
                    if 'drafts' not in st.session_state:
                        st.session_state['drafts'] = []
                    
                    draft = {
                        'original_email': email_data,
                        'to': to_address,
                        'subject': subject,
                        'body': template_body,
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state['drafts'].append(draft)
                    st.success("📋 Draft saved!")
                    time.sleep(1)
                    st.session_state['mode'] = 'drafts'
                    st.session_state['use_template'] = False
                    st.session_state['selected_template'] = None
                    st.rerun()
    
    # Standard Compose Mode
    else:
        with st.form("compose_form"):
            to_address = st.text_input("To:", value=recipient)
            subject = st.text_input("Subject:", value=reply_subject)
            
            # Email Canvas
            st.markdown("### 📝 Email Body")
            body = st.text_area("", value=initial_body, height=400, key="email_body")
            
            # Preview
            st.markdown("### 👁️ Live Preview")
            st.markdown(f"""
            <div class="email-canvas">
                <div class="email-canvas-header">
                    <strong>To:</strong> {to_address if to_address else '(recipient)'}<br>
                    <strong>Subject:</strong> {subject if subject else '(no subject)'}
                </div>
                <div class="email-canvas-body">
                    {body.replace(chr(10), '<br>') if body else '(email body)'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                send_button = st.form_submit_button("📤 Send Email", use_container_width=True, type="primary")
            with col2:
                draft_button = st.form_submit_button("📋 Save Draft", use_container_width=True)
            
            if send_button:
                if to_address and subject and body:
                    # Check if SMTP is configured
                    if st.session_state['smtp_settings']['user'] and st.session_state['smtp_settings']['password']:
                        success, message = send_real_email(
                            st.session_state['smtp_settings'],
                            to_address,
                            subject,
                            body.replace('\n', '<br>')
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            time.sleep(2)
                            st.session_state['mode'] = 'inbox'
                            st.session_state['selected_email'] = None
                            st.session_state['use_ai_reply'] = False
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("⚠️ SMTP not configured. Email saved as draft instead.")
                        st.info(f"📧 Configure SMTP settings to send to: {to_address}")
                else:
                    st.error("Please fill in all fields before sending.")
            
            if draft_button:
                if 'drafts' not in st.session_state:
                    st.session_state['drafts'] = []
                
                draft = {
                    'original_email': email_data,
                    'to': to_address,
                    'subject': subject,
                    'body': body,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state['drafts'].append(draft)
                st.success("📋 Draft saved!")
                time.sleep(1)
                st.session_state['mode'] = 'drafts'
                st.rerun()
    
    if st.button("⬅️ Back to Inbox"):
        st.session_state['mode'] = 'inbox'
        st.session_state['selected_email'] = None
        st.session_state['use_ai_reply'] = False
        st.session_state['use_template'] = False
        st.session_state['selected_template'] = None
        st.rerun()

def render_drafts():
    """Renders the drafts page with edit and template options."""
    st.markdown("## 📋 Drafts")
    
    if 'drafts' not in st.session_state or len(st.session_state['drafts']) == 0:
        st.info("No drafts saved yet. Compose an email and save it as a draft to see it here!")
        
        if st.button("✉️ Compose New Email"):
            st.session_state['mode'] = 'compose'
            st.session_state['selected_email'] = None
            st.rerun()
        return
    
    st.success(f"You have **{len(st.session_state['drafts'])}** saved draft(s).")
    st.markdown("---")
    
    for idx, draft in enumerate(st.session_state['drafts']):
        st.markdown(f"""
        <div class="draft-card">
            <span class="draft-badge">DRAFT #{idx + 1}</span>
            <h3 style="margin-top: 15px;">{draft.get('subject', 'No Subject')}</h3>
            <p><strong>To:</strong> {draft.get('to', 'N/A')}</p>
            <p><strong>Saved:</strong> {draft.get('timestamp', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"📄 View Draft #{idx + 1} Content"):
            st.markdown(draft.get('body', 'No content'), unsafe_allow_html=False)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✏️ Edit Draft", key=f"edit_draft_{idx}", use_container_width=True):
                st.session_state['editing_draft_index'] = idx
                st.session_state['mode'] = 'edit_draft'
                st.rerun()
        with col2:
            if st.button("📝 Apply Template", key=f"template_draft_{idx}", use_container_width=True):
                st.session_state['editing_draft_index'] = idx
                st.session_state['mode'] = 'template_draft'
                st.rerun()
        with col3:
            if st.button("🗑️ Delete", key=f"delete_draft_{idx}", use_container_width=True):
                st.session_state['drafts'].pop(idx)
                st.toast("Draft deleted!", icon="🗑️")
                st.rerun()
        
        st.markdown("---")
    
    if st.button("⬅️ Back to Inbox"):
        st.session_state['mode'] = 'inbox'
        st.rerun()

def render_edit_draft():
    """Render the draft editing interface."""
    st.markdown("## ✏️ Edit Draft")
    
    draft_idx = st.session_state.get('editing_draft_index', 0)
    draft = st.session_state['drafts'][draft_idx]
    
    st.info(f"Editing Draft #{draft_idx + 1}")
    
    with st.form("edit_draft_form"):
        to_address = st.text_input("To:", value=draft.get('to', ''))
        subject = st.text_input("Subject:", value=draft.get('subject', ''))
        body = st.text_area("Body:", value=draft.get('body', ''), height=400)
        
        st.markdown("### 👁️ Live Preview")
        st.markdown(f"""
        <div class="email-canvas">
            <div class="email-canvas-header">
                <strong>To:</strong> {to_address if to_address else '(recipient)'}<br>
                <strong>Subject:</strong> {subject if subject else '(no subject)'}
            </div>
            <div class="email-canvas-body">
                {body.replace(chr(10), '<br>') if body else '(email body)'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
        with col2:
            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        if send_button:
            if to_address and subject and body:
                if st.session_state['smtp_settings']['user'] and st.session_state['smtp_settings']['password']:
                    success, message = send_real_email(
                        st.session_state['smtp_settings'],
                        to_address,
                        subject,
                        body.replace('\n', '<br>')
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.session_state['drafts'].pop(draft_idx)
                        time.sleep(2)
                        st.session_state['mode'] = 'inbox'
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("⚠️ SMTP not configured.")
            else:
                st.error("Please fill in all fields.")
        
        if save_button:
            st.session_state['drafts'][draft_idx] = {
                'original_email': draft.get('original_email'),
                'to': to_address,
                'subject': subject,
                'body': body,
                'timestamp': datetime.now().isoformat()
            }
            st.success("💾 Draft updated!")
            time.sleep(1)
            st.session_state['mode'] = 'drafts'
            st.rerun()
    
    if st.button("⬅️ Back to Drafts"):
        st.session_state['mode'] = 'drafts'
        st.rerun()

def render_inbox(df, credentials_dict=None):
    """Renders the inbox page with email cards and stats."""
    st.markdown("## 📥 Inbox")
    
    display_stats(df)
    
    st.markdown("---")
    st.markdown(f"### 📬 {len(df)} Email(s)")
    
    if len(df) == 0:
        st.info("No emails to display with the current filters.")
        return
    
    for idx, row in df.iterrows():
        display_email_card(row.to_dict(), idx, credentials_dict)

def main():
    """Main application function."""
    
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'inbox'
    if 'selected_email' not in st.session_state:
        st.session_state['selected_email'] = None
    if 'use_ai_reply' not in st.session_state:
        st.session_state['use_ai_reply'] = False
    if 'use_template' not in st.session_state:
        st.session_state['use_template'] = False
    
    credentials_dict = None

    st.title("📧 InboxKeep Pro: Full Email Suite")
    st.markdown("Complete email management with **real email sending**, **templates**, **AI replies**, and **visual email canvas**.")
    st.markdown("---")
    
    with st.sidebar:
        st.markdown("### ⚙️ Navigation & Configuration")
        
        mode_options = {
            'inbox': "📥 Inbox",
            'compose': "✉️ Compose",
            'drafts': "📋 Drafts"
        }
        
        current_mode = st.radio(
            "Select View:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            key='sidebar_mode_select'
        )
        
        if current_mode != st.session_state['mode']:
            st.session_state['mode'] = current_mode
            st.session_state['selected_email'] = None
            st.rerun()

        st.markdown("---")
        
        st.markdown("#### 🔐 Google Sheets Credentials")
        uploaded_file = st.file_uploader("Upload JSON credentials", type=['json'])
        
        if uploaded_file is not None:
            try:
                credentials_dict = json.load(uploaded_file)
                st.success("✅ Credentials loaded!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                credentials_dict = None
        
        st.markdown("---")
        
        if credentials_dict:
            df = load_data_from_gsheet(credentials_dict)
        else:
            st.warning("Using mock data. Upload credentials for real data.")
            df = generate_mock_data(num_emails=25)
            
        st.session_state['df'] = df
        
        if st.session_state['mode'] == 'inbox':
            st.markdown("#### 🔍 Inbox Filters")
            
            all_departments = ['All'] + sorted(st.session_state['df']['department'].unique().tolist())
            department_filter = st.selectbox("Filter by Department:", all_departments, key='dept_filter')
            
            priority_filter = st.selectbox("Filter by Priority:", ["All", "high", "medium", "low"], key='priority_filter')
            
            sort_option = st.selectbox(
                "Sort by:",
                ["Date (Newest First)", "Date (Oldest First)", "AI Replies First", "Priority (High First)"],
                key='sort_option'
            )
            
            df_filtered = st.session_state['df'].copy()
            
            if department_filter != "All":
                df_filtered = df_filtered[df_filtered['department'] == department_filter]
            
            if priority_filter != "All":
                df_filtered = df_filtered[df_filtered['priority'] == priority_filter]
            
            if sort_option == "Date (Newest First)":
                df_filtered = df_filtered.sort_values('date', ascending=False)
            elif sort_option == "Date (Oldest First)":
                df_filtered = df_filtered.sort_values('date', ascending=True)
            elif sort_option == "AI Replies First":
                df_filtered['has_ai_reply'] = df_filtered['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))
                df_filtered = df_filtered.sort_values(['has_ai_reply', 'date'], ascending=[False, False])
                df_filtered = df_filtered.drop('has_ai_reply', axis=1)
            elif sort_option == "Priority (High First)":
                priority_order = pd.CategoricalDtype(['high', 'medium', 'low'], ordered=True)
                df_filtered['priority'] = df_filtered['priority'].astype(priority_order)
                df_filtered = df_filtered.sort_values(['priority', 'date'], ascending=[True, False])
            
            st.session_state['df_view'] = df_filtered
        
        st.markdown("---")
        st.markdown("#### 📊 Data Source")
        st.info(f"**{len(st.session_state.get('df_view', st.session_state['df']))}** emails displayed")

    if st.session_state['mode'] == 'inbox':
        render_inbox(st.session_state.get('df_view', st.session_state['df']), credentials_dict)
    elif st.session_state['mode'] == 'compose':
        render_compose(st.session_state.get('selected_email'))
    elif st.session_state['mode'] == 'drafts':
        render_drafts()
    elif st.session_state['mode'] == 'edit_draft':
        render_edit_draft()
    elif st.session_state['mode'] == 'template_draft':
        draft_idx = st.session_state.get('editing_draft_index', 0)
        draft = st.session_state['drafts'][draft_idx]
        st.session_state['selected_email'] = draft.get('original_email')
        st.session_state['use_template'] = True
        st.session_state['mode'] = 'compose'
        st.rerun()

if __name__ == "__main__":
    main()
