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
import base64

# ------------------------------
# 🔐 AUTHENTICATION & API SETUP
# ------------------------------

SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
SCOPES_SHEETS = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"

def get_persistent_credentials():
    """Get credentials from Streamlit secrets or session state."""
    if 'credentials' in st.secrets:
        try:
            return dict(st.secrets['credentials'])
        except:
            pass
    if 'stored_credentials' in st.session_state:
        return st.session_state['stored_credentials']
    return None

def initialize_gmail_service(credentials_dict):
    """Initialize Gmail API service."""
    try:
        from googleapiclient.discovery import build
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES_GMAIL)
        service = build('gmail', 'v1', credentials=credentials)
        return service, True, "Gmail API authenticated successfully!"
    except Exception as e:
        return None, False, f"Gmail API authentication failed: {str(e)}"

def initialize_sheets_service(credentials_dict):
    """Initialize Google Sheets service."""
    try:
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES_SHEETS)
        gc = gspread.authorize(credentials)
        return gc, True, "Google Sheets authenticated successfully!"
    except Exception as e:
        return None, False, f"Google Sheets authentication failed: {str(e)}"

def send_email_via_gmail_api(gmail_service, to_email, subject, body_html, from_email):
    """Send email using Gmail API."""
    try:
        message = MIMEMultipart('alternative')
        message['To'] = to_email
        message['From'] = from_email
        message['Subject'] = subject
        html_part = MIMEText(body_html, 'html')
        message.attach(html_part)
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw_message}
        sent_message = gmail_service.users().messages().send(userId='me', body=body).execute()
        return True, f"Email sent successfully! Message ID: {sent_message['id']}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def send_via_smtp(smtp_settings, to_email, subject, body_html, from_name="InboxKeep User"):
    """Send email using SMTP."""
    try:
        smtp_server = smtp_settings.get('server', 'smtp.gmail.com')
        smtp_port = smtp_settings.get('port', 587)
        smtp_user = smtp_settings.get('user', '')
        smtp_password = smtp_settings.get('password', '')
        
        if not smtp_user or not smtp_password:
            return False, "SMTP credentials not configured"
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully via SMTP!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# ------------------------------
# 🎨 PAGE CONFIGURATION
# ------------------------------

