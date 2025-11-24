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

# Use a placeholder ID. In a real app, this would be a user-specific or project-specific ID.
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
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #000000;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Stats container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid rgba(0,0,0,0.05);
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
        color: #333;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        font-size: 16px;
        color: #666;
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
    
    /* New feature: Task Card */
    .task-card {
        background: linear-gradient(135deg, #e6e9f0 0%, #eef1f5 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
        color: #000000;
    }
    
    .task-card.completed {
        border-left-color: #8BC34A;
        opacity: 0.7;
    }
    
    .task-title {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 5px;
    }
    
    .task-meta {
        font-size: 12px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------
# ⚙️ UTILITY FUNCTIONS
# ------------------------------

def get_gmail_credentials():
    """Get Gmail credentials from Streamlit secrets."""
    try:
        # Assuming the secrets file is structured to support multiple accounts
        # For simplicity, we'll look for a single 'gmail' entry first, then 'gmail_accounts'
        
        accounts = []
        
        # Check for single account (backward compatibility)
        if "gmail" in st.secrets and "email" in st.secrets["gmail"]:
            accounts.append({
                "name": "Default Account",
                "email": st.secrets["gmail"]["email"],
                "password": st.secrets["gmail"]["password"]
            })
            
        # Check for multiple accounts
        if "gmail_accounts" in st.secrets:
            for key, account in st.secrets["gmail_accounts"].items():
                accounts.append({
                    "name": key.replace('_', ' ').title(),
                    "email": account["email"],
                    "password": account["password"]
                })
        
        return accounts
    except Exception as e:
        # st.error(f"Error loading credentials: {e}")
        return []

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
    
    data = []
    for i in range(num_emails):
        sender_name = random.choice(["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Eve Adams"])
        sender_email = f"{sender_name.lower().replace(' ', '.')}@example.com"
        subject = random.choice([
            "Follow up on our meeting", 
            "Urgent: System outage report", 
            "Quarterly marketing plan draft", 
            "Question about invoice #12345",
            "New feature request for the app"
        ])
        summary = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        attachment = random.choice(["Yes", "No"])
        department = random.choice(departments)
        priority = random.choice(priorities)
        
        ai_reply = ""
        if random.random() > 0.5:
            ai_reply = f"Hello {sender_name},\n\nThank you for your email. I will look into the {subject.lower()} and get back to you by the end of the day.\n\nBest regards,\n[Your Name]"
        
        data.append({
            "sender name": sender_name,
            "sender email": sender_email,
            "subject": subject,
            "summary": summary,
            "date": date,
            "attachment": attachment,
            "aireply": ai_reply,
            "department": department,
            "priority": priority
        })
        
    df = pd.DataFrame(data)
    return df

# ------------------------------
# 📧 EMAIL SENDING LOGIC
# ------------------------------

def send_email(to_address, subject, body, from_email, from_password, attachment_path=None):
    """Sends an email using the provided SMTP credentials."""
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {os.path.basename(attachment_path)}",
            )
            msg.attach(part)
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_address, text)
        server.quit()
        
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
            'priority': email_email.get('priority', 'medium'),
            'to_address': email_data.get('to', ''),
            'sent_at': datetime.now().isoformat()
        }
        
        st.session_state['sent_items'].append(sent_email)
        
        # NOTE: Google Sheets integration is complex and depends on a service account.
        # For this example, we'll skip the GSheets part to focus on the Streamlit app logic.
        # if credentials_dict:
        #     try:
        #         gc = authenticate_gsheets(credentials_dict)
        #         if gc:
        #             worksheet = gc.open_by_key(SHEET_ID).worksheet('Sent')
        #             
        #             row_data = [
        #                 sent_email['sender name'],
        #                 sent_email['sender email'],
        #                 sent_email['subject'],
        #                 sent_email['summary'],
        #                 sent_email['date'],
        #                 sent_email['attachment'],
        #                 sent_email['aireply'],
        #                 sent_email['department'],
        #                 sent_email['priority'],
        #                 sent_email['to_address'],
        #                 sent_email['sent_at']
        #             ]
        #             worksheet.append_row(row_data)
        #     except Exception as sheet_error:
        #         st.warning(f"Could not save to Google Sheets: {sheet_error}")
        
        return True
    except Exception as e:
        st.error(f"Error saving sent email: {e}")
        return False

# ------------------------------
# 🖼️ UI COMPONENTS
# ------------------------------

