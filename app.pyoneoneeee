import streamlit as st
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
import re
import random

# ------------------------------
# 🔧 PAGE CONFIGURATION
# ------------------------------
st.set_page_config(
    page_title="InboxKeep Pro - Email Management",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# 🎨 CUSTOM CSS - Enhanced Professional Theme
# ------------------------------
CUSTOM_CSS = """
<style>
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
    }
    
    /* Stats Cards (Dashboard Metrics) */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 35px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        flex: 1;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
    }
    .stat-card.teal {
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
    }
    .stat-card.purple {
        background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
    }
    .stat-card.orange {
        background: linear-gradient(135deg, #ea580c 0%, #fb923c 100%);
    }
    .stat-number {
        font-size: 56px;
        font-weight: 900;
        margin-bottom: 8px;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .stat-label {
        font-size: 18px;
        opacity: 0.95;
        font-weight: 600;
        letter-spacing: 0.8px;
    }

    /* Email Cards (Inbox Items) */
    .email-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .email-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(30, 58, 138, 0.15);
        border-color: #3b82f6;
    }
    
    /* Priority Marker */
    .email-card.priority-high::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 10px;
        height: 100%;
        background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
    }
    .email-card.priority-medium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 10px;
        height: 100%;
        background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
    }
    .email-card.priority-low::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 10px;
        height: 100%;
        background: linear-gradient(180deg, #10b981 0%, #059669 100%);
    }

    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 18px;
        padding-left: 20px;
    }
    .sender-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 24px;
        margin-right: 18px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
    }
    .sender-name {
        font-weight: 800;
        font-size: 20px;
        color: #1e293b;
    }
    .sender-email {
        color: #64748b;
        font-size: 14px;
        margin-top: 2px;
    }
    .subject {
        font-size: 24px;
        font-weight: 900;
        color: #0f172a;
        margin: 12px 0 10px 0;
        line-height: 1.3;
        padding-left: 20px;
    }
    .summary {
        color: #334155;
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 18px;
        padding-left: 20px;
    }
    .email-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        color: #475569;
        border-top: 2px solid #f1f5f9;
        padding-top: 14px;
        margin-top: 14px;
        padding-left: 20px;
        font-weight: 600;
    }
    .date {
        font-weight: 700;
        color: #3b82f6;
    }
    .tag {
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        margin-left: 8px;
    }
    .tag.ai {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
    }
    .tag.attachment {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
    }
    .tag.no-attachment {
        background: #f1f5f9;
        color: #64748b;
    }

    /* AI Reply Preview */
    .ai-reply-preview {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 6px solid #3b82f6;
        padding: 20px;
        margin: 14px 0 24px 20px;
        border-radius: 12px;
        font-size: 15px;
        color: #1e293b;
        line-height: 1.7;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
    }
    .ai-reply-preview strong {
        color: #1e3a8a;
        font-size: 16px;
    }

    /* IMPROVED DRAFT CARD - Focus on Draft Content Only */
    .draft-card {
        background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
        border: 3px solid #eab308;
        border-radius: 20px;
        padding: 32px;
        margin: 24px 0;
        box-shadow: 0 8px 24px rgba(234, 179, 8, 0.3);
        transition: all 0.3s ease;
        position: relative;
    }
    .draft-card::before {
        content: '✏️ DRAFT';
        position: absolute;
        top: 16px;
        right: 24px;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }
    .draft-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(234, 179, 8, 0.5);
        border-color: #ca8a04;
    }
    
    /* Draft timestamp badge */
    .draft-timestamp {
        background: rgba(0, 0, 0, 0.1);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        color: #713f12;
        display: inline-block;
        margin-bottom: 20px;
    }
    
    /* Draft subject - Large and prominent */
    .draft-subject {
        font-size: 32px;
        font-weight: 900;
        color: #713f12;
        margin: 16px 0 24px 0;
        line-height: 1.2;
        padding-right: 120px;
    }
    
    /* Draft body display - Clean card with good spacing */
    .draft-body-container {
        background: white;
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 2px solid #fde047;
        min-height: 200px;
    }
    .draft-body-label {
        font-size: 14px;
        font-weight: 800;
        color: #92400e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    .draft-body-content {
        color: #0f172a;
        font-size: 17px;
        line-height: 1.8;
    }
    
    /* Draft metadata - subtle and minimal */
    .draft-meta {
        margin-top: 20px;
        padding-top: 16px;
        border-top: 2px solid #fde047;
        font-size: 14px;
        color: #78716c;
    }
    .draft-meta strong {
        color: #57534e;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------
# 📊 GOOGLE SHEETS INTEGRATION
# ------------------------------
SHEET_ID = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"

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
        
        # Normalize column names
        df.columns = [col.lower().replace(' ', '') for col in df.columns]
        
        # Ensure required columns exist with proper names
        column_mapping = {
            'sendername': 'sender name',
            'senderemail': 'sender email',
            'ai_reply': 'aireply',
            'airply': 'aireply'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Add missing columns with defaults
        if 'priority' not in df.columns:
            df['priority'] = 'medium'
        
        if 'aireply' not in df.columns:
            df['aireply'] = ''
            
        if 'department' not in df.columns:
            df['department'] = 'General'
        
        if 'attachment' not in df.columns:
            df['attachment'] = 'No'
        
        st.success(f"✅ Loaded {len(df)} emails from Google Sheet (Sheet ID: {SHEET_ID})")
        return df
        
    except Exception as e:
        st.error(f"Error loading data from Google Sheet: {e}")
        st.warning("Using mock data as fallback...")
        return generate_mock_data(num_emails=25)

def save_draft(email_data, body, credentials_dict):
    """Save email draft body to the AIreply column in the Google Sheet."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(SHEET_ID).sheet1
        
        if 'drafts' not in st.session_state:
            st.session_state['drafts'] = []
        
        draft = {
            'original_email': email_data,
            'body': body,
            'timestamp': datetime.now().isoformat(),
            'subject': f"Re: {email_data.get('subject', '')}"
        }
        st.session_state['drafts'].append(draft)
        
        st.toast("Draft saved to session state (Google Sheet update skipped in mock-up).", icon="📋")
        
    except Exception as e:
        st.error(f"Error saving draft to Google Sheet: {e}")

# ------------------------------
# 📝 MOCK DATA GENERATION
# ------------------------------

def get_initials(name):
    """Extract initials from sender name."""
    if not name or name == "Unknown Sender":
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[0].upper() if name else "?"

def generate_mock_data(num_emails=25):
    """Generates a longer list of mock email data matching Google Sheets structure."""
    mock_senders = [
        ("Custom All Stars", "customallstars@gmail.com", "Community"),
        ("Blogz Team", "info@blogz.life", "Community"),
        ("John Smith", "john.s@sales.com", "Sales"),
        ("Sarah Johnson", "sarah.j@marketing.com", "Marketing"),
        ("Mike Chen", "m.chen@tech.io", "IT"),
        ("Lisa Rodriguez", "lisa.r@hr.company.com", "HR"),
        ("David Wilson", "d.wilson@finance.com", "Finance"),
        ("Emily Brown", "emily.b@support.com", "Support"),
        ("Alex Green", "alex.g@product.com", "Product"),
        ("Jessica Lee", "jessica.l@legal.com", "Legal"),
        ("Robert Taylor", "robert.t@operations.com", "Operations"),
        ("Maria Garcia", "maria.g@research.com", "Research"),
        ("James Anderson", "james.a@design.com", "Design"),
        ("Linda Martinez", "linda.m@qa.com", "Quality Assurance"),
        ("William Thomas", "william.t@security.com", "Security"),
    ]
    
    example_emails = [
        {
            "sender name": "Custom All Stars",
            "sender email": "customallstars@gmail.com",
            "subject": "ai_systems_checklist",
            "summary": "I'm unable to access external links or content such as the email you referenced. Please provide the text of the email, and I'll be happy to summarize it for you.",
            "date": "2025-10-09",
            "attachment": "No",
            "aireply": "hey there",
            "department": "Community",
            "priority": "high"
        },
        {
            "sender name": "Blogz Team",
            "sender email": "info@blogz.life",
            "subject": "[Blogz- The Blogging Community] A new subscriber has (been) registered!",
            "summary": "New subscriber on Blogz: yaralennon29 (ys4058319@gmail.com).",
            "date": "2025-08-23",
            "attachment": "No",
            "aireply": "who are you",
            "department": "Community",
            "priority": "medium"
        }
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
        "Security vulnerability report - URGENT",
        "Welcome to the new team member!",
        "Quarterly performance review schedule",
        "Important: Policy update on remote work",
        "Project deadline extension request",
        "Client meeting notes and action items",
        "Weekly status report submission",
        "Equipment purchase request approval",
        "Training session scheduled for next week",
        "Office relocation announcement",
        "New employee onboarding checklist",
        "Monthly expense report review",
        "Collaboration opportunity with Partner Co",
        "Year-end bonus and compensation review",
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
        "Introducing our newest team member, Alex Johnson, who will be joining the Engineering team.",
        "Your QPR meeting is scheduled for next Tuesday. Please prepare your self-assessment.",
        "New guidelines for remote work eligibility and office attendance.",
        "Project Alpha deadline needs to be pushed by two weeks due to resource constraints.",
        "Summary of action items from yesterday's client meeting. Please review and confirm.",
        "Weekly team status report is due by Friday EOD. Please submit your updates.",
        "Requesting approval to purchase new laptops for the development team.",
        "Mandatory security training session scheduled for Thursday afternoon.",
        "Office will be moving to a new location next quarter. Details and timeline inside.",
        "Updated onboarding checklist for new hires. Please review and provide feedback.",
        "Monthly expense reports need to be submitted by the end of this week.",
        "Exploring a strategic partnership with TechPartner Inc. Initial proposal attached.",
        "Year-end performance bonuses will be discussed in next week's leadership meeting.",
    ]
    
    ai_reply_templates = [
        "<p>Thank you for your email regarding <strong>{subject}</strong>. I have reviewed the details and will follow up with specific action items by end of day.</p><p>In the meantime, please let me know if you need any additional information.</p><p>Best regards</p>",
        "<p>I appreciate you bringing <strong>{subject}</strong> to my attention. This requires careful consideration and I will provide a comprehensive response within 24 hours.</p><p>Thank you for your patience.</p>",
        "<p>Regarding <strong>{subject}</strong>, I suggest we schedule a brief meeting to discuss this in detail. I have availability tomorrow afternoon or Thursday morning.</p><p>Please let me know what works best for you.</p><p>Best regards</p>",
        "<p>Thank you for the update on <strong>{subject}</strong>. I've reviewed the information and agree with the proposed approach.</p><p>Let's proceed as discussed and reconvene next week to review progress.</p>",
        "<p>I've received your email about <strong>{subject}</strong> and am currently reviewing the attached documents. I should have feedback for you by tomorrow morning.</p><p>Thanks for your thoroughness on this matter.</p>",
    ]
    
    emails = example_emails.copy()
    priorities = ["high", "medium", "low"]
    
    # Generate additional emails
    for i in range(num_emails - len(example_emails)):
        sender_name, sender_email, department = random.choice(mock_senders)
        subject = mock_subjects[i % len(mock_subjects)]
        summary = mock_summaries[i % len(mock_summaries)]
        
        date_offset = random.randint(0, 45)
        date = (datetime.now() - pd.Timedelta(days=date_offset)).strftime("%Y-%m-%d")
        
        has_attachment = random.choice(["Yes", "No"])
        has_ai_reply = random.choice([True, False, False])
        priority = random.choice(priorities)
        
        ai_reply = ""
        if has_ai_reply:
            template = random.choice(ai_reply_templates)
            ai_reply = f"<div style='font-family: Arial, sans-serif;'><p>Dear {sender_name},</p>{template.format(subject=subject)}</div>"
        
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
# 📊 UI RENDERING FUNCTIONS
# ------------------------------

def display_stats(df):
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    with_attachments = df[df['attachment'].str.lower().isin(['yes', 'true', '1'])].shape[0]
    high_priority = df[df['priority'] == 'high'].shape[0]
    ai_replies_ready = df[df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))].shape[0]
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{total_emails}</div>
            <div class="stat-label">📧 Total Emails</div>
        </div>
        <div class="stat-card teal">
            <div class="stat-number">{with_attachments}</div>
            <div class="stat-label">📎 With Attachments</div>
        </div>
        <div class="stat-card purple">
            <div class="stat-number">{high_priority}</div>
            <div class="stat-label">🔥 High Priority</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{ai_replies_ready}</div>
            <div class="stat-label">🤖 AI Replies Ready</div>
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
        if st.button("📋 Save as Draft", key=f"draft_{index}", use_container_width=True):
            if 'drafts' not in st.session_state:
                st.session_state['drafts'] = []
            
            draft = {
                'sender name': sender_name,
                'sender email': sender_email,
                'subject': f"Re: {subject}",
                'body': ai_reply if ai_reply else f"Replying to: {summary[:100]}...",
                'timestamp': datetime.now().isoformat(),
                'to': sender_email,
                'original_email': email_data
            }
            st.session_state['drafts'].append(draft)
            st.toast("📋 Draft saved successfully!", icon="✅")
    with col4:
        if st.button("✅ Archive", key=f"archive_{index}", use_container_width=True):
            st.toast(f"Archived email from {sender_name}!", icon="✅")
    
    st.markdown("---")

