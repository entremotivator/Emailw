import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import requests
import base64
from email.mime.text import MIMEText
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Page config
st.set_page_config(
    page_title="Email Management System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== OPENAI UTILS ====================
def get_openai_client():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise Exception('OPENAI_API_KEY not found in environment variables')
    return OpenAI(api_key=api_key)

def generate_email_draft(subject, sender_name, email_body, template_type="Professional", tone="Neutral", length="Medium", custom_instructions=""):
    try:
        client = get_openai_client()
        
        prompt = f"""You are an AI assistant helping to draft professional email responses.

Original Email Details:
From: {sender_name}
Subject: {subject}
Body: {email_body}

Template Style: {template_type}
Tone: {tone}
Length: {length}
{f'Additional Instructions: {custom_instructions}' if custom_instructions else ''}

Generate a professional, concise, and appropriate email reply. Keep it friendly and to the point.
Only provide the email body text, no subject line or greetings like "Dear [Name]"."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates professional email responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        draft = response.choices[0].message.content
        return draft.strip() if draft else "No draft generated"
    except Exception as e:
        return f"Error generating draft: {str(e)}"

def classify_email(subject, sender_name, email_body):
    try:
        client = get_openai_client()
        
        prompt = f"""Classify the following email into ONE of these categories:
- Business
- Personal
- Marketing
- Notification
- Support
- Urgent
- Newsletter
- Spam

Email Details:
From: {sender_name}
Subject: {subject}
Body: {email_body}

Respond with ONLY the category name, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies emails into categories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        tag = response.choices[0].message.content
        return tag.strip() if tag else "Unclassified"
    except Exception as e:
        return "Unclassified"

def batch_generate_drafts_and_tags(emails_df):
    results = []
    
    for _, email in emails_df.iterrows():
        subject = email.get('subject', 'No Subject')
        sender_name = email.get('sender name', 'Unknown')
        summary = email.get('summary', '')
        
        draft = generate_email_draft(subject, sender_name, summary)
        tag = classify_email(subject, sender_name, summary)
        
        results.append({
            'draft': draft,
            'tag': tag
        })
    
    return results

# ==================== GMAIL UTILS ====================
def get_gmail_access_token():
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('X_REPLIT_TOKEN not found for repl/depl')
    
    url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-mail'
    
    response = requests.get(
        url,
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    data = response.json()
    connection_settings = data.get('items', [])[0] if data.get('items') else None
    
    if not connection_settings:
        raise Exception('Gmail not connected')
    
    access_token = (
        connection_settings.get('settings', {}).get('access_token') or 
        connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token')
    )
    
    if not access_token:
        raise Exception('Gmail access token not found')
    
    return access_token

def get_gmail_service():
    access_token = get_gmail_access_token()
    credentials = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=credentials)
    return service

def fetch_emails(max_results=50):
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            email_data = parse_email(message)
            emails.append(email_data)
        
        return emails
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return []

def parse_email(message):
    headers = message['payload']['headers']
    
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
    
    sender_email = sender
    sender_name = sender
    if '<' in sender and '>' in sender:
        sender_name = sender.split('<')[0].strip()
        sender_email = sender.split('<')[1].split('>')[0].strip()
    
    body = get_email_body(message['payload'])
    
    has_attachments = 'No'
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part.get('filename'):
                has_attachments = 'Yes'
                break
    
    try:
        date_obj = datetime.strptime(date.split('(')[0].strip(), '%a, %d %b %Y %H:%M:%S %z')
        formatted_date = date_obj.strftime('%m/%d/%Y, %I:%M %p')
    except:
        formatted_date = date
    
    return {
        'message_id': message['id'],
        'thread_id': message['threadId'],
        'sender name': sender_name,
        'sender email': sender_email,
        'subject': subject,
        'summary': body[:500] if body else 'No content',
        'Date': formatted_date,
        'Attachment': has_attachments,
        'generated_email_draft': '',
        'email_tag': ''
    }

def get_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'multipart/alternative':
                return get_email_body(part)
    
    if 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return ''

def send_email(to_email, subject, body, reply_to_message_id=None):
    try:
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        
        if reply_to_message_id:
            message['In-Reply-To'] = reply_to_message_id
            message['References'] = reply_to_message_id
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True, f"Email sent successfully! Message ID: {send_message['id']}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# ==================== SHEETS UTILS ====================
def get_sheets_access_token():
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('X_REPLIT_TOKEN not found for repl/depl')
    
    url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet'
    
    response = requests.get(
        url,
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    data = response.json()
    connection_settings = data.get('items', [])[0] if data.get('items') else None
    
    if not connection_settings:
        raise Exception('Google Sheets not connected')
    
    access_token = (
        connection_settings.get('settings', {}).get('access_token') or 
        connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token')
    )
    
    if not access_token:
        raise Exception('Google Sheets access token not found')
    
    return access_token

def get_sheets_service():
    access_token = get_sheets_access_token()
    credentials = Credentials(token=access_token)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def extract_sheet_id(url):
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return url

def read_sheet_data(sheet_url, range_name='Sheet1'):
    try:
        service = get_sheets_service()
        sheet_id = extract_sheet_id(sheet_url)
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return pd.DataFrame()
        
        headers = values[0]
        rows = values[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        return df
    except Exception as e:
        st.error(f"Error reading sheet: {e}")
        return pd.DataFrame()

def write_sheet_data(sheet_url, df, range_name='Sheet1'):
    try:
        service = get_sheets_service()
        sheet_id = extract_sheet_id(sheet_url)
        
        headers = df.columns.tolist()
        values = [headers] + df.values.tolist()
        
        body = {'values': values}
        
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True, f"Updated {result.get('updatedCells')} cells"
    except Exception as e:
        return False, f"Error writing to sheet: {str(e)}"

def append_sheet_data(sheet_url, df, range_name='Sheet1'):
    try:
        service = get_sheets_service()
        sheet_id = extract_sheet_id(sheet_url)
        
        values = df.values.tolist()
        body = {'values': values}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return True, f"Appended {result.get('updates', {}).get('updatedRows')} rows"
    except Exception as e:
        return False, f"Error appending to sheet: {str(e)}"

# ==================== SESSION STATE ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'emails_df' not in st.session_state:
    st.session_state.emails_df = None
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'generated_draft' not in st.session_state:
    st.session_state.generated_draft = ""
if 'email_template' not in st.session_state:
    st.session_state.email_template = "professional"

# ==================== SIDEBAR AUTHENTICATION ====================
with st.sidebar:
    st.markdown("### 🔐 Authentication")
    
    auth_method = st.radio("Select Authentication Method:", ["Environment Variables", "Service Account JSON", "API Key"])
    
    if auth_method == "Service Account JSON":
        st.markdown("#### Upload Service Account JSON")
        uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
        if uploaded_file:
            try:
                service_account_info = json.load(uploaded_file)
                st.session_state.authenticated = True
                st.success("✅ Service account loaded!")
            except Exception as e:
                st.error(f"Error loading JSON: {e}")
    
    elif auth_method == "API Key":
        st.markdown("#### Enter API Keys")
        openai_key = st.text_input("OpenAI API Key", type="password")
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
            st.session_state.authenticated = True
            st.success("✅ API Key set!")
    
    else:
        if st.button("Use Environment Variables"):
            st.session_state.authenticated = True
            st.success("✅ Using environment variables!")
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    auto_refresh = st.checkbox("Auto-refresh emails", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Refresh interval (seconds)", 30, 300, 60)
    
    st.markdown("---")
    
    # Statistics
    if st.session_state.emails_df is not None:
        st.markdown("### 📊 Statistics")
        st.metric("Total Emails", len(st.session_state.emails_df))
        if 'email_tag' in st.session_state.emails_df.columns:
            most_common = st.session_state.emails_df['email_tag'].mode()
            if len(most_common) > 0:
                st.metric("Most Common Tag", most_common[0])

# ==================== MAIN HEADER ====================
st.markdown('<div class="main-header">📧 Email Management System</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    st.markdown('<div class="warning-box">⚠️ Please authenticate using the sidebar to continue.</div>', unsafe_allow_html=True)
    st.stop()

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Fetch Emails", "✍️ Email Generator", "📤 Send Email", "📊 Google Sheets", "📋 Templates"])

# ==================== TAB 1: FETCH EMAILS ====================
with tab1:
    st.markdown('<div class="sub-header">Fetch and Process Emails</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        max_emails = st.slider("Number of emails to fetch", 10, 100, 50)
    
    with col2:
        if st.button("🔄 Fetch Emails", use_container_width=True):
            with st.spinner("Fetching emails from Gmail..."):
                try:
                    emails = fetch_emails(max_results=max_emails)
                    if emails:
                        st.session_state.emails_df = pd.DataFrame(emails)
                        st.success(f"✅ Fetched {len(emails)} emails successfully!")
                    else:
                        st.warning("No emails found.")
                except Exception as e:
                    st.error(f"Error fetching emails: {e}")
    
    if st.session_state.emails_df is not None:
        st.markdown("---")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search in subject/sender", "")
        with col2:
            if 'email_tag' in st.session_state.emails_df.columns:
                tags = ['All'] + list(st.session_state.emails_df['email_tag'].unique())
                selected_tag = st.selectbox("Filter by tag", tags)
            else:
                selected_tag = 'All'
        with col3:
            if 'Attachment' in st.session_state.emails_df.columns:
                attachment_filter = st.selectbox("Has attachments?", ['All', 'Yes', 'No'])
            else:
                attachment_filter = 'All'
        
        # Apply filters
        filtered_df = st.session_state.emails_df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df['subject'].str.contains(search_term, case=False, na=False) |
                filtered_df['sender name'].str.contains(search_term, case=False, na=False)
            ]
        if 'email_tag' in filtered_df.columns and selected_tag != 'All':
            filtered_df = filtered_df[filtered_df['email_tag'] == selected_tag]
        if 'Attachment' in filtered_df.columns and attachment_filter != 'All':
            filtered_df = filtered_df[filtered_df['Attachment'] == attachment_filter]
        
        # Display emails
        st.dataframe(
            filtered_df[['sender name', 'subject', 'Date', 'email_tag', 'Attachment']],
            use_container_width=True,
            height=400
        )
        
        # Batch processing
        st.markdown("---")
        st.markdown("#### 🤖 Batch Processing")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate All Drafts & Tags", use_container_width=True):
                with st.spinner("Processing emails with AI..."):
                    try:
                        results = batch_generate_drafts_and_tags(st.session_state.emails_df)
                        st.session_state.emails_df['generated_email_draft'] = [r['draft'] for r in results]
                        st.session_state.emails_df['email_tag'] = [r['tag'] for r in results]
                        st.success("✅ All emails processed!")
                    except Exception as e:
                        st.error(f"Error processing: {e}")
        
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Emails (CSV)",
                data=csv,
                file_name=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ==================== TAB 2: EMAIL GENERATOR ====================
with tab2:
    st.markdown('<div class="sub-header">AI Email Draft Generator</div>', unsafe_allow_html=True)
    
    if st.session_state.emails_df is not None and len(st.session_state.emails_df) > 0:
        # Email selection
        email_options = [f"{row['sender name']} - {row['subject']}" for _, row in st.session_state.emails_df.iterrows()]
        selected_idx = st.selectbox("Select an email to reply to:", range(len(email_options)), format_func=lambda x: email_options[x])
        
        selected_email = st.session_state.emails_df.iloc[selected_idx]
        
        # Display original email
        with st.expander("📧 Original Email", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**From:** {selected_email['sender name']}")
                st.markdown(f"**Email:** {selected_email['sender email']}")
            with col2:
                st.markdown(f"**Date:** {selected_email['Date']}")
                st.markdown(f"**Subject:** {selected_email['subject']}")
            
            st.markdown("**Summary:**")
            st.text_area("", selected_email['summary'], height=150, disabled=True, key="original_summary")
        
        # Template selection
        st.markdown("---")
        st.markdown("#### 📝 Email Template")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            template_type = st.selectbox(
                "Choose template style:",
                ["Professional", "Friendly", "Formal", "Brief", "Detailed", "Custom"]
            )
        with col2:
            tone = st.selectbox("Tone:", ["Neutral", "Warm", "Enthusiastic", "Apologetic", "Grateful"])
        with col3:
            length = st.selectbox("Length:", ["Short", "Medium", "Long"])
        
        # Custom instructions
        custom_instructions = st.text_area(
            "Additional instructions (optional):",
            placeholder="E.g., 'Mention our meeting next week' or 'Decline the request politely'",
            height=80
        )
        
        # Generate button
        if st.button("✨ Generate Draft", use_container_width=True, type="primary"):
            with st.spinner("Generating email draft..."):
                try:
                    draft = generate_email_draft(
                        selected_email['subject'],
                        selected_email['sender name'],
                        selected_email['summary'],
                        template_type,
                        tone,
                        length,
                        custom_instructions
                    )
                    st.session_state.generated_draft = draft
                    st.success("✅ Draft generated!")
                except Exception as e:
                    st.error(f"Error generating draft: {e}")
        
        # Display and edit draft
        if st.session_state.generated_draft:
            st.markdown("---")
            st.markdown("#### 📄 Generated Draft")
            
            edited_draft = st.text_area(
                "Edit your draft:",
                st.session_state.generated_draft,
                height=300,
                key="draft_editor"
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.generated_draft = ""
                    st.rerun()
            with col2:
                if st.button("💾 Save Draft", use_container_width=True):
                    st.session_state.emails_df.at[selected_idx, 'generated_email_draft'] = edited_draft
                    st.success("✅ Draft saved!")
            with col3:
                if st.button("📤 Go to Send", use_container_width=True):
                    st.session_state.selected_email = selected_email
                    st.session_state.generated_draft = edited_draft
                    st.info("Switch to 'Send Email' tab to send this draft.")
    else:
        st.info("👆 Please fetch emails first from the 'Fetch Emails' tab.")

# ==================== TAB 3: SEND EMAIL ====================
with tab3:
    st.markdown('<div class="sub-header">Send Email</div>', unsafe_allow_html=True)
    
    # Pre-fill if coming from generator
    default_to = st.session_state.selected_email['sender email'] if st.session_state.selected_email else ""
    default_subject = f"Re: {st.session_state.selected_email['subject']}" if st.session_state.selected_email else ""
    default_body = st.session_state.generated_draft if st.session_state.generated_draft else ""
    
    with st.form("send_email_form"):
        recipient = st.text_input("To:", value=default_to)
        subject = st.text_input("Subject:", value=default_subject)
        
        # Email body with template options
        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("**Quick Insert:**")
            add_signature = st.form_submit_button("➕ Signature", use_container_width=True)
            add_meeting = st.form_submit_button("➕ Meeting Link", use_container_width=True)
        
        body = st.text_area("Message:", value=default_body, height=300)
        
        if add_signature:
            body += "\n\nBest regards,\n[Your Name]"
        if add_meeting:
            body += "\n\nJoin meeting: [Insert Link]"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            send_as_reply = st.checkbox("Send as reply to selected email", value=bool(st.session_state.selected_email))
        
        submitted = st.form_submit_button("📨 Send Email", type="primary", use_container_width=True)
        
        if submitted:
            if not recipient or not subject or not body:
                st.error("❌ Please fill in all fields.")
            else:
                with st.spinner("Sending email..."):
                    try:
                        reply_to_id = st.session_state.selected_email['message_id'] if send_as_reply and st.session_state.selected_email else None
                        success, message = send_email(recipient, subject, body, reply_to_id)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.session_state.generated_draft = ""
                            st.session_state.selected_email = None
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==================== TAB 4: GOOGLE SHEETS ====================
with tab4:
    st.markdown('<div class="sub-header">Google Sheets Integration</div>', unsafe_allow_html=True)
    
    sheet_url = st.text_input("📋 Google Sheet URL:", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📖 Read Sheet", use_container_width=True):
            if sheet_url:
                with st.spinner("Reading from Google Sheets..."):
                    try:
                        df = read_sheet_data(sheet_url)
                        if not df.empty:
                            st.session_state.sheet_df = df
                            st.success(f"✅ Loaded {len(df)} rows")
                        else:
                            st.warning("Sheet is empty or not found.")
                    except Exception as e:
                        st.error(f"Error reading sheet: {e}")
            else:
                st.warning("Please enter a sheet URL.")
    
    with col2:
        if st.button("💾 Write to Sheet", use_container_width=True):
            if sheet_url and st.session_state.emails_df is not None:
                with st.spinner("Writing to Google Sheets..."):
                    try:
                        success, message = write_sheet_data(sheet_url, st.session_state.emails_df)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter sheet URL and fetch emails first.")
    
    with col3:
        if st.button("➕ Append to Sheet", use_container_width=True):
            if sheet_url and st.session_state.emails_df is not None:
                with st.spinner("Appending to Google Sheets..."):
                    try:
                        success, message = append_sheet_data(sheet_url, st.session_state.emails_df)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter sheet URL and fetch emails first.")
    
    # Display sheet data
    if 'sheet_df' in st.session_state:
        st.markdown("---")
        st.markdown("#### 📊 Live Sheet View")
        
        # Auto-refresh option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                if sheet_url:
                    try:
                        df = read_sheet_data(sheet_url)
                        st.session_state.sheet_df = df
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.dataframe(st.session_state.sheet_df, use_container_width=True, height=400)
        
        # Export
        csv = st.session_state.sheet_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sheet Data (CSV)",
            data=csv,
            file_name=f"sheet_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ==================== TAB 5: TEMPLATES ====================
with tab5:
    st.markdown('<div class="sub-header">Email Templates Library</div>', unsafe_allow_html=True)
    
    templates = {
        "Professional Response": {
            "subject": "Re: {original_subject}",
            "body": """Dear {sender_name},

Thank you for your email regarding {topic}.

{main_content}

Please let me know if you need any additional information.

Best regards,
[Your Name]"""
        },
        "Meeting Request": {
            "subject": "Meeting Request: {topic}",
            "body": """Hi {sender_name},

I hope this email finds you well. I would like to schedule a meeting to discuss {topic}.

Would you be available for a meeting {timeframe}? Please let me know what works best for you.

Looking forward to hearing from you.

Best regards,
[Your Name]"""
        },
        "Follow-up": {
            "subject": "Following up: {topic}",
            "body": """Hi {sender_name},

I wanted to follow up on {topic} that we discussed previously.

{main_content}

Please let me know if you have any questions or if there's anything I can help with.

Best regards,
[Your Name]"""
        },
        "Thank You": {
            "subject": "Thank you - {topic}",
            "body": """Dear {sender_name},

Thank you so much for {reason}.

{main_content}

I truly appreciate your time and assistance.

Warm regards,
[Your Name]"""
        },
        "Decline Politely": {
            "subject": "Re: {original_subject}",
            "body": """Dear {sender_name},

Thank you for reaching out regarding {topic}.

Unfortunately, {reason}. However, {alternative_suggestion}.

I appreciate your understanding.

Best regards,
[Your Name]"""
        },
        "Information Request": {
            "subject": "Request for Information: {topic}",
            "body": """Hi {sender_name},

I hope you're doing well. I'm reaching out to request information about {topic}.

Specifically, I would like to know:
- {point_1}
- {point_2}
- {point_3}

Your assistance would be greatly appreciated.

Best regards,
[Your Name]"""
        },
        "Out of Office": {
            "subject": "Out of Office - {your_name}",
            "body": """Thank you for your email.

I am currently out of the office from {start_date} to {end_date} with limited access to email.

For urgent matters, please contact {alternate_contact} at {alternate_email}.

I will respond to your message upon my return.

Best regards,
[Your Name]"""
        },
        "Project Update": {
            "subject": "Project Update: {project_name}",
            "body": """Hi {sender_name},

I wanted to provide you with an update on {project_name}.

Progress Summary:
- {accomplishment_1}
- {accomplishment_2}
- {accomplishment_3}

Next Steps:
- {next_step_1}
- {next_step_2}

Timeline: {timeline_info}

Please let me know if you have any questions or concerns.

Best regards,
[Your Name]"""
        },
        "Apology Email": {
            "subject": "Apology regarding {issue}",
            "body": """Dear {sender_name},

I sincerely apologize for {issue}. I understand this may have caused {impact}.

{explanation}

To resolve this, I have {action_taken}.

Moving forward, {prevention_plan}.

Thank you for your patience and understanding.

Best regards,
[Your Name]"""
        },
        "Introduction Email": {
            "subject": "Introduction: {your_name}",
            "body": """Hi {sender_name},

My name is {your_name} and I am {your_role} at {company}.

I'm reaching out because {reason_for_contact}.

{value_proposition}

Would you be open to a brief call {timeframe} to discuss this further?

Looking forward to connecting.

Best regards,
[Your Name]"""
        }
    }
    
    st.markdown("### 📚 Available Templates")
    st.markdown("Select a template below to view and use it in your emails.")
    
    for template_name, template_content in templates.items():
        with st.expander(f"📋 {template_name}"):
            st.markdown(f"**Subject:** `{template_content['subject']}`")
            st.markdown("**Body:**")
            st.code(template_content['body'], language=None)
            
            if st.button(f"Use {template_name}", key=f"use_{template_name}"):
                st.session_state.generated_draft = template_content['body']
                st.success(f"✅ Template '{template_name}' loaded! Go to 'Send Email' tab.")
    
    st.markdown("---")
    st.markdown("### 📝 Create Custom Template")
    
    with st.form("custom_template_form"):
        custom_name = st.text_input("Template Name:", placeholder="My Custom Template")
        custom_subject = st.text_input("Subject Template:", placeholder="Re: {topic}")
        custom_body = st.text_area(
            "Body Template:", 
            height=200,
            placeholder="""Hi {sender_name},

{main_content}

Best regards,
[Your Name]"""
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Custom Template", use_container_width=True)
        with col2:
            preview = st.form_submit_button("👁️ Preview Template", use_container_width=True)
        
        if submitted:
            if custom_name and custom_body:
                # Save to session state for this session
                if 'custom_templates' not in st.session_state:
                    st.session_state.custom_templates = {}
                st.session_state.custom_templates[custom_name] = {
                    'subject': custom_subject,
                    'body': custom_body
                }
                st.success(f"✅ Template '{custom_name}' saved for this session!")
            else:
                st.warning("Please fill in template name and body.")
        
        if preview:
            if custom_body:
                st.markdown("#### Preview:")
                st.code(custom_body, language=None)
            else:
                st.warning("Please enter template body to preview.")
    
    # Display custom templates
    if 'custom_templates' in st.session_state and st.session_state.custom_templates:
        st.markdown("---")
        st.markdown("### 🎨 Your Custom Templates")
        
        for custom_name, custom_content in st.session_state.custom_templates.items():
            with st.expander(f"✨ {custom_name} (Custom)"):
                st.markdown(f"**Subject:** `{custom_content['subject']}`")
                st.markdown("**Body:**")
                st.code(custom_content['body'], language=None)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Use {custom_name}", key=f"use_custom_{custom_name}"):
                        st.session_state.generated_draft = custom_content['body']
                        st.success(f"✅ Custom template '{custom_name}' loaded!")
                with col2:
                    if st.button(f"Delete {custom_name}", key=f"delete_{custom_name}"):
                        del st.session_state.custom_templates[custom_name]
                        st.rerun()

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📧 Email Management System | Built with Streamlit | Powered by OpenAI & Google APIs</p>
    <p style='font-size: 0.8rem;'>All-in-One Solution: Gmail Integration • AI Email Generation • Google Sheets Sync</p>
</div>
""", unsafe_allow_html=True)
