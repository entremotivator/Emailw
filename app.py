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
    page_title="InboxKeep - Colorful Card UI",
    page_icon="📥",
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
        background: #f0f2f6; /* Light gray background for contrast */
    }
    
    /* Streamlit's main content container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }

    /* Header Styling */
    h1 {
        color: #1e3a8a; /* Deep Blue */
        font-weight: 800;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 10px;
    }

    /* --- Stats Cards (Dashboard Metrics) --- */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 35px;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); /* Deep Blue to Bright Blue */
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
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%); /* Dark Teal to Bright Teal */
        border-left: 8px solid #5eead4;
    }
    .stat-card.purple {
        background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%); /* Deep Purple to Lavender */
        border-left: 8px solid #c4b5fd;
    }
    .stat-card.orange {
        background: linear-gradient(135deg, #c2410c 0%, #f97316 100%); /* Dark Orange to Bright Orange */
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

    /* --- Email Cards (Inbox Items) --- */
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
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.1);
        border-color: #3b82f6;
    }
    
    /* Priority Marker (Left Border) */
    .email-card.priority-high::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #ef4444; /* Red for High Priority */
    }
    .email-card.priority-medium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #f59e0b; /* Amber for Medium Priority */
    }
    .email-card.priority-low::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 100%;
        background: #10b981; /* Green for Low Priority */
    }

    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-left: 15px; /* Offset for the priority bar */
    }
    .sender-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 20px;
        margin-right: 15px;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
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
        background: #d1fae5; /* Light Green */
        color: #065f46; /* Dark Green */
    }
    .tag.attachment {
        background: #eff6ff; /* Light Blue */
        color: #1e40af; /* Dark Blue */
    }
    .tag.no-attachment {
        background: #f3f4f6;
        color: #6b7280;
    }

    /* AI Reply Preview */
    .ai-reply-preview {
        background: #f0f9ff; /* Very light blue background */
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

    /* Draft Card Styling */
    .draft-card {
        background: #fffbeb; /* Light Yellow/Amber */
        border: 2px solid #fcd34d;
        border-radius: 14px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(252, 211, 77, 0.5);
        transition: all 0.3s ease;
    }
    .draft-card:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 20px rgba(252, 211, 77, 0.7);
    }
    .draft-badge {
        background: #f59e0b;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        margin-left: 12px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
        
        # Get all records as a list of dictionaries
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        df.columns = [col.lower() for col in df.columns]
        
        # Add mock priority column if not present (for UI consistency)
        if 'priority' not in df.columns:
            df['priority'] = 'medium'
        
        # Add mock AIreply column if not present (for UI consistency)
        if 'aireply' not in df.columns:  # Changed to lowercase 'aireply'
            df['aireply'] = ''
            
        # Add mock department column if not present (for UI consistency)
        if 'department' not in df.columns:
            df['department'] = 'General'
        
        st.success(f"✅ Data loaded from Google Sheet (Sheet ID: {SHEET_ID})")
        return df
        
    except Exception as e:
        st.error(f"Error loading data from Google Sheet: {e}")
        return generate_mock_data(num_emails=0) # Return empty DF if real data fails

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
        
        # Find the row index of the email to update (assuming 'subject' is unique enough for mock data)
        # In a real app, you'd use a unique ID. Here we rely on the row index from the original load.
        # Since we don't have the original row index, we'll just update the first row for demonstration.
        # For a real implementation, the email_data would need to contain the original row index.
        # For this mock-up, we will skip the actual sheet update as it requires a specific row index.
        
        # Fallback to session state draft saving for UI demonstration
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

def generate_mock_data(num_emails=15):
    """Generates a longer list of mock email data."""
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
        "Introducing our newest team member, [Name], who will be joining the [Department] team.",
        "Your QPR meeting is scheduled for next Tuesday. Please prepare your self-assessment.",
        "New guidelines for remote work eligibility and office attendance.",
    ]
    
    emails = []
    priorities = ["high", "medium", "low"]
    
    for i in range(num_emails):
        sender_name, sender_email, department = random.choice(mock_senders)
        subject = random.choice(mock_subjects)
        summary = random.choice(mock_summaries)
        
        # Generate a date within the last 30 days
        date_offset = random.randint(0, 30)
        date = (datetime.now() - pd.Timedelta(days=date_offset)).strftime("%Y-%m-%d")
        
        has_attachment = random.choice(["Yes", "No"])
        has_ai_reply = random.choice([True, False, False]) # Less frequent AI replies
        priority = random.choice(priorities)
        
        ai_reply = ""
        if has_ai_reply:
            ai_reply = f"""<div style='font-family: Arial, sans-serif;'><p>Dear {sender_name},</p><p>Thank you for your email regarding <strong>{subject}</strong>. I have reviewed the summary and the proposed next steps.</p><p>I suggest we proceed with the following action: [Specific AI-suggested action].</p><p>I will follow up with a detailed response shortly.</p><p>Best regards</p></div>"""
        
        emails.append({
            "sender name": sender_name,
            "sender email": sender_email,
            "subject": subject,
            "summary": summary,
            "date": date,  # lowercase
            "attachment": has_attachment,  # lowercase
            "aireply": ai_reply,  # lowercase
            "department": department,
            "priority": priority
        })
        
    return pd.DataFrame(emails)