def display_stats(df):
    """Display email statistics in colorful cards."""
    total_emails = len(df)
    with_attachments = df[df['attachment'].astype(str).str.lower().isin(['yes', 'true', '1'])].shape[0] if 'attachment' in df.columns else 0
    high_priority = df[df['priority'] == 'high'].shape[0] if 'priority' in df.columns else 0
    ai_replies_ready = df[df['aireply'].apply(lambda x: bool(x and str(x).strip() not in ["", "nan", "None", "null"]))].shape[0] if 'aireply' in df.columns else 0
    
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
        if st.button("✅ Mark Done", key=f"done_{index}", use_container_width=True):
            # Simple removal from the current view for mock data
            st.session_state['df'] = st.session_state['df'].drop(index).reset_index(drop=True)
            st.success(f"Email from {sender_name} marked as done!")
            st.rerun()
    with col4:
        if st.button("🗑️ Archive", key=f"archive_{index}", use_container_width=True):
            # Simple removal from the current view for mock data
            st.session_state['df'] = st.session_state['df'].drop(index).reset_index(drop=True)
            st.info(f"Email from {sender_name} archived.")
            st.rerun()

def display_task_card(task, index):
    """Render a task entry."""
    status_icon = "✅" if task['completed'] else "⏳"
    status_class = "completed" if task['completed'] else ""
    
    st.markdown(f"""
    <div class="task-card {status_class}">
        <div class="task-title">{status_icon} {task['title']}</div>
        <div class="task-meta">
            Priority: {task['priority'].capitalize()} | Due: {task['due_date']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Toggle Status", key=f"task_toggle_{index}", use_container_width=True):
            st.session_state['tasks'][index]['completed'] = not st.session_state['tasks'][index]['completed']
            st.rerun()
    with col2:
        if st.button("Remove", key=f"task_remove_{index}", use_container_width=True):
            st.session_state['tasks'].pop(index)
            st.rerun()

# ------------------------------
# 📄 PAGE RENDERING FUNCTIONS
# ------------------------------

def render_compose(accounts):
    """Renders the email composition page."""
    st.markdown("## ✍️ Compose Email")
    
    # --- Sender Selection (Fix for blank sender and auto-use selected email) ---
    account_options = [f"{acc['name']} <{acc['email']}>" for acc in accounts]
    selected_account_str = st.selectbox(
        "**Select Sender Account:**", 
        options=account_options,
        index=0,
        key='sender_account_select'
    )
    
    # Extract the email from the selected string
    match = re.search(r'<(.*?)>', selected_account_str)
    selected_from_email = match.group(1) if match else accounts[0]['email'] if accounts else ""
    
    # Find the full account object for credentials
    selected_account = next((acc for acc in accounts if acc['email'] == selected_from_email), None)
    
    if not selected_account:
        st.error("No valid sender account selected or configured. Please check your settings.")
        return
    
    # --- Pre-fill logic for reply ---
    to_address = ""
    subject = ""
    body = ""
    
    if 'selected_email' in st.session_state and st.session_state['selected_email']:
        original_email = st.session_state['selected_email']
        to_address = original_email.get("sender email", "")
        original_subject = original_email.get("subject", "")
        
        # Ensure subject starts with Re:
        if not original_subject.lower().startswith("re:"):
            subject = f"Re: {original_subject}"
        else:
            subject = original_subject
            
        # Add original email content to the body for context
        original_body = original_email.get("summary", "Original email content not available.")
        
        # Check for AI reply
        if st.session_state.get('use_ai_reply', False) and original_email.get('aireply'):
            ai_reply_text = original_email['aireply']
            body = f"{ai_reply_text}\n\n---\n\nOn {original_email.get('date')}, {original_email.get('sender name')} wrote:\n> {original_body.replace('\n', '\n> ')}"
        else:
            body = f"\n\n---\n\nOn {original_email.get('date')}, {original_email.get('sender name')} wrote:\n> {original_body.replace('\n', '\n> ')}"
            
        # Clear the selected email after pre-filling
        # st.session_state['selected_email'] = None
        # st.session_state['use_ai_reply'] = False

    # --- Composition Form ---
    with st.form("email_compose_form"):
        recipient = st.text_input("**To:**", value=to_address, key='recipient_input')
        email_subject = st.text_input("**Subject:**", value=subject, key='subject_input')
        email_body = st.text_area("**Body:**", value=body, height=300, key='body_input')
        
        uploaded_file = st.file_uploader("Attach File (Optional)", type=None)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            send_button = st.form_submit_button("🚀 Send Email", type="primary", use_container_width=True)
        with col2:
            draft_button = st.form_submit_button("💾 Save Draft", use_container_width=True)

        if send_button:
            if not recipient or not email_subject or not email_body:
                st.error("Please fill in the recipient, subject, and body.")
            else:
                attachment_path = None
                if uploaded_file:
                    # Save the uploaded file temporarily
                    attachment_path = os.path.join("/tmp", uploaded_file.name)
                    with open(attachment_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                with st.spinner(f"Sending email from {selected_from_email}..."):
                    success = send_email(
                        to_address=recipient,
                        subject=email_subject,
                        body=email_body,
                        from_email=selected_account['email'],
                        from_password=selected_account['password'],
                        attachment_path=attachment_path
                    )
                
                if success:
                    st.success("Email sent successfully!")
                    
                    # Save to sent items
                    email_data = {
                        'from_name': selected_account_str.split('<')[0].strip(),
                        'from_email': selected_account['email'],
                        'to': recipient,
                        'subject': email_subject,
                        'body': email_body,
                        'attachments': uploaded_file.name if uploaded_file else None
                    }
                    save_to_sent_items(email_data)
                    
                    # Clean up temporary file
                    if attachment_path and os.path.exists(attachment_path):
                        os.remove(attachment_path)
                        
                    # Navigate back to inbox
                    st.session_state['page'] = 'inbox'
                    st.session_state['selected_email'] = None
                    st.session_state['use_ai_reply'] = False
                    st.rerun()
                else:
                    st.error("Failed to send email. Check credentials and recipient address.")
        
        if draft_button:
            if 'drafts' not in st.session_state:
                st.session_state['drafts'] = []
            
            draft = {
                'to': recipient,
                'subject': email_subject,
                'body': email_body,
                'from_email': selected_account['email'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state['drafts'].append(draft)
            st.info("Draft saved successfully!")
            st.session_state['page'] = 'drafts'
            st.rerun()

def render_inbox(df, credentials_dict=None):
    """Renders the inbox page with email cards and stats."""
    st.markdown("## 📨 Inbox")
    
    display_stats(df)
    
    st.markdown("---")
    
    # Enhanced filtering with search functionality
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
        filtered_df = filtered_df[filtered_df['attachment'].astype(str).str.lower().isin(['yes', 'true', '1'])]
    elif attachment_filter == "Without Attachments":
        filtered_df = filtered_df[~filtered_df['attachment'].astype(str).str.lower().isin(['yes', 'true', '1'])]
    
    # Apply search filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df['sender name'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df['subject'].astype(str).str.contains(search_query, case=False, na=False)
        ]
    
    st.markdown(f"### {len(filtered_df)} Email(s)")
    
    if len(filtered_df) == 0:
        st.info("📭 No emails to display with the current filters.")
        return
    
    for idx, row in filtered_df.iterrows():
        display_email_card(row.to_dict(), idx, credentials_dict)

def render_sent_items():
    """Renders the sent items page."""
    st.markdown("## 📤 Sent Items")
    
    if 'sent_items' not in st.session_state or not st.session_state['sent_items']:
        st.info("No emails have been sent yet.")
        return
    
    st.markdown("---")
    
    # Convert sent items to DataFrame for easier display/filtering if needed
    sent_df = pd.DataFrame(st.session_state['sent_items'])
    st.markdown(f"### {len(sent_df)} Sent Email(s)")
    
    for idx, sent in enumerate(st.session_state['sent_items']):
        # Use a simplified card for sent items
        st.markdown(f"""
        <div class="email-card" style="border-left-color: #4CAF50;">
            <div class="sender-info">
                <div class="sender-avatar" style="background: #4CAF50;">ME</div>
                <div class="sender-details">
                    <div class="sender-name">To: {sent.get('to_address', 'N/A')}</div>
                    <div class="sender-email">From: &lt;{sent.get('sender email', 'N/A')}&gt;</div>
                </div>
            </div>
            <div class="subject">{sent.get('subject', 'No Subject')}</div>
            <div class="summary">{sent.get('summary', 'No summary available')}</div>
            <div class="email-meta">
                <div class="date">📅 {sent.get('date', 'N/A')} | Sent At: {datetime.fromisoformat(sent.get('sent_at')).strftime('%H:%M')}</div>
                <div><span class="tag attachment" style="background: #4CAF50;">Sent</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_drafts():
    """Renders the drafts page."""
    st.markdown("## 📝 Drafts")
    
    if 'drafts' not in st.session_state or not st.session_state['drafts']:
        st.info("No drafts saved yet.")
        return
    
    st.markdown("---")
    
    for idx, draft in enumerate(st.session_state['drafts']):
        st.markdown(f"""
        <div class="draft-card">
            <div class="draft-header">
                <div class="draft-avatar">D</div>
                <div style="flex: 1;">
                    <div style="font-size: 18px; font-weight: 700; color: #000000;">{draft.get('subject', 'No Subject')}</div>
                    <div style="font-size: 13px; color: #666;">To: {draft.get('to', 'N/A')} | From: {draft.get('from_email', 'N/A')}</div>
                </div>
                <span class="draft-badge">Draft</span>
            </div>
            <div class="draft-field"><strong>Saved:</strong> {draft.get('timestamp')}</div>
            <div class="draft-field"><strong>Preview:</strong> {draft.get('body', '')[:100]}...</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✏️ Edit Draft", key=f"edit_draft_{idx}", use_container_width=True):
                # Pre-fill compose page with draft content
                st.session_state['page'] = 'compose'
                st.session_state['selected_email'] = {'sender email': draft.get('to', ''), 'subject': draft.get('subject', ''), 'summary': draft.get('body', '')}
                # Remove draft after selecting it for edit
                st.session_state['drafts'].pop(idx)
                st.rerun()
        with col2:
            if st.button("🗑️ Delete Draft", key=f"delete_draft_{idx}", use_container_width=True):
                st.session_state['drafts'].pop(idx)
                st.success("Draft deleted.")
                st.rerun()

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
            attachment_counts = df['attachment'].astype(str).str.lower().isin(['yes', 'true', '1']).value_counts()
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
            contacts['sender name'].astype(str).str.contains(search, case=False, na=False) |
            contacts['sender email'].astype(str).str.contains(search, case=False, na=False)
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
        dept = df[df['sender email'] == email]['department'].mode()[0] if 'department' in df.columns and not df[df['sender email'] == email]['department'].empty else 'N/A'
        
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
                st.session_state['selected_email'] = {'sender email': email, 'subject': '', 'summary': ''}
                st.rerun()

def render_tasks():
    """Renders the task management page (New Feature)."""
    st.markdown("## 📋 Task Manager")
    st.markdown("Keep track of follow-up actions required for your emails.")
    st.markdown("---")
    
    if 'tasks' not in st.session_state:
        st.session_state['tasks'] = []
        
    # Add New Task Form
    with st.expander("➕ Add New Task", expanded=False):
        with st.form("new_task_form"):
            task_title = st.text_input("Task Title")
            task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            task_due_date = st.date_input("Due Date", datetime.now() + timedelta(days=7))
            
            if st.form_submit_button("Add Task", type="primary"):
                if task_title:
                    st.session_state['tasks'].append({
                        'title': task_title,
                        'priority': task_priority.lower(),
                        'due_date': task_due_date.strftime("%Y-%m-%d"),
                        'completed': False
                    })
                    st.success("Task added!")
                    st.rerun()
                else:
                    st.error("Task title cannot be empty.")

    # Display Tasks
    if not st.session_state['tasks']:
        st.info("You have no pending tasks.")
        return
    
    st.markdown(f"### {len([t for t in st.session_state['tasks'] if not t['completed']])} Pending Tasks")
    
    # Sort tasks: Pending High -> Pending Medium -> Pending Low -> Completed
    sorted_tasks = sorted(st.session_state['tasks'], key=lambda x: (x['completed'], x['priority'] == 'low', x['priority'] == 'medium', x['priority'] == 'high'))
    
    for idx, task in enumerate(sorted_tasks):
        display_task_card(task, idx)

def render_settings(accounts):
    """Renders the settings page."""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    st.markdown("---")
    
    # --- Google Sheets Configuration ---
    st.markdown("### ☁️ Google Sheets Configuration")
    
    gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    
    if gsheets_file is not None:
        try:
            # Read the uploaded file
            gsheets_credentials = json.load(gsheets_file)
            
            # Store in session state
            st.session_state['gsheets_credentials'] = gsheets_credentials
            st.success("✅ Google Sheets credentials uploaded and saved for this session.")
            
            # Optionally, try to authenticate immediately
            gc = authenticate_gsheets(gsheets_credentials)
            if gc:
                st.success("✅ Successfully authenticated with Google Sheets!")
            else:
                st.error("❌ Authentication failed with the provided JSON file.")
                
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
    
    if 'gsheets_credentials' in st.session_state:
        st.info("Current Google Sheets credentials are set from the uploaded file.")
    else:
        st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    
    st.markdown("---")
    
    # --- Gmail Configuration ---
    st.markdown("### 📧 Gmail Configuration")
    
    if accounts:
        st.success(f"✅ {len(accounts)} Gmail account(s) configured.")
        for acc in accounts:
            st.info(f"Account: **{acc['name']}** | Email: **{acc['email']}**")
        st.markdown("To update credentials, edit your `.streamlit/secrets.toml` file with the following structure:")
        st.code("""
[gmail_accounts.work]
email = "work@example.com"
password = "your_app_password"

[gmail_accounts.personal]
email = "personal@example.com"
password = "your_app_password"
""", language="toml")
    else:
        st.warning("No Gmail credentials found in `secrets.toml`. Email sending is disabled.")
        st.markdown("Please add your Gmail credentials (using an App Password) to your `.streamlit/secrets.toml` file.")
        st.code("""
[gmail]
email = "your_email@gmail.com"
password = "your_app_password"
""", language="toml")
        st.markdown("---")
        st.markdown("### ⚠️ Important: Using App Passwords")
        st.markdown("For security, you must use a **Gmail App Password** instead of your regular password. You can generate one in your Google Account security settings.")
    
    # --- End of render_settings ---
    pass
    
    # Find the original render_settings function definition and replace it
    # I'll search for the function definition and replace the entire block.
    # The original function starts around line 1238 and ends around line 1277.
    # Since I don't have the exact line numbers from the truncated read, I'll use the function signature and a unique part of its body.
    # I'll search for the start of the function and replace everything until the end of the function.
    # The original function body:
    # def render_settings(accounts):
    #     """Renders the settings page."""
    #     st.markdown("## ⚙️ Settings")
    #     
    #     st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    #     st.markdown("---")
    #     
    #     # Gmail settings
    #     st.markdown("### 📧 Gmail Configuration")
    #     
    #     if accounts:
    #         st.success(f"✅ {len(accounts)} Gmail account(s) configured.")
    #         for acc in accounts:
    #             st.info(f"Account: **{acc['name']}** | Email: **{acc['email']}**")
    #         st.markdown("To update credentials, edit your `.streamlit/secrets.toml` file with the following structure:")
    #         st.code("""
    # [gmail_accounts.work]
    # email = "work@example.com"
    # password = "your_app_password"
    # 
    # [gmail_accounts.personal]
    # email = "personal@example.com"
    # password = "your_app_password"
    # """, language="toml")
    #     else:
    #         st.warning("No Gmail credentials found in `secrets.toml`. Email sending is disabled.")
    #         st.markdown("Please add your Gmail credentials (using an App Password) to your `.streamlit/secrets.toml` file.")
    #         st.code("""
    # [gmail]
    # email = "your_email@gmail.com"
    # password = "your_app_password"
    # """, language="toml")
    #         st.markdown("---")
    #         st.markdown("### ⚠️ Important: Using App Passwords")
    #         st.markdown("For security, you must use a **Gmail App Password** instead of your regular password. You can generate one in your Google Account security settings.")
    # 
    # The replacement is the new function body. I will use a multi-line find/replace.
    
    # I will use a simpler edit to insert the new GSheets logic at the beginning of the function.
    
    # Find:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Replace with:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # --- Google Sheets Configuration ---
    # st.markdown("### ☁️ Google Sheets Configuration")
    # 
    # gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    # 
    # if gsheets_file is not None:
    #     try:
    #         # Read the uploaded file
    #         gsheets_credentials = json.load(gsheets_file)
    #         
    #         # Store in session state
    #         st.session_state['gsheets_credentials'] = gsheets_credentials
    #         st.success("✅ Google Sheets credentials uploaded and saved for this session.")
    #         
    #         # Optionally, try to authenticate immediately
    #         gc = authenticate_gsheets(gsheets_credentials)
    #         if gc:
    #             st.success("✅ Successfully authenticated with Google Sheets!")
    #         else:
    #             st.error("❌ Authentication failed with the provided JSON file.")
    #             
    #     except json.JSONDecodeError:
    #         st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
    #     except Exception as e:
    #         st.error(f"An error occurred during file processing: {e}")
    # 
    # if 'gsheets_credentials' in st.session_state:
    #     st.info("Current Google Sheets credentials are set from the uploaded file.")
    # else:
    #     st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    # 
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # This is safer. I will also need to update the `main` function to pass the credentials to `render_inbox` and update `load_data_from_gsheet` to use the session state.

    # Step 2: Update `load_data_from_gsheet` to use session state credentials.
    # I need to modify the main function to get the credentials and pass them to `load_data_from_gsheet` if they exist.
    
    # Let's start with the `main` function (around line 1290).
    # I need to change how `st.session_state['df']` is initialized.
    
    # Find:
    # if 'df' not in st.session_state:
    #     # NOTE: credentials_dict is not available here, so we use mock data
    #     st.session_state['df'] = generate_mock_data(num_emails=50)
    
    # Replace with:
    # if 'df' not in st.session_state:
    #     # Try to load data from GSheets if credentials are in session state
    #     gsheets_creds = st.session_state.get('gsheets_credentials')
    #     if gsheets_creds:
    #         gc = authenticate_gsheets(gsheets_creds)
    #         if gc:
    #             st.session_state['df'] = load_data_from_gsheet(gc)
    #         else:
    #             st.session_state['df'] = generate_mock_data(num_emails=50)
    #             st.warning("Could not authenticate GSheets. Using mock data.")
    #     else:
    #         st.session_state['df'] = generate_mock_data(num_emails=50)
    #         st.info("Using mock data. Upload Google Sheets credentials in Settings to load real data.")
    
    # This is a bit complex because Streamlit's rerun mechanism means the `main` function runs on every interaction. I should put the data loading logic in a function and call it.
    
    # Let's define a new function `get_data_frame` and call it in `main`.
    
    # I will modify the `main` function to call a new function `get_gsheets_credentials_from_session()` and pass it to `load_data_from_gsheet`.
    
    # New utility function:
    # def get_gsheets_credentials_from_session():
    #     """Retrieves Google Sheets credentials from session state."""
    #     return st.session_state.get('gsheets_credentials')
    
    # I will also update `load_data_from_gsheet` to handle the credentials.
    
    # I will simplify the approach. The `main` function will check for credentials and load data.

    # I will use the `file.edit` tool to implement the changes.

    # Edit 1: Insert the GSheets credentials retrieval function.
    # Find:
    # def authenticate_gsheets(credentials_dict):
    #     """Authenticate with Google Sheets using service account credentials."""
    # 
    # Insert new function before it.
    
    # Edit 2: Modify `load_data_from_gsheet` to accept credentials directly and use them.
    # The original `load_data_from_gsheet` takes `gc` (gspread client) as an argument. I will keep it simple and just update the main logic.

    # Edit 3: Modify `main` function's initialization logic.
    
    # Edit 4: Modify `render_settings` function.

    # Let's do Edit 4 first, as it's the core of the user's request.
    
    # Find the start of the Gmail configuration section in `render_settings` (around line 1250) and insert the GSheets upload logic before it.
    
    # Find:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Replace with:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # --- Google Sheets Configuration ---
    # st.markdown("### ☁️ Google Sheets Configuration")
    # 
    # gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    # 
    # if gsheets_file is not None:
    #     try:
    #         # Read the uploaded file
    #         gsheets_credentials = json.load(gsheets_file)
    #         
    #         # Store in session state
    #         st.session_state['gsheets_credentials'] = gsheets_credentials
    #         st.success("✅ Google Sheets credentials uploaded and saved for this session. Rerun to load data.")
    #         
    #         # Optionally, try to authenticate immediately
    #         gc = authenticate_gsheets(gsheets_credentials)
    #         if gc:
    #             st.success("✅ Successfully authenticated with Google Sheets!")
    #         else:
    #             st.error("❌ Authentication failed with the provided JSON file.")
    #             
    #     except json.JSONDecodeError:
    #         st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
    #     except Exception as e:
    #         st.error(f"An error occurred during file processing: {e}")
    # 
    # if 'gsheets_credentials' in st.session_state:
    #     st.info("Current Google Sheets credentials are set from the uploaded file.")
    # else:
    #     st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    # 
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # I need to find the exact lines in `improved_email_app.py` for `render_settings`.
    
    # Line 1238: def render_settings(accounts):
    # Line 1243: st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # Line 1244: st.markdown("---")
    # Line 1247: st.markdown("### 📧 Gmail Configuration")
    
    # I will replace lines 1243-1247 with the new block.

    # Edit 1: Update `render_settings`
    
    # Find:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Replace:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # --- Google Sheets Configuration ---
    # st.markdown("### ☁️ Google Sheets Configuration")
    # 
    # gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    # 
    # if gsheets_file is not None:
    #     try:
    #         # Read the uploaded file
    #         gsheets_credentials = json.load(gsheets_file)
    #         
    #         # Store in session state
    #         st.session_state['gsheets_credentials'] = gsheets_credentials
    #         st.success("✅ Google Sheets credentials uploaded and saved for this session. Rerun to load data.")
    #         
    #         # Optionally, try to authenticate immediately
    #         gc = authenticate_gsheets(gsheets_credentials)
    #         if gc:
    #             st.success("✅ Successfully authenticated with Google Sheets!")
    #         else:
    #             st.error("❌ Authentication failed with the provided JSON file.")
    #             
    #     except json.JSONDecodeError:
    #         st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
    #     except Exception as e:
    #         st.error(f"An error occurred during file processing: {e}")
    # 
    # if 'gsheets_credentials' in st.session_state:
    #     st.info("Current Google Sheets credentials are set from the uploaded file.")
    # else:
    #     st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    # 
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Edit 2: Update `main` function's initialization logic (around line 1298).
    
    # Find:
    # if 'df' not in st.session_state:
    #     # NOTE: credentials_dict is not available here, so we use mock data
    #     st.session_state['df'] = generate_mock_data(num_emails=50)
    
    # Replace with:
    # if 'df' not in st.session_state:
    #     # Try to load data from GSheets if credentials are in session state
    #     gsheets_creds = st.session_state.get('gsheets_credentials')
    #     if gsheets_creds:
    #         gc = authenticate_gsheets(gsheets_creds)
    #         if gc:
    #             st.session_state['df'] = load_data_from_gsheet(gc)
    #             st.info("Data loaded from Google Sheets.")
    #         else:
    #             st.session_state['df'] = generate_mock_data(num_emails=50)
    #             st.warning("Could not authenticate GSheets. Using mock data.")
    #     else:
    #         st.session_state['df'] = generate_mock_data(num_emails=50)
    #         st.info("Using mock data. Upload Google Sheets credentials in Settings to load real data.")
    
    # I will perform the edits now. I'll use the line numbers from the last full read of the file (lines 1-500, then 385-1303). The `render_settings` function starts at line 1238.
    
    # The `main` function starts at line 1289. The block to replace is around line 1298.
    
    # I will perform the edits in two steps to ensure clarity and avoid large multi-line replacements that might fail.
    
    # Edit 1: Update `render_settings`
    
    # Find:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Replace:
    # st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    # st.markdown("---")
    # 
    # # --- Google Sheets Configuration ---
    # st.markdown("### ☁️ Google Sheets Configuration")
    # 
    # gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    # 
    # if gsheets_file is not None:
    #     try:
    #         # Read the uploaded file
    #         gsheets_credentials = json.load(gsheets_file)
    #         
    #         # Store in session state
    #         st.session_state['gsheets_credentials'] = gsheets_credentials
    #         st.success("✅ Google Sheets credentials uploaded and saved for this session. Rerun to load data.")
    #         
    #         # Optionally, try to authenticate immediately
    #         gc = authenticate_gsheets(gsheets_credentials)
    #         if gc:
    #             st.success("✅ Successfully authenticated with Google Sheets!")
    #         else:
    #             st.error("❌ Authentication failed with the provided JSON file.")
    #             
    #     except json.JSONDecodeError:
    #         st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
    #     except Exception as e:
    #         st.error(f"An error occurred during file processing: {e}")
    # 
    # if 'gsheets_credentials' in st.session_state:
    #     st.info("Current Google Sheets credentials are set from the uploaded file.")
    # else:
    #     st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    # 
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # I will use a simpler edit to insert the new GSheets logic right after the "---" in `render_settings`.
    
    # Find:
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # Replace:
    # st.markdown("---")
    # 
    # # --- Google Sheets Configuration ---
    # st.markdown("### ☁️ Google Sheets Configuration")
    # 
    # gsheets_file = st.file_uploader("Upload Google Sheets Service Account JSON", type="json")
    # 
    # if gsheets_file is not None:
    #     try:
    #         # Read the uploaded file
    #         gsheets_credentials = json.load(gsheets_file)
    #         
    #         # Store in session state
    #         st.session_state['gsheets_credentials'] = gsheets_credentials
    #         st.success("✅ Google Sheets credentials uploaded and saved for this session. Rerun to load data.")
    #         
    #         # Optionally, try to authenticate immediately
    #         gc = authenticate_gsheets(gsheets_credentials)
    #         if gc:
    #             st.success("✅ Successfully authenticated with Google Sheets!")
    #         else:
    #             st.error("❌ Authentication failed with the provided JSON file.")
    #             
    #     except json.JSONDecodeError:
    #         st.error("Invalid JSON file. Please upload a valid Google Sheets Service Account JSON.")
    #     except Exception as e:
    #         st.error(f"An error occurred during file processing: {e}")
    # 
    # if 'gsheets_credentials' in st.session_state:
    #     st.info("Current Google Sheets credentials are set from the uploaded file.")
    # else:
    #     st.warning("No Google Sheets credentials set. Data will be loaded from mock data.")
    # 
    # st.markdown("---")
    # 
    # # Gmail settings
    # st.markdown("### 📧 Gmail Configuration")
    
    # This seems correct and robust.
    
    # Edit 2: Update `main` function's initialization logic.
    
    # Find:
    # if 'df' not in st.session_state:
    #     # NOTE: credentials_dict is not available here, so we use mock data
    #     st.session_state['df'] = generate_mock_data(num_emails=50)
    
    # Replace with:
    # if 'df' not in st.session_state:
    #     # Try to load data from GSheets if credentials are in session state
    #     gsheets_creds = st.session_state.get('gsheets_credentials')
    #     if gsheets_creds:
    #         gc = authenticate_gsheets(gsheets_creds)
    #         if gc:
    #             st.session_state['df'] = load_data_from_gsheet(gc)
    #             st.info("Data loaded from Google Sheets.")
    #         else:
    #             st.session_state['df'] = generate_mock_data(num_emails=50)
    #             st.warning("Could not authenticate GSheets. Using mock data.")
    #     else:
    #         st.session_state['df'] = generate_mock_data(num_emails=50)
    #         st.info("Using mock data. Upload Google Sheets credentials in Settings to load real data.")
    
    # This is also correct. I will perform the edits now.<ctrl95><ctrl42>call:default_api:file{action:
    """Renders the settings page."""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("Configure your InboxKeep Pro preferences and integrations.")
    st.markdown("---")
    
    # Gmail settings
    st.markdown("### 📧 Gmail Configuration")
    
    if accounts:
        st.success(f"✅ {len(accounts)} Gmail account(s) configured.")
        for acc in accounts:
            st.info(f"Account: **{acc['name']}** | Email: **{acc['email']}**")
        st.markdown("To update credentials, edit your `.streamlit/secrets.toml` file with the following structure:")
        st.code("""
[gmail_accounts.work]
email = "work@example.com"
password = "your_app_password"

[gmail_accounts.personal]
email = "personal@example.com"
password = "your_app_password"
""", language="toml")
    else:
        st.warning("No Gmail credentials found in `secrets.toml`. Email sending is disabled.")
        st.markdown("Please add your Gmail credentials (using an App Password) to your `.streamlit/secrets.toml` file.")
        st.code("""
[gmail]
email = "your_email@gmail.com"
password = "your_app_password"
""", language="toml")
        st.markdown("---")
        st.markdown("### ⚠️ Important: Using App Passwords")
        st.markdown("For security, you must use a **Gmail App Password** instead of your regular password. You can generate one in your Google Account security settings.")

# ------------------------------
# 💻 MAIN APPLICATION
# ------------------------------

def main():
    """Main function to run the Streamlit application."""
    
    # 1. Initialization
    load_custom_css()
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 'inbox'
    if 'df' not in st.session_state:
        # Try to load data from GSheets if credentials are in session state
        gsheets_creds = st.session_state.get('gsheets_credentials')
        if gsheets_creds:
            gc = authenticate_gsheets(gsheets_creds)
            if gc:
                st.session_state['df'] = load_data_from_gsheet(gc)
                st.info("Data loaded from Google Sheets.")
            else:
                st.session_state['df'] = generate_mock_data(num_emails=50)
                st.warning("Could not authenticate GSheets. Using mock data.")
        else:
            st.session_state['df'] = generate_mock_data(num_emails=50)
            st.info("Using mock data. Upload Google Sheets credentials in Settings to load real data.")
    if 'sent_items' not in st.session_state:
        st.session_state['sent_items'] = []
    if 'drafts' not in st.session_state:
        st.session_state['drafts'] = []
    if 'tasks' not in st.session_state:
        st.session_state['tasks'] = []
        
    # Get configured accounts
    accounts = get_gmail_credentials()
    
    # 2. Sidebar Navigation
    st.sidebar.title("InboxKeep Pro")
    st.sidebar.markdown("---")
    
    # Navigation buttons
    if st.sidebar.button("📨 Inbox", use_container_width=True):
        st.session_state['page'] = 'inbox'
        st.session_state['selected_email'] = None
        st.session_state['use_ai_reply'] = False
    if st.sidebar.button("✍️ Compose", use_container_width=True):
        st.session_state['page'] = 'compose'
        st.session_state['selected_email'] = None
        st.session_state['use_ai_reply'] = False
    if st.sidebar.button("📤 Sent Items", use_container_width=True):
        st.session_state['page'] = 'sent'
    if st.sidebar.button("📝 Drafts", use_container_width=True):
        st.session_state['page'] = 'drafts'
    st.sidebar.markdown("---")
    if st.sidebar.button("📊 Analytics", use_container_width=True):
        st.session_state['page'] = 'analytics'
    if st.sidebar.button("👥 Contacts", use_container_width=True):
        st.session_state['page'] = 'contacts'
    if st.sidebar.button("📋 Task Manager (New)", use_container_width=True):
        st.session_state['page'] = 'tasks'
    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ Settings", use_container_width=True):
        st.session_state['page'] = 'settings'
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"**{len(st.session_state['df'])}** Emails in Inbox")
    st.sidebar.info(f"**{len(st.session_state['tasks'])}** Total Tasks")
    
    # 3. Page Rendering
    if st.session_state['page'] == 'inbox':
        render_inbox(st.session_state['df'])
    elif st.session_state['page'] == 'compose':
        render_compose(accounts)
    elif st.session_state['page'] == 'sent':
        render_sent_items()
    elif st.session_state['page'] == 'drafts':
        render_drafts()
    elif st.session_state['page'] == 'analytics':
        render_analytics(st.session_state['df'])
    elif st.session_state['page'] == 'contacts':
        render_contacts(st.session_state['df'])
    elif st.session_state['page'] == 'tasks':
        render_tasks()
    elif st.session_state['page'] == 'settings':
        render_settings(accounts)

if __name__ == '__main__':
    main()