def render_compose(email_data=None):
    """Renders the compose page for replying to an email or drafting a new one."""
    st.markdown("## ✉️ Compose Email")
    
    if st.session_state.get('use_ai_reply') and email_data:
        initial_body = email_data.get('aireply', '')
    else:
        initial_body = ""
    
    if email_data:
        st.info(f"**Replying to:** {email_data.get('sender name', 'Unknown')} - {email_data.get('subject', 'No Subject')}")
        
        reply_subject = f"Re: {email_data.get('subject', '')}"
        recipient = email_data.get('sender email', '')
        
        # Show original email content
        with st.expander("📧 View Original Email", expanded=False):
            st.markdown(f"**From:** {email_data.get('sender name', 'Unknown')} ({email_data.get('sender email', '')})")
            st.markdown(f"**Department:** {email_data.get('department', 'N/A')}")
            st.markdown(f"**Date:** {email_data.get('date', 'N/A')}")
            st.markdown(f"**Summary:** {email_data.get('summary', 'No summary available')}")
            if email_data.get('aireply'):
                st.markdown("---")
                st.markdown("**AI Suggestion:**")
                st.markdown(email_data.get('aireply', ''), unsafe_allow_html=True)
        
        # Template selection for reply
        st.markdown("### 📝 Choose Reply Method")
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
                st.markdown(f"<div style='background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;'>{initial_body}</div>", unsafe_allow_html=True)
    else:
        st.info("Composing a new email.")
        reply_subject = ""
        recipient = ""
    
    st.markdown("---")
    st.markdown("### ✍️ Compose Your Message")
    
    with st.form("compose_form"):
        to_address = st.text_input("📧 To:", value=recipient, placeholder="recipient@example.com")
        cc_address = st.text_input("📧 CC:", placeholder="cc@example.com (optional)")
        subject = st.text_input("📋 Subject:", value=reply_subject, placeholder="Email subject")
        
        st.markdown("**📝 Message Body:**")
        
        # Editor options
        col_editor1, col_editor2 = st.columns([1, 4])
        with col_editor1:
            editor_mode = st.selectbox("Editor Mode:", ["Plain Text", "HTML"])
        with col_editor2:
            if editor_mode == "HTML":
                st.info("HTML mode: You can use HTML tags for formatting (e.g., <strong>, <em>, <ul>, <li>)")
        
        body = st.text_area(
            "Body:", 
            value=initial_body, 
            height=400,
            placeholder="Type your message here..." if editor_mode == "Plain Text" else "Type your message here using HTML formatting...",
            label_visibility="collapsed"
        )
        
        # Formatting toolbar hint
        if editor_mode == "HTML":
            st.markdown("""
            <div style='background: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 13px;'>
            <strong>Quick HTML Tips:</strong> 
            &lt;strong&gt;bold&lt;/strong&gt;, 
            &lt;em&gt;italic&lt;/em&gt;, 
            &lt;p&gt;paragraph&lt;/p&gt;, 
            &lt;ul&gt;&lt;li&gt;bullet&lt;/li&gt;&lt;/ul&gt;
            </div>
            """, unsafe_allow_html=True)
        
        # Attachment section
        st.markdown("**📎 Attachments:**")
        uploaded_files = st.file_uploader("Add files", accept_multiple_files=True, label_visibility="collapsed")
        
        if uploaded_files:
            st.write(f"📎 {len(uploaded_files)} file(s) selected:")
            for file in uploaded_files:
                st.write(f"  • {file.name}")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            send_button = st.form_submit_button("📤 Send Email", use_container_width=True, type="primary")
        with col2:
            draft_button = st.form_submit_button("📋 Save as Draft", use_container_width=True)
        with col3:
            preview_button = st.form_submit_button("👁️ Preview", use_container_width=True)
        
        if send_button:
            if to_address and subject and body:
                st.success(f"✅ Email sent successfully to {to_address}!")
                st.balloons()
                time.sleep(1)
                st.session_state['page'] = 'inbox'
                st.session_state['selected_email'] = None
                st.session_state['use_ai_reply'] = False
                st.rerun()
            else:
                st.error("❌ Please fill in To, Subject, and Body fields before sending.")
        
        if draft_button:
            if 'drafts' not in st.session_state:
                st.session_state['drafts'] = []
            
            draft = {
                'subject': subject,
                'body': body,
                'timestamp': datetime.now().isoformat(),
                'to': to_address,
                'cc': cc_address,
                'editor_mode': editor_mode,
                'attachments': [file.name for file in uploaded_files] if uploaded_files else [],
                'original_email': email_data
            }
            st.session_state['drafts'].append(draft)
            st.success("📋 Draft saved successfully!")
            time.sleep(1)
            st.session_state['page'] = 'drafts'
            st.rerun()
        
        if preview_button:
            st.markdown("---")
            st.markdown("### 👁️ Email Preview")
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 10px; border: 2px solid #e0e0e0;'>
                <div style='color: black;'><strong>To:</strong> {to_address}</div>
                {f"<div style='color: black;'><strong>CC:</strong> {cc_address}</div>" if cc_address else ""}
                <div style='color: black;'><strong>Subject:</strong> {subject}</div>
                <hr style='margin: 15px 0;'>
                <div style='color: black;'>{body if editor_mode == "HTML" else body.replace(chr(10), "<br>")}</div>
            </div>
            """, unsafe_allow_html=True)

def render_drafts():
    """Renders the drafts page showing saved draft emails - IMPROVED VERSION."""
    st.markdown("## 📋 Drafts")
    
    if 'drafts' not in st.session_state or len(st.session_state['drafts']) == 0:
        st.info("No drafts saved yet. Compose an email and save it as a draft to see it here!")
        
        if st.button("✉️ Compose New Email"):
            st.session_state['page'] = 'compose'
            st.session_state['selected_email'] = None
            st.rerun()
        return
    
    st.success(f"You have **{len(st.session_state['drafts'])}** saved draft(s).")
    st.markdown("---")
    
    for idx, draft in enumerate(st.session_state['drafts']):
        # Get draft-specific fields
        subject = draft.get('subject', 'No Subject')
        body = draft.get('body', 'No content')
        timestamp = draft.get('timestamp', datetime.now().isoformat())
        to_address = draft.get('to', 'No recipient')
        cc_address = draft.get('cc', '')
        attachments = draft.get('attachments', [])
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_timestamp = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_timestamp = timestamp
        
        # Clean body preview for summary
        body_preview = re.sub('<[^<]+?>', '', str(body))
        body_preview = body_preview.replace('\n', ' ').strip()
        body_preview = body_preview[:200] + "..." if len(body_preview) > 200 else body_preview
        
        # Render the improved draft card
        draft_html = f"""
        <div class="draft-card">
            <div class="draft-timestamp">
                🕒 Saved: {formatted_timestamp}
            </div>
            
            <div class="draft-subject">{subject}</div>
            
            <div class="draft-body-container">
                <div class="draft-body-label">Draft Content</div>
                <div class="draft-body-content">{body if len(body) < 1000 else body_preview}</div>
            </div>
            
            <div class="draft-meta">
                <strong>To:</strong> {to_address}
                {f"<br><strong>CC:</strong> {cc_address}" if cc_address else ""}
                {f"<br><strong>Attachments:</strong> {', '.join(attachments)}" if attachments else ""}
            </div>
        </div>
        """
        st.markdown(draft_html, unsafe_allow_html=True)
        
        # Optional: Show original email reference if it exists
        if draft.get('original_email'):
            with st.expander("📧 Original Email Reference"):
                orig = draft['original_email']
                st.markdown(f"**From:** {orig.get('sender name', 'Unknown')} ({orig.get('sender email', '')})")
                st.markdown(f"**Subject:** {orig.get('subject', 'No Subject')}")
                st.markdown(f"**Date:** {orig.get('date', 'N/A')}")
                st.markdown(f"**Summary:** {orig.get('summary', 'No summary')}")
        
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

# ------------------------------
# 🎯 MAIN APPLICATION
# ------------------------------

def main():
    """Main application function for the single-page Streamlit app."""
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 'inbox'
    if 'selected_email' not in st.session_state:
        st.session_state['selected_email'] = None
    if 'use_ai_reply' not in st.session_state:
        st.session_state['use_ai_reply'] = False
    if 'df' not in st.session_state:
        st.session_state['df'] = generate_mock_data(num_emails=25)
    
    credentials_dict = None

    st.title("📥 InboxKeep Pro: Email Management Dashboard")
    st.markdown("A comprehensive email management application with beautiful card-based UI, AI-powered suggestions, and Google Sheets integration.")
    st.markdown("---")
    
    st.markdown("### 🧭 Navigation")
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        if st.button("📥 Inbox", use_container_width=True, type="primary" if st.session_state['page'] == 'inbox' else "secondary"):
            st.session_state['page'] = 'inbox'
            st.session_state['selected_email'] = None
            st.rerun()
    with col2:
        if st.button("✉️ Compose", use_container_width=True, type="primary" if st.session_state['page'] == 'compose' else "secondary"):
            st.session_state['page'] = 'compose'
            st.session_state['selected_email'] = None
            st.rerun()
    with col3:
        drafts_count = len(st.session_state.get('drafts', []))
        if st.button(f"📋 Drafts ({drafts_count})", use_container_width=True, type="primary" if st.session_state['page'] == 'drafts' else "secondary"):
            st.session_state['page'] = 'drafts'
            st.rerun()
    
    st.markdown("---")
    
    # --- Sidebar Configuration (credentials only) ---
    with st.sidebar:
        st.markdown("### 🔐 Google Service Account Credentials")
        st.markdown("""
        <div style='background: rgba(59, 130, 246, 0.1); padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #3b82f6;'>
            <p style='margin: 0; color: #1e3a8a; font-size: 14px; font-weight: 600;'>
                📄 Upload your Service Account JSON file
            </p>
            <p style='margin: 8px 0 0 0; color: #1e40af; font-size: 13px;'>
                This file enables Gmail API and Google Sheets access. Get it from:
            </p>
            <p style='margin: 4px 0 0 0; color: #3b82f6; font-size: 12px;'>
                ☁️ Google Cloud Console → IAM & Admin → Service Accounts → Keys
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose JSON credentials file",
            type=['json'],
            help="Upload the complete Service Account JSON file from Google Cloud Console",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                credentials_dict = json.load(uploaded_file)
                st.success(f"✅ Credentials loaded: {uploaded_file.name}")
                st.info(f"📧 Service Account: {credentials_dict.get('client_email', 'N/A')}")
            except Exception as e:
                st.error(f"❌ Error reading JSON file: {str(e)}")
                credentials_dict = None
        
        st.markdown("---")
        
        if credentials_dict:
            if st.button("🔄 Load Data from Google Sheets", use_container_width=True, type="primary"):
                with st.spinner("Loading data from Google Sheets..."):
                    df = load_data_from_gsheet(credentials_dict)
                    st.session_state['df'] = df
                    st.rerun()
        else:
            st.warning("⚠️ No credentials uploaded. Using mock data.")
            
        st.markdown("---")
        st.markdown(f"### 📊 Sheet Configuration")
        st.info(f"📊 Sheet ID: `{SHEET_ID}`")
        
        # Filters in sidebar (only for inbox page)
        if st.session_state['page'] == 'inbox':
            st.markdown("---")
            st.markdown("### 🔍 Inbox Filters")
            
            all_departments = ['All'] + sorted(st.session_state['df']['department'].unique().tolist())
            department_filter = st.selectbox(
                "Filter by Department:",
                all_departments,
                key='dept_filter'
            )
            
            priority_filter = st.selectbox(
                "Filter by Priority:",
                ["All", "high", "medium", "low"],
                key='priority_filter'
            )
            
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
        st.markdown("### 📊 Data Summary")
        st.info(f"📧 Showing **{len(st.session_state.get('df_view', st.session_state['df']))}** emails")
        st.caption(f"🗄️ Total in database: **{len(st.session_state['df'])}** emails")

    # --- Main Content Area ---
    if st.session_state['page'] == 'inbox':
        render_inbox(st.session_state.get('df_view', st.session_state['df']), credentials_dict)
    elif st.session_state['page'] == 'compose':
        render_compose(st.session_state.get('selected_email'))
    elif st.session_state['page'] == 'drafts':
        render_drafts()

if __name__ == "__main__":
    main()
