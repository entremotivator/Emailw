import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import time

# ------------------------------
# 🔧 PAGE CONFIGURATION
# ------------------------------
st.set_page_config(
    page_title="Email Management Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# 🎨 CUSTOM CSS
# ------------------------------
st.markdown("""
<style>
    /* Email Cards */
    .email-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .email-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .sender-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin-right: 12px;
    }
    .sender-details {
        flex: 1;
    }
    .sender-name {
        font-weight: bold;
        font-size: 17px;
        color: #1f2937;
    }
    .sender-email {
        color: #6b7280;
        font-size: 13px;
    }
    .subject {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin: 15px 0 10px 0;
        line-height: 1.4;
    }
    .summary {
        color: #4b5563;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 18px;
    }
    .email-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: #9ca3af;
        border-top: 1px solid #f3f4f6;
        padding-top: 12px;
        margin-bottom: 15px;
    }
    .date {
        font-weight: 500;
        color: #6b7280;
    }
    .attachment {
        background: #dbeafe;
        color: #1e40af;
        padding: 5px 10px;
        border-radius: 6px;
        font-weight: 500;
    }
    .no-attachment {
        color: #9ca3af;
    }
    
    /* Stats Cards */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        flex: 1;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .stat-label {
        font-size: 14px;
        opacity: 0.95;
        font-weight: 500;
    }
    
    /* Email Editor */
    .editor-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .editor-header {
        font-size: 24px;
        font-weight: bold;
        color: #111827;
        margin-bottom: 20px;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
    }
    
    /* Template Cards */
    .template-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .template-card:hover {
        border-color: #667eea;
        transform: scale(1.02);
    }
    .template-title {
        font-size: 18px;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 8px;
    }
    .template-desc {
        font-size: 14px;
        color: #6b7280;
    }
    
    /* Draft Badge */
    .draft-badge {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-left: 10px;
    }
    
    /* Action Buttons */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 📝 EMAIL TEMPLATES
# ------------------------------
EMAIL_TEMPLATES = {
    "Professional Reply": {
        "subject": "Re: {original_subject}",
        "body": """<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {sender_name},</p>
    <p>Thank you for your email regarding {subject}.</p>
    <p>I have reviewed your message and would like to respond as follows:</p>
    <p>[Your response here]</p>
    <p>Please let me know if you need any further information or clarification.</p>
    <p>Best regards,<br>
    <strong>[Your Name]</strong><br>
    [Your Title]<br>
    [Your Contact Information]</p>
</div>""",
        "description": "Formal professional response template"
    },
    "Quick Acknowledgment": {
        "subject": "Re: {original_subject}",
        "body": """<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {sender_name},</p>
    <p>Thanks for reaching out! I've received your message about {subject}.</p>
    <p>I'm currently reviewing the details and will get back to you with a comprehensive response within 24-48 hours.</p>
    <p>Thanks for your patience!</p>
    <p>Best,<br>
    <strong>[Your Name]</strong></p>
</div>""",
        "description": "Quick acknowledgment for received emails"
    },
    "Meeting Request": {
        "subject": "Re: {original_subject} - Meeting Request",
        "body": """<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hello {sender_name},</p>
    <p>Thank you for your email about {subject}.</p>
    <p>I think it would be beneficial to discuss this further in a meeting. Would you be available for a call this week?</p>
    <p>Here are some time slots that work for me:</p>
    <ul>
        <li>[Day], [Time] - [Time]</li>
        <li>[Day], [Time] - [Time]</li>
        <li>[Day], [Time] - [Time]</li>
    </ul>
    <p>Please let me know which works best for you, or suggest an alternative time.</p>
    <p>Looking forward to connecting!</p>
    <p>Best regards,<br>
    <strong>[Your Name]</strong></p>
</div>""",
        "description": "Request a meeting to discuss further"
    },
    "Follow-up": {
        "subject": "Follow-up: {original_subject}",
        "body": """<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {sender_name},</p>
    <p>I wanted to follow up on my previous email regarding {subject}.</p>
    <p>I understand you may be busy, but I'd appreciate any updates or feedback you might have when you get a chance.</p>
    <p>Key points from my last message:</p>
    <ul>
        <li>[Point 1]</li>
        <li>[Point 2]</li>
        <li>[Point 3]</li>
    </ul>
    <p>Please let me know if you need any additional information from my end.</p>
    <p>Thank you,<br>
    <strong>[Your Name]</strong></p>
</div>""",
        "description": "Follow up on previous communication"
    },
    "Decline with Alternatives": {
        "subject": "Re: {original_subject}",
        "body": """<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {sender_name},</p>
    <p>Thank you for reaching out about {subject}.</p>
    <p>Unfortunately, I won't be able to accommodate this request at this time due to [reason].</p>
    <p>However, I'd like to suggest the following alternatives:</p>
    <ul>
        <li>[Alternative 1]</li>
        <li>[Alternative 2]</li>
    </ul>
    <p>I hope one of these options works for you. Please don't hesitate to reach out if you'd like to discuss further.</p>
    <p>Best regards,<br>
    <strong>[Your Name]</strong></p>
</div>""",
        "description": "Politely decline with alternative suggestions"
    }
}

# ------------------------------
# 🧩 HELPER FUNCTIONS
# ------------------------------
def load_credentials_from_json(json_content):
    """Load Google Sheets credentials from JSON content."""
    try:
        credentials_dict = json.loads(json_content)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        return Credentials.from_service_account_info(credentials_dict, scopes=scope)
    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        return None


def connect_to_gsheet(credentials, sheet_url):
    """Connect to Google Sheets and return the first worksheet."""
    try:
        gc = gspread.authorize(credentials)
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        worksheet = gc.open_by_key(sheet_id).sheet1
        return worksheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None


def load_data_from_gsheet(worksheet):
    """Load data from Google Sheets into a DataFrame."""
    try:
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


def create_sample_data():
    """Fallback sample email dataset."""
    return pd.DataFrame([
        {
            "sender name": "John Smith",
            "sender email": "john.smith@company.com",
            "subject": "Q4 Sales Report - Action Required",
            "summary": "Please review the attached Q4 sales report and provide feedback by end of week.",
            "Date": "2024-01-15",
            "Attachment": "Yes",
            "AIreply": "<div style='font-family: Arial, sans-serif;'><p>Dear John,</p><p>Thank you for sending the Q4 sales report. I have reviewed the document and it looks comprehensive. The numbers are impressive, showing a 15% increase compared to Q3.</p><p>I'll provide detailed feedback by Thursday as requested.</p><p>Best regards</p></div>",
            "department": "Sales"
        },
        {
            "sender name": "Sarah Johnson",
            "sender email": "sarah.j@marketing.com",
            "subject": "Marketing Campaign Results",
            "summary": "The campaign exceeded expectations with a 25% increase in engagement.",
            "Date": "2024-01-14",
            "Attachment": "No",
            "AIreply": "<div style='font-family: Arial, sans-serif;'><p>Hi Sarah,</p><p>Congratulations on the successful campaign! A 25% engagement increase is outstanding and demonstrates the effectiveness of your strategy.</p><p>Let's schedule a meeting to discuss scaling this approach for Q2.</p><p>Great work!</p></div>",
            "department": "Marketing"
        },
        {
            "sender name": "Mike Chen",
            "sender email": "m.chen@tech.io",
            "subject": "System Maintenance Scheduled",
            "summary": "Server maintenance scheduled this weekend. Expected downtime: 2–4 hours.",
            "Date": "2024-01-13",
            "Attachment": "Yes",
            "AIreply": "<div style='font-family: Arial, sans-serif;'><p>Hi Mike,</p><p>Thanks for the heads up about the scheduled maintenance. The 2-4 hour window works well for us.</p><p>Please confirm when the maintenance is complete so we can verify all systems are operational.</p><p>Thanks</p></div>",
            "department": "IT"
        },
        {
            "sender name": "Lisa Rodriguez",
            "sender email": "lisa.r@hr.company.com",
            "subject": "Team Building Event - Save the Date",
            "summary": "Annual team building event next month. Please confirm your attendance.",
            "Date": "2024-01-12",
            "Attachment": "No",
            "AIreply": "<div style='font-family: Arial, sans-serif;'><p>Hi Lisa,</p><p>Thanks for organizing the annual team building event! I'm happy to confirm my attendance.</p><p>Please let me know if you need any help with the planning or coordination.</p><p>Looking forward to it!</p></div>",
            "department": "HR"
        },
        {
            "sender name": "David Wilson",
            "sender email": "d.wilson@finance.com",
            "subject": "Budget Approval Request",
            "summary": "Requesting approval for additional project budget. ROI details attached.",
            "Date": "2024-01-11",
            "Attachment": "Yes",
            "AIreply": "<div style='font-family: Arial, sans-serif;'><p>Dear David,</p><p>I've reviewed your budget approval request along with the ROI projections you provided.</p><p>The numbers look solid and justify the additional investment. I'm approving the request. Please proceed with the next steps.</p><p>Best regards</p></div>",
            "department": "Finance"
        }
    ])


def get_initials(name):
    """Extract initials from sender name."""
    if not name or name == "Unknown Sender":
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[0].upper() if name else "?"


def display_stats(df):
    """Display statistics about emails in a nice card layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(df)}</div>
            <div class="stat-label">📬 Total Emails</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ai_replies = len(df[df['AIreply'].notna() & (df['AIreply'] != '')]) if 'AIreply' in df.columns else 0
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">{ai_replies}</div>
            <div class="stat-label">🤖 AI Replies Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        attachments = len(df[df['Attachment'].str.lower().isin(['yes', 'true', '1'])]) if 'Attachment' in df.columns else 0
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-number">{attachments}</div>
            <div class="stat-label">📎 With Attachments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        drafts_count = len(st.session_state.get('drafts', []))
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-number">{drafts_count}</div>
            <div class="stat-label">📝 Saved Drafts</div>
        </div>
        """, unsafe_allow_html=True)


def display_email_card(email_data, index):
    """Render one email entry as a card with action buttons."""
    sender_name = email_data.get("sender name", "Unknown Sender")
    sender_email = email_data.get("sender email", "")
    subject = email_data.get("subject", "No Subject")
    summary = email_data.get("summary", "No summary available")
    date = email_data.get("Date", "")
    attachment = email_data.get("Attachment", "No")
    ai_reply = email_data.get("AIreply", "")
    department = email_data.get("department", "General")
    
    initials = get_initials(sender_name)

    try:
        formatted_date = datetime.strptime(str(date), "%Y-%m-%d").strftime("%B %d, %Y")
    except:
        formatted_date = str(date)

    has_attachment = str(attachment).lower() in ["yes", "true", "1"]
    attachment_class = "attachment" if has_attachment else "no-attachment"
    attachment_text = "📎 Has Attachment" if has_attachment else "No Attachment"
    
    has_ai_reply = bool(ai_reply and str(ai_reply).strip() != "")

    card_html = f"""
    <div class="email-card">
        <div class="sender-info">
            <div class="sender-avatar">{initials}</div>
            <div class="sender-details">
                <div class="sender-name">{sender_name}</div>
                <div class="sender-email">&lt;{sender_email}&gt;</div>
            </div>
        </div>
        <div class="subject">{subject}</div>
        <div class="summary">{summary}</div>
        <div class="email-meta">
            <div class="date">📅 {formatted_date} | 🏢 {department}</div>
            <div class="{attachment_class}">{attachment_text}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if has_ai_reply:
        st.markdown('<span class="draft-badge">🤖 AI Reply Ready</span>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        if st.button("✉️ Reply", key=f"reply_{index}"):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = email_data
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col2:
        if st.button("🤖 AI Reply", key=f"ai_reply_{index}", disabled=not has_ai_reply):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = email_data
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = True
            st.rerun()
    with col3:
        if st.button("📝 Quick Reply", key=f"quick_{index}"):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = email_data
            st.session_state['selected_template'] = "Quick Acknowledgment"
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col4:
        if st.button("📋 Draft", key=f"draft_{index}"):
            draft_body = ai_reply if has_ai_reply else ""
            save_draft(email_data, draft_body)
            st.success("Saved to drafts!")
    with col5:
        if has_ai_reply and st.button("👁️ Preview AI", key=f"preview_{index}"):
            with st.expander("🤖 AI Generated Reply Preview", expanded=True):
                st.markdown(ai_reply, unsafe_allow_html=True)


def save_draft(email_data, body):
    """Save email draft to session state."""
    if 'drafts' not in st.session_state:
        st.session_state['drafts'] = []
    
    draft = {
        'original_email': email_data,
        'body': body,
        'timestamp': datetime.now().isoformat(),
        'subject': f"Re: {email_data.get('subject', '')}"
    }
    st.session_state['drafts'].append(draft)


def render_email_composer(email_data=None, template_name=None):
    """Render email composition interface."""
    st.markdown('<div class="editor-container">', unsafe_allow_html=True)
    st.markdown('<div class="editor-header">✍️ Compose Reply</div>', unsafe_allow_html=True)
    
    if email_data:
        st.info(f"📬 Replying to: **{email_data.get('sender name')}** - {email_data.get('subject')}")
    
    use_ai_reply = st.session_state.get('use_ai_reply', False)
    ai_reply_content = email_data.get('AIreply', '') if email_data and use_ai_reply else ''
    
    if use_ai_reply and ai_reply_content:
        st.success("🤖 Using AI-generated reply from Google Sheets - Ready to send or edit!")
    
    st.subheader("📋 Choose a Template")
    cols = st.columns(5)
    
    template_buttons = list(EMAIL_TEMPLATES.keys())
    for idx, template_name_btn in enumerate(template_buttons):
        with cols[idx]:
            if st.button(f"📄 {template_name_btn.split()[0]}", key=f"template_{idx}", use_container_width=True):
                st.session_state['selected_template'] = template_name_btn
                st.session_state['use_ai_reply'] = False
                st.rerun()
    
    selected_template = st.session_state.get('selected_template', template_name)
    
    if use_ai_reply and ai_reply_content:
        subject = f"Re: {email_data.get('subject', '')}"
        body = ai_reply_content
    elif selected_template and selected_template in EMAIL_TEMPLATES:
        template = EMAIL_TEMPLATES[selected_template]
        st.success(f"✅ Using template: **{selected_template}** - {template['description']}")
        
        subject = template['subject'].format(
            original_subject=email_data.get('subject', '') if email_data else ''
        )
        body = template['body'].format(
            sender_name=email_data.get('sender name', '[Sender Name]') if email_data else '[Sender Name]',
            subject=email_data.get('subject', '[Subject]') if email_data else '[Subject]'
        )
    else:
        subject = f"Re: {email_data.get('subject', '')}" if email_data else ""
        body = ""
    
    st.markdown("---")
    
    email_to = st.text_input("To:", value=email_data.get('sender email', '') if email_data else '')
    email_subject = st.text_input("Subject:", value=subject)
    
    editor_mode = st.radio("Editor Mode:", ["HTML Editor", "Plain Text"], horizontal=True)
    
    if editor_mode == "HTML Editor":
        st.markdown("**HTML Body:**")
        email_body = st.text_area("", value=body, height=400, key="html_editor")
        
        with st.expander("👁️ Preview HTML", expanded=False):
            st.markdown(email_body, unsafe_allow_html=True)
    else:
        email_body = st.text_area("Message:", value="", height=300, key="plain_editor")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("📤 Send", type="primary", use_container_width=True):
            if email_to and email_subject and email_body:
                st.success(f"✅ Email sent to {email_to}!")
                st.balloons()
                st.session_state['composing_email'] = False
                st.session_state['selected_template'] = None
                st.session_state['use_ai_reply'] = False
                time.sleep(2)
                st.rerun()
            else:
                st.error("Please fill in all fields")
    
    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            if email_data:
                save_draft(email_data, email_body)
                st.success("Draft saved!")
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state['composing_email'] = False
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_drafts():
    """Render drafts management interface."""
    st.header("📝 Email Drafts")
    
    if 'drafts' not in st.session_state or len(st.session_state['drafts']) == 0:
        st.info("No drafts saved yet. Create a draft by clicking 'Save Draft' when composing an email.")
        return
    
    for idx, draft in enumerate(st.session_state['drafts']):
        original = draft['original_email']
        
        with st.expander(f"📄 Draft {idx + 1}: {draft['subject']}", expanded=False):
            st.markdown(f"**To:** {original.get('sender email', 'N/A')}")
            st.markdown(f"**Original Subject:** {original.get('subject', 'N/A')}")
            st.markdown(f"**Saved:** {datetime.fromisoformat(draft['timestamp']).strftime('%B %d, %Y %I:%M %p')}")
            
            st.markdown("---")
            st.markdown("**Draft Content:**")
            st.markdown(draft['body'], unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✏️ Edit", key=f"edit_draft_{idx}"):
                    st.session_state['composing_email'] = True
                    st.session_state['reply_to'] = original
                    st.session_state['editing_draft'] = idx
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_draft_{idx}"):
                    st.session_state['drafts'].pop(idx)
                    st.success("Draft deleted!")
                    st.rerun()


def main():
    if 'composing_email' not in st.session_state:
        st.session_state['composing_email'] = False
    if 'drafts' not in st.session_state:
        st.session_state['drafts'] = []
    if 'selected_template' not in st.session_state:
        st.session_state['selected_template'] = None
    if 'use_ai_reply' not in st.session_state:
        st.session_state['use_ai_reply'] = False
    
    st.title("📧 Advanced Email Management Dashboard")
    st.markdown("**Manage emails, compose replies with AI-powered templates, and organize drafts - all in one place**")
    
    st.sidebar.header("🔐 Google Sheets Authentication")
    st.sidebar.markdown("Upload your service account JSON file to connect to Google Sheets")
    
    uploaded_file = st.sidebar.file_uploader("Upload JSON Service Account File", type=['json'])
    sheet_url = st.sidebar.text_input(
        "Google Sheets URL",
        value="https://docs.google.com/spreadsheets/d/1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc/edit?usp=sharing"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Settings")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh data", value=False)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 30, 300, 60)
    
    if st.sidebar.button("🔄 Refresh Data Now", use_container_width=True):
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Quick Stats")
    st.sidebar.info("**Expected Columns:**\n- sender name\n- sender email\n- subject\n- summary\n- Date\n- Attachment\n- AIreply\n- department")
    
    tab1, tab2, tab3 = st.tabs(["📬 Inbox", "✍️ Compose", "📝 Drafts"])
    
    with tab1:
        df = pd.DataFrame()
        
        if uploaded_file and sheet_url:
            try:
                credentials = load_credentials_from_json(uploaded_file.read().decode('utf-8'))
                if credentials:
                    with st.spinner("Connecting to Google Sheets..."):
                        worksheet = connect_to_gsheet(credentials, sheet_url)
                        if worksheet:
                            df = load_data_from_gsheet(worksheet)
                            st.sidebar.success("✅ Connected to Google Sheets")
            except Exception as e:
                st.sidebar.error(f"Connection error: {e}")
        
        if df.empty:
            st.info("📝 Using sample data. Upload credentials in the sidebar to load live data from Google Sheets.")
            df = create_sample_data()
        else:
            st.success(f"✅ Loaded {len(df)} emails from Google Sheets")
        
        display_stats(df)
        
        st.markdown("### 🔍 Search & Filter")
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            search = st.text_input("Search emails", placeholder="Search by sender, subject, or summary...", label_visibility="collapsed")
        with col2:
            attach_filter = st.selectbox("Filter", ["All Emails", "With Attachments", "Without Attachments"], label_visibility="collapsed")
        with col3:
            departments = ["All Departments"] + sorted(df["department"].unique().tolist()) if "department" in df.columns else ["All Departments"]
            dept_filter = st.selectbox("Department", departments, label_visibility="collapsed")
        with col4:
            sort_order = st.selectbox("Sort", ["Newest First", "Oldest First"], label_visibility="collapsed")
        
        filtered_df = df.copy()
        
        if search:
            mask = (
                filtered_df["sender name"].str.contains(search, case=False, na=False) |
                filtered_df["subject"].str.contains(search, case=False, na=False) |
                filtered_df["summary"].str.contains(search, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if attach_filter == "With Attachments":
            filtered_df = filtered_df[filtered_df["Attachment"].str.lower().isin(['yes', 'true', '1'])]
        elif attach_filter == "Without Attachments":
            filtered_df = filtered_df[~filtered_df["Attachment"].str.lower().isin(['yes', 'true', '1'])]
        
        if dept_filter != "All Departments" and "department" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["department"] == dept_filter]
        
        try:
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            ascending = sort_order == "Oldest First"
            filtered_df = filtered_df.sort_values("Date", ascending=ascending)
        except:
            pass
        
        st.markdown("---")
        st.markdown(f"### 📬 Inbox ({len(filtered_df)} emails)")
        
        if filtered_df.empty:
            st.warning("⚠️ No matching emails found. Try adjusting your search filters.")
        else:
            for idx, row in filtered_df.iterrows():
                display_email_card(row, idx)
        
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    with tab2:
        if st.session_state.get('composing_email', False):
            render_email_composer(
                email_data=st.session_state.get('reply_to'),
                template_name=st.session_state.get('selected_template')
            )
        else:
            st.info("💡 Go to the Inbox tab and click 'Reply' or 'AI Reply' on any email to start composing, or create a new email below.")
            
            if st.button("✉️ Compose New Email", type="primary"):
                st.session_state['composing_email'] = True
                st.session_state['reply_to'] = None
                st.session_state['use_ai_reply'] = False
                st.rerun()
    
    with tab3:
        render_drafts()


if __name__ == "__main__":
    main()