def display_stats(df):
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    ai_replies = df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"])).sum()
    with_attachments = df[df['attachment'].str.lower().isin(['yes', 'true', '1'])].shape[0]
    high_priority = df[df['priority'] == 'high'].shape[0]
    
    st.markdown("""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">📧 Total Emails</div>
        </div>
        <div class="stat-card teal">
            <div class="stat-number">{}</div>
            <div class="stat-label">🤖 AI Replies Ready</div>
        </div>
        <div class="stat-card purple">
            <div class="stat-number">{}</div>
            <div class="stat-label">🔥 High Priority</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{}</div>
            <div class="stat-label">📎 With Attachments</div>
        </div>
    </div>
    """.format(total_emails, ai_replies, high_priority, with_attachments), unsafe_allow_html=True)

def display_email_card(email_data, index, credentials_dict=None):
    """Render one email entry as a colorful card with action buttons."""
    sender_name = email_data.get("sender name", "Unknown Sender")
    sender_email = email_data.get("sender email", "")
    subject = email_data.get("subject", "No Subject")
    summary = email_data.get("summary", "No summary available")
    date = email_data.get("date", "")  # Use lowercase 'date'
    attachment = email_data.get("attachment", "No")  # Use lowercase 'attachment'
    ai_reply = email_data.get("aireply", "")  # Use lowercase 'aireply'
    department = email_data.get("department", "General")
    priority = email_data.get("priority", "low")
    
    initials = get_initials(sender_name)

    try:
        formatted_date = datetime.strptime(str(date), "%Y-%m-%d").strftime("%b %d, %Y")
    except:
        formatted_date = str(date)

    has_attachment = str(attachment).lower() in ["yes", "true", "1"]
    has_ai_reply = bool(ai_reply and str(ai_reply).strip() not in ["", "nan", "None", "null"])
    
    # Tags
    attachment_tag = f'<span class="tag attachment">📎 Attachment</span>' if has_attachment else f'<span class="tag no-attachment">No Attachment</span>'
    ai_tag = f'<span class="tag ai">🤖 AI Suggestion</span>' if has_ai_reply else ''
    
    # AI Reply Preview
    ai_reply_preview = ""
    if has_ai_reply:
        # Strip HTML tags for preview
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
    
    # Action buttons below the card
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        if st.button("✉️ Reply", key=f"reply_{index}", use_container_width=True):
            st.session_state['selected_email'] = email_data
            st.session_state['mode'] = 'compose'
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col2:
        if st.button("🤖 Use AI Reply", key=f"ai_reply_{index}", disabled=not has_ai_reply, use_container_width=True, type="primary"):
            st.session_state['selected_email'] = email_data
            st.session_state['mode'] = 'compose'
            st.session_state['use_ai_reply'] = True
            st.rerun()
    with col3:
        if st.button("📋 Save as Draft", key=f"draft_{index}", use_container_width=True):
            draft_body = ai_reply if has_ai_reply else ""
            if credentials_dict:
                save_draft(email_data, draft_body, credentials_dict)
            else:
                st.toast("Draft saved to session state (Connect Google Sheet to save permanently).", icon="📋")
    with col4:
        if st.button("✅ Archive", key=f"archive_{index}", use_container_width=True):
            st.toast(f"Archived email from {sender_name}!", icon="✅")
    
    st.markdown("---") # Separator after buttons


