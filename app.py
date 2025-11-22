import streamlit as st
import pandas as pd
import json
from datetime import datetime
import time

# Import your existing modules
try:
    from gmail_utils import fetch_emails, send_email
    from sheets_utils import read_sheet_data, write_sheet_data, append_sheet_data, ensure_columns_exist
    from openai_utils import generate_email_draft, classify_email, batch_generate_drafts_and_tags
except ImportError:
    st.error("Required modules not found. Ensure gmail_utils.py, sheets_utils.py, and openai_utils.py are available.")

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

# Initialize session state
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

# Authentication in Sidebar
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
            import os
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

# Main header
st.markdown('<div class="main-header">📧 Email Management System</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    st.markdown('<div class="warning-box">⚠️ Please authenticate using the sidebar to continue.</div>', unsafe_allow_html=True)
    st.stop()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Fetch Emails", "✍️ Email Generator", "📤 Send Email", "📊 Google Sheets", "📋 Templates"])

# TAB 1: Fetch Emails
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
        with col3:
            if 'Attachment' in st.session_state.emails_df.columns:
                attachment_filter = st.selectbox("Has attachments?", ['All', 'Yes', 'No'])
        
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

# TAB 2: Email Generator
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
                    # Build enhanced prompt
                    prompt_additions = f"\n\nTemplate: {template_type}\nTone: {tone}\nLength: {length}"
                    if custom_instructions:
                        prompt_additions += f"\nAdditional instructions: {custom_instructions}"
                    
                    draft = generate_email_draft(
                        selected_email['subject'],
                        selected_email['sender name'],
                        selected_email['summary'] + prompt_additions
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

# TAB 3: Send Email
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
            if st.form_submit_button("➕ Signature", use_container_width=True):
                default_body += "\n\nBest regards,\n[Your Name]"
            if st.form_submit_button("➕ Meeting Link", use_container_width=True):
                default_body += "\n\nJoin meeting: [Insert Link]"
        
        body = st.text_area("Message:", value=default_body, height=300)
        
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
                            # Clear draft
                            st.session_state.generated_draft = ""
                            st.session_state.selected_email = None
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# TAB 4: Google Sheets
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

# TAB 5: Templates
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
        }
    }
    
    st.markdown("### Available Templates")
    
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
        custom_name = st.text_input("Template Name:")
        custom_subject = st.text_input("Subject Template:")
        custom_body = st.text_area("Body Template:", height=200)
        
        if st.form_submit_button("💾 Save Custom Template"):
            if custom_name and custom_body:
                st.success(f"✅ Template '{custom_name}' saved! (Note: Restart needed to persist)")
            else:
                st.warning("Please fill in template name and body.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📧 Email Management System | Built with Streamlit | Powered by OpenAI & Google APIs</p>
</div>
""", unsafe_allow_html=True)
