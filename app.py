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
import os


def get_gmail_credentials():
    """Get Gmail credentials from Streamlit secrets."""
    try:
        gmail_email = st.secrets["gmail"]["email"]
        gmail_password = st.secrets["gmail"]["password"]
        return gmail_email, gmail_password
    except Exception as e:
        st.warning("Gmail credentials not found in secrets. Please configure .streamlit/secrets.toml")
        return None, None

def send_real_email(to_address, subject, body, cc_address=None, attachments=None, use_html=True):
    """Send a real email using Gmail SMTP."""
    try:
        gmail_email, gmail_password = get_gmail_credentials()
        
        if not gmail_email or not gmail_password:
            st.error("Gmail credentials not configured. Please add them to .streamlit/secrets.toml")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_email
        msg['To'] = to_address
        msg['Subject'] = subject
        
        if cc_address:
            msg['Cc'] = cc_address
        
        # Add body
        if use_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
                msg.attach(part)
        
        # Connect to Gmail SMTP server
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
        
        # Optionally save to Google Sheets
        if credentials_dict:
            try:
                scope = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"
                ]
                credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
                gc = gspread.authorize(credentials)
                worksheet = gc.open_by_key(SHEET_ID).worksheet('Sent')  # Create a 'Sent' sheet in your Google Sheets
                
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


def render_compose(email_data=None):
    """Renders the compose page for replying to an email or drafting a new one."""
    st.markdown("## ✉️ Compose Email")
    
    gmail_email, gmail_password = get_gmail_credentials()
    gmail_configured = bool(gmail_email and gmail_password)
    
    if not gmail_configured:
        st.warning("⚠️ Gmail not configured. Add credentials to .streamlit/secrets.toml to send real emails.")
        with st.expander("📋 How to configure Gmail"):
            st.markdown("""
            Create a file `.streamlit/secrets.toml` with:
            \`\`\`toml
            [gmail]
            email = "your-email@gmail.com"
            password = "your-app-password"
            \`\`\`
            
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
        
        uploaded_files = st.file_uploader(
            "📎 Attachments (optional):",
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
                st.markdown(f"<div style='background: #f9f9f9; padding: 15px; border-radius: 8px;'>{body or '[Empty body]'}</div>", unsafe_allow_html=True)
            else:
                st.text(body or "[Empty body]")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            send_button = st.form_submit_button("📤 Send Email", type="primary", use_container_width=True)
        with col2:
            save_draft_button = st.form_submit_button("📋 Save Draft", use_container_width=True)
        with col3:
            clear_button = st.form_submit_button("🗑️ Clear", use_container_width=True)
        with col4:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if send_button:
            if not to_address:
                st.error("❌ Please enter a recipient email address!")
            elif not subject:
                st.error("❌ Please enter an email subject!")
            elif not body:
                st.error("❌ Please enter email body!")
            elif not gmail_configured:
                st.error("❌ Gmail credentials not configured. Cannot send email.")
            else:
                with st.spinner("📤 Sending email..."):
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
                        st.error("❌ Failed to send email. Please check your credentials and try again.")
        
        if save_draft_button:
            if not subject and not body:
                st.error("❌ Cannot save empty draft!")
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
                st.success("📋 Draft saved successfully!")
                time.sleep(1)
                st.session_state['page'] = 'drafts'
                st.rerun()
        
        if clear_button:
            st.rerun()
        
        if cancel_button:
            st.session_state['page'] = 'inbox'
            st.rerun()