st.set_page_config(
    page_title="InboxKeep Pro - Email Management Suite",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# 📧 EMAIL TEMPLATES
# ------------------------------

EMAIL_TEMPLATES = {
    "professional_reply": {
        "name": "Professional Reply",
        "icon": "💼",
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
        "icon": "😊",
        "description": "A warm, approachable response for casual communications",
        "template": """Hi {sender_name},

Thanks for reaching out about {subject}!

{custom_content}

Let me know if you need anything else!

Best,
{your_name}"""
    },
    "quick_acknowledge": {
        "name": "Quick Acknowledgment",
        "icon": "✅",
        "description": "Brief response to acknowledge receipt",
        "template": """Hi {sender_name},

I've received your email about {subject}. I'll get back to you with a detailed response soon.

Thanks,
{your_name}"""
    },
    "meeting_request": {
        "name": "Meeting Request",
        "icon": "📅",
        "description": "Request a meeting or call",
        "template": """Dear {sender_name},

Thank you for your email regarding {subject}.

I'd like to discuss this further. Would you be available for a meeting? Please let me know your availability.

Best regards,
{your_name}"""
    },
    "follow_up": {
        "name": "Follow-up",
        "icon": "🔄",
        "description": "Follow up on a previous conversation",
        "template": """Hi {sender_name},

I wanted to follow up on {subject}.

{custom_content}

Looking forward to your response.

Best,
{your_name}"""
    }
}

# ------------------------------
# 🎯 SAMPLE EMAIL DATA
# ------------------------------

def generate_sample_emails():
    """Generate sample email data for demo purposes."""
    sample_emails = [
        {
            "id": "email_001",
            "sender_name": "Sarah Johnson",
            "sender_email": "sarah.johnson@company.com",
            "subject": "Q4 Budget Review Meeting",
            "summary": "Request to schedule a meeting to review the Q4 budget proposals and discuss resource allocation for the upcoming projects.",
            "priority": "high",
            "department": "Finance",
            "received_date": "2024-01-15 09:30 AM",
            "read_status": "unread",
            "has_attachment": True,
            "ai_suggestion": "This is a high-priority financial matter. Suggest scheduling the meeting within the next 2 business days and preparing budget reports beforehand."
        },
        {
            "id": "email_002",
            "sender_name": "Michael Chen",
            "sender_email": "m.chen@techcorp.com",
            "subject": "Product Demo Request",
            "summary": "Interested in scheduling a product demonstration for their team of 15 members. They're evaluating solutions for their upcoming project launch.",
            "priority": "medium",
            "department": "Sales",
            "received_date": "2024-01-15 08:45 AM",
            "read_status": "read",
            "has_attachment": False,
            "ai_suggestion": "Good sales opportunity. Respond promptly with available demo slots and prepare a customized presentation highlighting features relevant to their team size."
        },
        {
            "id": "email_003",
            "sender_name": "Emily Rodriguez",
            "sender_email": "emily.r@startup.io",
            "subject": "Partnership Opportunity",
            "summary": "Proposing a strategic partnership between our companies. They see synergies in our product offerings and want to explore collaboration options.",
            "priority": "high",
            "department": "Business Development",
            "received_date": "2024-01-14 04:20 PM",
            "read_status": "read",
            "has_attachment": True,
            "ai_suggestion": "Strategic importance - forward to business development team. Schedule an exploratory call to understand their vision and assess alignment with company goals."
        },
        {
            "id": "email_004",
            "sender_name": "David Kim",
            "sender_email": "david.kim@agency.com",
            "subject": "Invoice #INV-2024-0142",
            "summary": "Invoice for consulting services rendered in January. Payment terms: Net 30 days. Total amount: $5,250.00.",
            "priority": "medium",
            "department": "Accounting",
            "received_date": "2024-01-14 02:15 PM",
            "read_status": "unread",
            "has_attachment": True,
            "ai_suggestion": "Standard invoice processing. Forward to accounting department for verification and payment processing within the 30-day term."
        },
        {
            "id": "email_005",
            "sender_name": "Jennifer Martinez",
            "sender_email": "j.martinez@nonprofit.org",
            "subject": "Thank You & Event Recap",
            "summary": "Expressing gratitude for sponsoring their recent charity event. Sharing impact metrics and photos from the successful event.",
            "priority": "low",
            "department": "Corporate Social Responsibility",
            "received_date": "2024-01-13 11:00 AM",
            "read_status": "read",
            "has_attachment": True,
            "ai_suggestion": "Positive relationship building. A brief acknowledgment response would strengthen the partnership. Consider sharing on company social media."
        }
    ]
    return sample_emails

# ------------------------------
# 💾 SESSION STATE INITIALIZATION
# ------------------------------

if 'emails' not in st.session_state:
    st.session_state.emails = generate_sample_emails()

if 'drafts' not in st.session_state:
    st.session_state.drafts = []

if 'sent_emails' not in st.session_state:
    st.session_state.sent_emails = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

if 'gmail_service' not in st.session_state:
    st.session_state.gmail_service = None

if 'sheets_service' not in st.session_state:
    st.session_state.sheets_service = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ------------------------------
# 🎨 SIDEBAR - DERIVE JSON
# ------------------------------

st.sidebar.title("🔧 Derive JSON Configuration")
st.sidebar.markdown("---")

st.sidebar.subheader("📝 Service Account JSON")
st.sidebar.markdown("Paste your Google Service Account JSON credentials below:")

json_input = st.sidebar.text_area(
    "JSON Credentials",
    height=200,
    placeholder='{\n  "type": "service_account",\n  "project_id": "your-project",\n  ...\n}',
    help="Paste the entire JSON file content from your Google Cloud Service Account"
)

if st.sidebar.button("🔐 Authenticate Services", use_container_width=True):
    if json_input.strip():
        try:
            credentials_dict = json.loads(json_input)
            st.session_state.stored_credentials = credentials_dict
            
            # Initialize Gmail Service
            gmail_service, gmail_success, gmail_msg = initialize_gmail_service(credentials_dict)
            if gmail_success:
                st.session_state.gmail_service = gmail_service
                st.sidebar.success(gmail_msg)
            else:
                st.sidebar.error(gmail_msg)
            
            # Initialize Sheets Service
            sheets_service, sheets_success, sheets_msg = initialize_sheets_service(credentials_dict)
            if sheets_success:
                st.session_state.sheets_service = sheets_service
                st.sidebar.success(sheets_msg)
            else:
                st.sidebar.error(sheets_msg)
            
            if gmail_success and sheets_success:
                st.session_state.authenticated = True
                st.sidebar.success("✅ All services authenticated!")
                
        except json.JSONDecodeError:
            st.sidebar.error("❌ Invalid JSON format. Please check your credentials.")
        except Exception as e:
            st.sidebar.error(f"❌ Authentication error: {str(e)}")
    else:
        st.sidebar.warning("⚠️ Please paste your JSON credentials first.")

st.sidebar.markdown("---")

# Authentication Status
st.sidebar.subheader("🔑 Authentication Status")
if st.session_state.authenticated:
    st.sidebar.success("✅ Authenticated")
    st.sidebar.info(f"Gmail API: {'✓' if st.session_state.gmail_service else '✗'}")
    st.sidebar.info(f"Sheets API: {'✓' if st.session_state.sheets_service else '✗'}")
else:
    st.sidebar.warning("🔒 Not authenticated")

st.sidebar.markdown("---")

# Quick Stats in Sidebar
st.sidebar.subheader("📊 Quick Stats")
st.sidebar.metric("Total Emails", len(st.session_state.emails))
st.sidebar.metric("Unread", len([e for e in st.session_state.emails if e['read_status'] == 'unread']))
st.sidebar.metric("Drafts", len(st.session_state.drafts))
st.sidebar.metric("Sent", len(st.session_state.sent_emails))

# ------------------------------
# 🎨 CUSTOM CSS
# ------------------------------

st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    }
    
    .block-container {
        padding-top: 2rem;
    }
    
    /* Stats cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 900;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Email cards custom styling */
    div[data-testid="stExpander"] {
        background: white;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 📱 MAIN NAVIGATION
# ------------------------------

st.title("📧 InboxKeep Pro - Email Management Suite")
st.markdown("### Intelligent Email Management & Response System")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📬 Dashboard", "✉️ Compose", "📤 Sent", "📝 Drafts", "⚙️ Settings"])

# ------------------------------
# 📬 DASHBOARD TAB
# ------------------------------

with tab1:
    st.header("📊 Email Dashboard")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emails = len(st.session_state.emails)
        st.metric("Total Emails", total_emails, delta=None)
    
    with col2:
        unread_count = len([e for e in st.session_state.emails if e['read_status'] == 'unread'])
        st.metric("Unread", unread_count, delta=f"+{unread_count}")
    
    with col3:
        high_priority = len([e for e in st.session_state.emails if e['priority'] == 'high'])
        st.metric("High Priority", high_priority, delta=f"{high_priority} urgent")
    
    with col4:
        with_attachments = len([e for e in st.session_state.emails if e['has_attachment']])
        st.metric("With Attachments", with_attachments, delta=None)
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filter Emails")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    
    with filter_col2:
        status_filter = st.selectbox("Status", ["All", "Unread", "Read"])
    
    with filter_col3:
        attachment_filter = st.selectbox("Attachments", ["All", "With Attachments", "No Attachments"])
    
    # Filter emails
    filtered_emails = st.session_state.emails.copy()
    
    if priority_filter != "All":
        filtered_emails = [e for e in filtered_emails if e['priority'].lower() == priority_filter.lower()]
    
    if status_filter != "All":
        filtered_emails = [e for e in filtered_emails if e['read_status'].lower() == status_filter.lower()]
    
    if attachment_filter == "With Attachments":
        filtered_emails = [e for e in filtered_emails if e['has_attachment']]
    elif attachment_filter == "No Attachments":
        filtered_emails = [e for e in filtered_emails if not e['has_attachment']]
    
    st.markdown("---")
    
    # Display emails
    st.subheader(f"📥 Inbox ({len(filtered_emails)} emails)")
    
    for email in filtered_emails:
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_emoji = "📭" if email['read_status'] == 'unread' else "📬"
        attachment_emoji = "📎" if email['has_attachment'] else ""
        
        with st.expander(f"{status_emoji} {priority_emoji[email['priority']]} **{email['subject']}** - {email['sender_name']} {attachment_emoji}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**From:** {email['sender_name']} ({email['sender_email']})")
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown(f"**Department:** {email['department']}")
                st.markdown(f"**Received:** {email['received_date']}")
                st.markdown("---")
                st.markdown(f"**Summary:** {email['summary']}")
                st.info(f"🤖 **AI Suggestion:** {email['ai_suggestion']}")
            
            with col2:
                st.markdown("**Quick Actions:**")
                if st.button("✏️ Reply", key=f"reply_{email['id']}", use_container_width=True):
                    st.session_state.reply_to_email = email
                    st.session_state.current_page = "Compose"
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{email['id']}", use_container_width=True):
                    st.session_state.emails = [e for e in st.session_state.emails if e['id'] != email['id']]
                    st.success("Email deleted!")
                    st.rerun()
                
                if email['read_status'] == 'unread':
                    if st.button("✓ Mark Read", key=f"mark_{email['id']}", use_container_width=True):
                        email['read_status'] = 'read'
                        st.success("Marked as read!")
                        st.rerun()

# ------------------------------
# ✉️ COMPOSE TAB
# ------------------------------

with tab2:
    st.header("✉️ Compose Email")
    
    # Check if replying to an email
    reply_mode = 'reply_to_email' in st.session_state
    
    if reply_mode:
        original_email = st.session_state.reply_to_email
        st.info(f"📧 Replying to: **{original_email['subject']}** from **{original_email['sender_name']}**")
        default_to = original_email['sender_email']
        default_subject = f"Re: {original_email['subject']}"
    else:
        default_to = ""
        default_subject = ""
    
    # Email form
    col1, col2 = st.columns(2)
    
    with col1:
        to_email = st.text_input("To:", value=default_to)
        subject = st.text_input("Subject:", value=default_subject)
    
    with col2:
        from_email = st.text_input("From:", value="your-email@example.com")
        your_name = st.text_input("Your Name:", value="Your Name")
    
    st.markdown("---")
    
    # Template selection
    st.subheader("📝 Select Email Template")
    
    template_cols = st.columns(len(EMAIL_TEMPLATES))
    selected_template = None
    
    for idx, (template_key, template_data) in enumerate(EMAIL_TEMPLATES.items()):
        with template_cols[idx]:
            if st.button(
                f"{template_data['icon']}\n{template_data['name']}",
                key=f"template_{template_key}",
                use_container_width=True,
                help=template_data['description']
            ):
                selected_template = template_key
                st.session_state.selected_template = template_key
    
    # Show selected template
    if 'selected_template' in st.session_state:
        template = EMAIL_TEMPLATES[st.session_state.selected_template]
        st.success(f"✅ Template selected: **{template['name']}**")
        
        # Custom content input
        custom_content = st.text_area(
            "Custom Content:",
            height=200,
            placeholder="Enter your custom message here...",
            help="This will replace the {custom_content} placeholder in the template"
        )
        
        # Generate email body
        if reply_mode:
            sender_name = original_email['sender_name']
            email_subject = original_email['subject']
        else:
            sender_name = to_email.split('@')[0].replace('.', ' ').title() if '@' in to_email else "Recipient"
            email_subject = subject
        
        email_body = template['template'].format(
            sender_name=sender_name,
            subject=email_subject,
            custom_content=custom_content if custom_content else "[Your detailed response here]",
            your_name=your_name
        )
        
        # Preview
        st.markdown("---")
        st.subheader("👁️ Email Preview")
        
        with st.container():
            st.markdown("**Preview:**")
            st.markdown(f"**To:** {to_email}")
            st.markdown(f"**From:** {from_email}")
            st.markdown(f"**Subject:** {subject}")
            st.markdown("---")
            st.markdown(email_body.replace('\n', '<br>'), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📤 Send Email", use_container_width=True, type="primary"):
                if st.session_state.authenticated and st.session_state.gmail_service:
                    success, message = send_email_via_gmail_api(
                        st.session_state.gmail_service,
                        to_email,
                        subject,
                        email_body.replace('\n', '<br>'),
                        from_email
                    )
                    if success:
                        st.success("✅ Email sent successfully!")
                        st.session_state.sent_emails.append({
                            "to": to_email,
                            "subject": subject,
                            "body": email_body,
                            "sent_date": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        })
                        if reply_mode:
                            del st.session_state.reply_to_email
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please authenticate in the sidebar first!")
        
        with action_col2:
            if st.button("💾 Save as Draft", use_container_width=True):
                st.session_state.drafts.append({
                    "to": to_email,
                    "subject": subject,
                    "body": email_body,
                    "template": st.session_state.selected_template,
                    "created_date": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                })
                st.success("✅ Draft saved!")
                if reply_mode:
                    del st.session_state.reply_to_email
        
        with action_col3:
            if st.button("🔄 Clear Form", use_container_width=True):
                if 'selected_template' in st.session_state:
                    del st.session_state.selected_template
                if reply_mode:
                    del st.session_state.reply_to_email
                st.rerun()

# ------------------------------
# 📤 SENT TAB
# ------------------------------

with tab3:
    st.header("📤 Sent Emails")
    
    if st.session_state.sent_emails:
        for idx, sent_email in enumerate(st.session_state.sent_emails):
            with st.expander(f"✅ **{sent_email['subject']}** - To: {sent_email['to']}"):
                st.markdown(f"**To:** {sent_email['to']}")
                st.markdown(f"**Subject:** {sent_email['subject']}")
                st.markdown(f"**Sent:** {sent_email['sent_date']}")
                st.markdown("---")
                st.markdown("**Message:**")
                st.markdown(sent_email['body'])
    else:
        st.info("📭 No sent emails yet. Compose and send your first email!")

# ------------------------------
# 📝 DRAFTS TAB
# ------------------------------

with tab4:
    st.header("📝 Draft Emails")
    
    if st.session_state.drafts:
        for idx, draft in enumerate(st.session_state.drafts):
            with st.expander(f"📄 **{draft['subject']}** - To: {draft['to']}"):
                st.markdown(f"**To:** {draft['to']}")
                st.markdown(f"**Subject:** {draft['subject']}")
                st.markdown(f"**Created:** {draft['created_date']}")
                st.markdown(f"**Template:** {EMAIL_TEMPLATES[draft['template']]['name']}")
                st.markdown("---")
                st.markdown("**Message:**")
                st.markdown(draft['body'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_draft_{idx}", use_container_width=True):
                        st.info("💡 Tip: Copy the content to the Compose tab to edit")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_draft_{idx}", use_container_width=True):
                        st.session_state.drafts.pop(idx)
                        st.success("Draft deleted!")
                        st.rerun()
    else:
        st.info("📭 No drafts saved. Create a draft from the Compose tab!")

# ------------------------------
# ⚙️ SETTINGS TAB
# ------------------------------

with tab5:
    st.header("⚙️ Settings")
    
    st.subheader("🔧 System Configuration")
    
    # SMTP Settings
    with st.expander("📧 SMTP Settings (Alternative to Gmail API)"):
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        smtp_user = st.text_input("SMTP Username")
        smtp_password = st.text_input("SMTP Password", type="password")
        
        if st.button("💾 Save SMTP Settings"):
            st.session_state.smtp_settings = {
                "server": smtp_server,
                "port": smtp_port,
                "user": smtp_user,
                "password": smtp_password
            }
            st.success("✅ SMTP settings saved!")
    
    # Google Sheets Configuration
    with st.expander("📊 Google Sheets Configuration"):
        sheet_id = st.text_input("Sheet ID", value=SHEET_ID)
        if st.button("💾 Save Sheet ID"):
            st.session_state.sheet_id = sheet_id
            st.success("✅ Sheet ID saved!")
    
    # App Settings
    with st.expander("🎨 App Settings"):
        st.markdown("**Email Display Settings:**")
        emails_per_page = st.slider("Emails per page", 5, 50, 20)
        show_ai_suggestions = st.checkbox("Show AI Suggestions", value=True)
        auto_mark_read = st.checkbox("Auto-mark as read", value=False)
        
        if st.button("💾 Save App Settings"):
            st.session_state.emails_per_page = emails_per_page
            st.session_state.show_ai_suggestions = show_ai_suggestions
            st.session_state.auto_mark_read = auto_mark_read
            st.success("✅ App settings saved!")
    
    # Data Management
    st.markdown("---")
    st.subheader("💾 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset Sample Data", use_container_width=True):
            st.session_state.emails = generate_sample_emails()
            st.success("✅ Sample data reset!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Drafts", use_container_width=True):
            st.session_state.drafts = []
            st.success("✅ All drafts cleared!")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Sent Emails", use_container_width=True):
            st.session_state.sent_emails = []
            st.success("✅ Sent emails cleared!")
            st.rerun()

# ------------------------------
# 📊 FOOTER
# ------------------------------

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 20px;'>
    <p><strong>InboxKeep Pro v1.0</strong> - Intelligent Email Management System</p>
    <p>🔐 Secure • 🤖 AI-Powered • 📊 Analytics-Driven</p>
</div>
""", unsafe_allow_html=True)