def render_compose(email_data=None):
    """Renders the compose page for replying to an email or drafting a new one."""
    st.markdown("## ✉️ Compose Email")
    
    if email_data:
        st.info(f"**Replying to:** {email_data.get('sender name', 'Unknown')} ({email_data.get('sender email', '')})")
        st.markdown(f"**Original Subject:** {email_data.get('subject', 'No Subject')}")
        
        reply_subject = f"Re: {email_data.get('subject', '')}"
        recipient = email_data.get('sender email', '')
        
        # Check if user wants to use AI reply
        if st.session_state.get('use_ai_reply', False):
            ai_reply_body = email_data.get('aireply', '')  # lowercase 'aireply'
            initial_body = ai_reply_body if ai_reply_body else ""
        else:
            initial_body = ""
    else:
        st.info("Composing a new email.")
        reply_subject = ""
        recipient = ""
        initial_body = ""
    
    # Form
    with st.form("compose_form"):
        to_address = st.text_input("To:", value=recipient)
        subject = st.text_input("Subject:", value=reply_subject)
        body = st.text_area("Body:", value=initial_body, height=300)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
        with col2:
            draft_button = st.form_submit_button("📋 Save Draft", use_container_width=True)
        
        if send_button:
            if to_address and subject and body:
                st.success(f"✅ Email sent to {to_address}!")
                st.balloons()
                time.sleep(1)
                st.session_state['mode'] = 'inbox'
                st.session_state['selected_email'] = None
                st.session_state['use_ai_reply'] = False
                st.rerun()
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

    # Back button
    if st.button("⬅️ Back to Inbox"):
        st.session_state['mode'] = 'inbox'
        st.session_state['selected_email'] = None
        st.session_state['use_ai_reply'] = False
        st.rerun()


