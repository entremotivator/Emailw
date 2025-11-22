import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import time
import re

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
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Email Cards - Enhanced with vibrant colors */
    .email-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e0e7ff;
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .email-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    }
    .email-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.25);
        border-color: #818cf8;
    }
    
    .ai-reply-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .ai-reply-preview {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 5px solid #10b981;
        padding: 16px 20px;
        margin: 16px 0;
        border-radius: 10px;
        font-size: 14px;
        color: #065f46;
        line-height: 1.7;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
    }
    
    .sender-info {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        margin-top: 10px;
    }
    .sender-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 22px;
        margin-right: 16px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        border: 3px solid white;
    }
    .sender-details {
        flex: 1;
    }
    .sender-name {
        font-weight: bold;
        font-size: 19px;
        color: #1f2937;
        margin-bottom: 4px;
    }
    .sender-email {
        color: #6b7280;
        font-size: 14px;
    }
    .subject {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin: 18px 0 12px 0;
        line-height: 1.4;
        padding-left: 10px;
    }
    .summary {
        color: #4b5563;
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 20px;
        padding-left: 10px;
    }
    .email-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        color: #9ca3af;
        border-top: 2px solid #f3f4f6;
        padding-top: 14px;
        margin-bottom: 18px;
        padding-left: 10px;
    }
    .date {
        font-weight: 600;
        color: #6366f1;
    }
    .attachment {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
    .no-attachment {
        color: #d1d5db;
        font-size: 13px;
    }
    
    /* Stats Cards - More colorful */
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
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-card.green {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    .stat-card.blue {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    .stat-card.orange {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
    }
    .stat-number {
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stat-label {
        font-size: 15px;
        opacity: 0.95;
        font-weight: 600;
    }
    
    /* Email Editor */
    .editor-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        margin: 25px 0;
        border: 2px solid #e0e7ff;
    }
    .editor-header {
        font-size: 28px;
        font-weight: bold;
        color: #111827;
        margin-bottom: 25px;
        border-bottom: 3px solid #667eea;
        padding-bottom: 12px;
    }
    
    /* HTML Preview Box */
    .html-preview {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Plain Text Display - Enhanced */
    .plain-text-display {
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        border: 2px solid #d1d5db;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        font-family: 'Courier New', monospace;
        font-size: 15px;
        line-height: 1.8;
        color: #1f2937;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Draft Card Styling */
    .draft-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #fbbf24;
        border-radius: 14px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
        transition: all 0.3s ease;
    }
    .draft-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(251, 191, 36, 0.4);
    }
    
    .draft-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        margin-left: 12px;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
    }
    
    /* Template Cards */
    .template-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-radius: 12px;
        padding: 22px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .template-card:hover {
        border-color: #667eea;
        transform: scale(1.03);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .template-title {
        font-size: 19px;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 10px;
    }
    .template-desc {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.5;
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


def load_data_from_gsheet(credentials_dict, sheet_url="1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"):
    """Load data from Google Sheets into a DataFrame and populate drafts."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        gc = gspread.authorize(credentials)
        sheet_id = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"
        worksheet = gc.open_by_key(sheet_id).sheet1
        records = worksheet.get_all_records()
        
        if not records:
            st.warning("Google Sheet is empty. Using sample data instead.")
            return create_sample_data()
        
        df = pd.DataFrame(records)
        
        # Ensure required columns exist
        required_columns = ['sender name', 'sender email', 'subject', 'summary', 'Date', 'Attachment', 'AIreply', 'department']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        if 'drafts' not in st.session_state:
            st.session_state['drafts'] = []
        
        # Clear existing drafts and reload from sheet
        st.session_state['drafts'] = []
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('AIreply')) and str(row.get('AIreply', '')).strip():
                draft = {
                    'original_email': {
                        'sender name': row.get('sender name', ''),
                        'sender email': row.get('sender email', ''),
                        'subject': row.get('subject', ''),
                        'summary': row.get('summary', ''),
                        'Date': row.get('Date', ''),
                        'Attachment': row.get('Attachment', ''),
                        'department': row.get('department', '')
                    },
                    'body': row.get('AIreply', ''),
                    'timestamp': datetime.now().isoformat(),
                    'subject': f"Re: {row.get('subject', '')}"
                }
                st.session_state['drafts'].append(draft)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Using sample data instead...")
        return create_sample_data()


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
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    ai_replies = df['AIreply'].notna().sum() if 'AIreply' in df.columns else 0
    with_attachments = df[df['Attachment'].str.lower().isin(['yes', 'true', '1'])].shape[0] if 'Attachment' in df.columns else 0
    drafts_count = len(st.session_state.get('drafts', []))
    
    st.markdown("""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">📧 Total Emails</div>
        </div>
        <div class="stat-card green">
            <div class="stat-number">{}</div>
            <div class="stat-label">🤖 AI Replies Ready</div>
        </div>
        <div class="stat-card blue">
            <div class="stat-number">{}</div>
            <div class="stat-label">📎 With Attachments</div>
        </div>
        <div class="stat-card orange">
            <div class="stat-number">{}</div>
            <div class="stat-label">📋 Saved Drafts</div>
        </div>
    </div>
    """.format(total_emails, ai_replies, with_attachments, drafts_count), unsafe_allow_html=True)


def display_email_card(email_data, index, credentials_dict=None):
    """Render one email entry as a colorful card with action buttons."""
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
    
    has_ai_reply = bool(ai_reply and str(ai_reply).strip() not in ["", "nan", "None", "null"])
    
    ai_reply_badge = ""
    ai_reply_preview = ""
    if has_ai_reply:
        ai_reply_badge = '<div class="ai-reply-badge">🤖 AI Reply Ready</div>'
        # Strip HTML tags for preview
        preview_text = re.sub('<[^<]+?>', '', str(ai_reply))
        preview_text = preview_text[:200] + "..." if len(preview_text) > 200 else preview_text
        ai_reply_preview = f'<div class="ai-reply-preview"><strong>🤖 AI Reply Preview:</strong><br/>{preview_text}</div>'

    card_html = f"""
    <div class="email-card">
        {ai_reply_badge}
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
            <div class="date">📅 {formatted_date} | 🏢 {department}</div>
            <div class="{attachment_class}">{attachment_text}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        if st.button("✉️ Reply", key=f"reply_{index}", use_container_width=True):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = dict(email_data)
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col2:
        ai_button_label = "🤖 Use AI Reply" if has_ai_reply else "🤖 No AI Reply"
        if st.button(ai_button_label, key=f"ai_reply_{index}", disabled=not has_ai_reply, use_container_width=True):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = dict(email_data)
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = True
            st.rerun()
    with col3:
        if st.button("⚡ Quick Reply", key=f"quick_{index}", use_container_width=True):
            st.session_state['composing_email'] = True
            st.session_state['reply_to'] = dict(email_data)
            st.session_state['selected_template'] = "Quick Acknowledgment"
            st.session_state['use_ai_reply'] = False
            st.rerun()
    with col4:
        if st.button("📋 Save as Draft", key=f"draft_{index}", use_container_width=True):
            draft_body = ai_reply if has_ai_reply else ""
            save_draft(dict(email_data), draft_body, credentials_dict)
            st.success("✅ Saved to drafts and Google Sheets!")
    
    st.markdown("---")


def save_draft(email_data, body, credentials_dict=None):
    """Save email draft to session state and Google Sheets column G (AIreply)."""
    if 'drafts' not in st.session_state:
        st.session_state['drafts'] = []
    
    draft = {
        'original_email': email_data,
        'body': body,
        'timestamp': datetime.now().isoformat(),
        'subject': f"Re: {email_data.get('subject', '')}"
    }
    st.session_state['drafts'].append(draft)
    
    # Write to Google Sheets if credentials available
    if credentials_dict:
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            gc = gspread.authorize(credentials)
            sheet_id = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"
            worksheet = gc.open_by_key(sheet_id).sheet1
            
            # Find the row with matching subject and sender email
            all_data = worksheet.get_all_values()
            headers = all_data[0]
            
            # Find AIreply column (column G)
            aireply_col_idx = headers.index('AIreply') + 1 if 'AIreply' in headers else 7
            
            # Search for matching row
            for row_idx, row in enumerate(all_data[1:], start=2):  # Start from row 2 (skip headers)
                if (len(row) > 2 and 
                    row[2] == email_data.get('subject', '') and 
                    row[1] == email_data.get('sender email', '')):
                    # Update AIreply column with draft body
                    worksheet.update_cell(row_idx, aireply_col_idx, body)
                    break
                    
        except Exception as e:
            st.warning(f"Could not save to Google Sheets: {str(e)}")


def render_email_composer(email_data=None, template_name=None):
    """Render email composition interface with HTML and Plain Text modes."""
    st.markdown('<div class="editor-container">', unsafe_allow_html=True)
    st.markdown('<div class="editor-header">✍️ Compose Reply</div>', unsafe_allow_html=True)
    
    has_email_data = email_data is not None and (isinstance(email_data, dict) or hasattr(email_data, 'get'))
    
    if has_email_data:
        st.info(f"📬 Replying to: **{email_data.get('sender name')}** - {email_data.get('subject')}")
    
    use_ai_reply = st.session_state.get('use_ai_reply', False)
    ai_reply_content = email_data.get('AIreply', '') if has_email_data and use_ai_reply else ''
    
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
            original_subject=email_data.get('subject', '') if has_email_data else ''
        )
        body = template['body'].format(
            sender_name=email_data.get('sender name', '[Sender Name]') if has_email_data else '[Sender Name]',
            subject=email_data.get('subject', '[Subject]') if has_email_data else '[Subject]'
        )
    else:
        subject = f"Re: {email_data.get('subject', '')}" if has_email_data else ""
        body = ""
    
    st.markdown("---")
    
    email_to = st.text_input("To:", value=email_data.get('sender email', '') if has_email_data else '')
    email_subject = st.text_input("Subject:", value=subject)
    
    editor_mode = st.radio("Editor Mode:", ["HTML Editor", "Plain Text"], horizontal=True)
    
    if editor_mode == "HTML Editor":
        st.markdown("**HTML Body:**")
        email_body = st.text_area("", value=body, height=400, key="html_editor")
        
        with st.expander("👁️ Preview HTML", expanded=False):
            st.markdown('<div class="html-preview">', unsafe_allow_html=True)
            st.markdown(email_body, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("**Plain Text Message:**")
        
        # Convert HTML to plain text if switching from HTML mode
        plain_body = re.sub('<[^<]+?>', '', body) if body else ""
        plain_body = plain_body.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        
        email_body = st.text_area("", value=plain_body, height=350, key="plain_editor", 
                                   placeholder="Type your message here in plain text...")
        
        if email_body:
            with st.expander("👁️ Preview Plain Text", expanded=False):
                st.markdown(f'<div class="plain-text-display">{email_body}</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("📤 Send", type="primary", use_container_width=True):
            if email_to and email_subject and email_body:
                st.success(f"✅ Email sent to {email_to}!")
                st.balloons()
                st.session_state['composing_email'] = False
                st.session_state['selected_template'] = None
                st.session_state['use_ai_reply'] = False
                st.session_state['reply_to'] = None
                time.sleep(2)
                st.rerun()
            else:
                st.error("⚠️ Please fill in all fields")
    
    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            if has_email_data:
                save_draft(email_data, email_body)
                st.success("✅ Draft saved!")
    
    with col3:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state['composing_email'] = False
            st.session_state['selected_template'] = None
            st.session_state['use_ai_reply'] = False
            st.session_state['reply_to'] = None
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
    """Main application function."""
    st.title("📧 Email Management Dashboard")
    st.markdown("**Manage your emails efficiently with AI-powered replies**")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("---")
        
        # JSON Credentials Upload
        st.markdown("#### 🔐 Upload JSON Credentials")
        uploaded_file = st.file_uploader("Choose your credentials JSON file", type=['json'])
        
        credentials_dict = None
        if uploaded_file is not None:
            try:
                credentials_dict = json.load(uploaded_file)
                st.success("✅ Credentials loaded successfully!")
            except Exception as e:
                st.error(f"Error reading JSON file: {str(e)}")
                credentials_dict = None
        
        st.markdown("---")
        
        # Google Sheets URL (hardcoded)
        sheet_url = "https://docs.google.com/spreadsheets/d/1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc/edit?usp=sharing"
        st.markdown(f"**📊 Google Sheet:**")
        st.code(sheet_url, language=None)
        
        st.markdown("---")
        
        # Department filter
        st.markdown("#### 🏢 Filter by Department")
        department_filter = st.selectbox(
            "Select Department:",
            ["All", "Sales", "Marketing", "IT", "HR", "Finance", "General"],
            index=0
        )
        
        # Sort option
        st.markdown("#### 📑 Sort Emails")
        sort_option = st.selectbox(
            "Sort by:",
            ["Date (Newest First)", "Date (Oldest First)", "AI Replies First", "Sender Name"],
            index=0
        )
        
        # Auto-refresh
        st.markdown("#### 🔄 Auto Refresh")
        auto_refresh = st.checkbox("Enable Auto Refresh", value=False)
        refresh_interval = 60
        if auto_refresh:
            refresh_interval = st.slider("Refresh Interval (seconds)", 30, 300, 60)
        
        st.markdown("---")
        st.markdown("### 📊 Stats Overview")
    
    # Load data
    if credentials_dict:
        df = load_data_from_gsheet(credentials_dict)
    else:
        st.warning("Please upload Google Sheets credentials in the sidebar.")
        df = create_sample_data()
    
    if not df.empty:
        # Apply department filter
        if department_filter != "All":
            df = df[df['department'] == department_filter]
        
        # Apply sorting
        if sort_option == "Date (Newest First)":
            df = df.sort_values('Date', ascending=False)
        elif sort_option == "Date (Oldest First)":
            df = df.sort_values('Date', ascending=True)
        elif sort_option == "AI Replies First":
            df['has_ai_reply'] = df['AIreply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))
            df = df.sort_values(['has_ai_reply', 'Date'], ascending=[False, False])
            df = df.drop('has_ai_reply', axis=1)
        elif sort_option == "Sender Name":
            df = df.sort_values('sender name')
        
        # Display statistics
        display_stats(df)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📥 Inbox", "✍️ Compose", "📋 Drafts"])
    
    with tab1:
        st.markdown("### 📬 Your Emails")
        
        if df.empty:
            st.info("📭 No emails to display for the selected department.")
        else:
            for index, row in df.iterrows():
                display_email_card(row.to_dict(), index, credentials_dict)
        
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
                st.session_state['selected_template'] = None
                st.session_state['use_ai_reply'] = False
                st.rerun()
    
    with tab3:
        st.markdown("### 📋 Saved Drafts")
        st.markdown("*Drafts are saved with AI-generated replies from the AIreply column*")
        st.markdown("---")
        
        drafts = st.session_state.get('drafts', [])
        
        if not drafts:
            st.info("📭 No drafts saved yet. Click 'Save as Draft' on any email card or use 'Save Draft' in the composer.")
        else:
            for idx, draft in enumerate(drafts):
                original = draft.get('original_email', {})
                draft_subject = draft.get('subject', 'No Subject')
                draft_body = draft.get('body', '')
                draft_time = draft.get('timestamp', '')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(draft_time)
                    formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_time = draft_time
                
                # Check if draft has AI reply content
                has_ai_content = bool(draft_body and str(draft_body).strip())
                
                with st.expander(f"📧 Draft {idx + 1}: {draft_subject} {'🤖' if has_ai_content else ''}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**To:** {original.get('sender email', 'N/A')}")
                        st.markdown(f"**Subject:** {draft_subject}")
                        st.markdown(f"**Saved:** {formatted_time}")
                        
                        if has_ai_content:
                            st.markdown("**Draft Content (from AIreply):**")
                            # Display with proper HTML rendering
                            st.markdown('<div class="html-preview">', unsafe_allow_html=True)
                            st.markdown(draft_body, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("No content saved in this draft")
                    
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_draft_{idx}", use_container_width=True):
                            st.session_state['composing_email'] = True
                            st.session_state['reply_to'] = original
                            st.session_state['selected_template'] = None
                            st.session_state['use_ai_reply'] = False
                            # Pre-fill with draft content
                            st.session_state['draft_body'] = draft_body
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_draft_{idx}", use_container_width=True):
                            st.session_state['drafts'].pop(idx)
                            st.success("✅ Draft deleted!")
                            st.rerun()
                
                st.markdown("---")


if __name__ == "__main__":
    main()