def render_drafts():
    """Renders the drafts page showing saved draft emails."""
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
        with st.container():
            st.markdown(f"### Draft #{idx + 1}")
            st.markdown(f"**To:** {draft.get('to', 'N/A')}")
            st.markdown(f"**Subject:** {draft.get('subject', 'No Subject')}")
            st.markdown(f"**Saved:** {draft.get('timestamp', 'Unknown')}")
            
            with st.expander("View Draft Body"):
                st.markdown(draft.get('body', 'No content'), unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("✏️ Edit", key=f"edit_draft_{idx}", use_container_width=True):
                    st.session_state['selected_email'] = draft.get('original_email')
                    st.session_state['mode'] = 'compose'
                    # Pre-fill with draft content
                    st.session_state['draft_to_edit'] = draft
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_draft_{idx}", use_container_width=True):
                    st.session_state['drafts'].pop(idx)
                    st.toast("Draft deleted!", icon="🗑️")
                    st.rerun()
            
            st.markdown("---")
    
    if st.button("⬅️ Back to Inbox"):
        st.session_state['mode'] = 'inbox'
        st.rerun()


def render_inbox(df, credentials_dict=None):
    """Renders the inbox page with email cards and stats."""
    st.markdown("## 📥 Inbox")
    
    # Display statistics
    display_stats(df)
    
    st.markdown("---")
    st.markdown(f"### 📬 {len(df)} Email(s)")
    
    if len(df) == 0:
        st.info("No emails to display with the current filters.")
        return
    
    # Display each email as a card
    for idx, row in df.iterrows():
        display_email_card(row.to_dict(), idx, credentials_dict)


def main():
    """Main application function for the single-page Streamlit app."""
    
    # Initialize session state for navigation and data
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'inbox' # 'inbox', 'compose', 'drafts'
    if 'selected_email' not in st.session_state:
        st.session_state['selected_email'] = None
    if 'use_ai_reply' not in st.session_state:
        st.session_state['use_ai_reply'] = False
    
    # Initialize credentials_dict
    credentials_dict = None

    st.title("📥 InboxKeep: Colorful Card UI Theme")
    st.markdown("A **full-page** Streamlit application demonstrating a vibrant, card-based UI for an email management dashboard.")
    st.markdown("---")
    
    # --- Sidebar Configuration (Filters and Actions) ---
    with st.sidebar:
        st.markdown("### ⚙️ Navigation & Filters")
        
        # Main Navigation
        mode_options = {
            'inbox': "📥 Inbox",
            'compose': "✉️ Compose",
            'drafts': "📋 Drafts"
        }
        
        # Use a radio button for clear navigation
        current_mode = st.radio(
            "Select View:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            key='sidebar_mode_select'
        )
        
        # Update session state mode
        if current_mode != st.session_state['mode']:
            st.session_state['mode'] = current_mode
            st.session_state['selected_email'] = None # Clear selection on mode change
            st.rerun()

        st.markdown("---")
        
        # JSON Credentials Upload
        st.markdown("#### 🔐 Upload JSON Credentials")
        uploaded_file = st.file_uploader("Choose your credentials JSON file", type=['json'])
        
        if uploaded_file is not None:
            try:
                credentials_dict = json.load(uploaded_file)
                st.success("✅ Credentials loaded successfully!")
            except Exception as e:
                st.error(f"Error reading JSON file: {str(e)}")
                credentials_dict = None
        
        st.markdown("---")
        
        # Load data based on credentials
        if credentials_dict:
            df = load_data_from_gsheet(credentials_dict)
        else:
            st.warning("Please upload Google Sheets credentials to load real data.")
            df = generate_mock_data(num_emails=25)
            
        # Store the loaded/mock data in session state
        st.session_state['df'] = df
        
        # Filters (Only visible in Inbox mode)
        if st.session_state['mode'] == 'inbox':
            st.markdown("#### 🔍 Inbox Filters")
            
            # Department filter
            all_departments = ['All'] + sorted(st.session_state['df']['department'].unique().tolist())
            department_filter = st.selectbox(
                "Filter by Department:",
                all_departments,
                key='dept_filter'
            )
            
            # Priority filter
            priority_filter = st.selectbox(
                "Filter by Priority:",
                ["All", "high", "medium", "low"],
                key='priority_filter'
            )
            
            # Sort option
            sort_option = st.selectbox(
                "Sort by:",
                ["Date (Newest First)", "Date (Oldest First)", "AI Replies First", "Priority (High First)"],
                key='sort_option'
            )
            
            # Apply filters and sorting to a temporary DataFrame
            df_filtered = st.session_state['df'].copy()
            
            if department_filter != "All":
                df_filtered = df_filtered[df_filtered['department'] == department_filter]
            
            if priority_filter != "All":
                df_filtered = df_filtered[df_filtered['priority'] == priority_filter]
            
            # Apply sorting
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
        st.info(f"Showing **{len(st.session_state.get('df_view', st.session_state['df']))}** emails.")
        st.caption("This is a mock-up with generated data for demonstration.")

    # --- Main Content Area ---
    if st.session_state['mode'] == 'inbox':
        render_inbox(st.session_state.get('df_view', st.session_state['df']), credentials_dict)
    elif st.session_state['mode'] == 'compose':
        render_compose(st.session_state.get('selected_email'))
    elif st.session_state['mode'] == 'drafts':
        render_drafts()

if __name__ == "__main__":
    main()


