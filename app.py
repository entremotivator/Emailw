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
import base64

# Configuration
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']
SCOPES_SHEETS = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1DhqfIYM92gTdQ3yku233tLlkfIZsgcI9MVS_MvNg_Cc"

st.set_page_config(page_title="InboxKeep Pro", page_icon="📧", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS with horizontal navigation
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .main { background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%); padding: 0 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    .top-nav { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 15px 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); position: sticky; top: 0; z-index: 1000; }
    .nav-brand { font-size: 28px; font-weight: 900; color: white; display: inline-block; margin-right: 40px; }
    .content-wrapper { padding: 30px 40px; max-width: 1800px; margin: 0 auto; }
    
    .page-header { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #3b82f6; }
    .page-title { font-size: 36px; font-weight: 900; color: #1e3a8a; margin: 0; }
    .page-subtitle { font-size: 16px; color: #64748b; margin-top: 8px; }
    
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 35px; }
    .stat-card { background: white; padding: 28px; border-radius: 16px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 6px solid #3b82f6; }
    .stat-icon { font-size: 36px; margin-bottom: 10px; }
    .stat-number { font-size: 36px; font-weight: 900; color: #1e293b; margin: 8px 0; }
    .stat-label { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; }
    
    .email-card { background: white; border: 2px solid #e2e8f0; border-radius: 16px; padding: 28px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); transition: all 0.3s ease; position: relative; }
    .email-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(30,58,138,0.12); border-color: #3b82f6; }
    .email-card::before { content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 100%; background: #94a3b8; }
    .email-card.priority-high::before { background: #ef4444; }
    .email-card.priority-medium::before { background: #f59e0b; }
    .email-card.priority-low::before { background: #10b981; }
    .email-card.unread { background: #fef3c7; border-color: #fbbf24; }
    
    .email-header { display: flex; align-items: center; margin-bottom: 18px; padding-left: 15px; }
    .sender-avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 22px; margin-right: 16px; }
    .sender-name { font-weight: 800; font-size: 18px; color: #1f2937; }
    .sender-email { color: #6b7280; font-size: 14px; }
    .subject-line { font-size: 22px; font-weight: 800; color: #111827; margin: 14px 0 10px 15px; }
    .email-summary { color: #4b5563; font-size: 15px; line-height: 1.7; margin-bottom: 16px; padding-left: 15px; }
    
    .badge { padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 11px; text-transform: uppercase; margin-right: 8px; }
    .badge.priority-high { background: #fee2e2; color: #991b1b; }
    .badge.priority-medium { background: #fef3c7; color: #92400e; }
    .badge.priority-low { background: #d1fae5; color: #065f46; }
    
    .ai-box { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 4px solid #3b82f6; padding: 16px; margin: 12px 0 20px 15px; border-radius: 10px; }
    
    .compose-container { background: white; border-radius: 16px; padding: 35px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 30px; }
    .email-preview { background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; padding: 28px; margin-top: 25px; }
    
    .template-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 25px 0; }
    .template-card { background: white; border: 3px solid #e2e8f0; border-radius: 14px; padding: 24px; cursor: pointer; transition: all 0.3s; }
    .template-card:hover { border-color: #3b82f6; transform: translateY(-4px); }
    .template-card.selected { border-color: #3b82f6; background: #eff6ff; }
    
    .draft-card { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 3px solid #fbbf24; border-radius: 16px; padding: 28px; margin-bottom: 20px; }
    .sent-card { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 2px solid #10b981; border-radius: 16px; padding: 24px; margin-bottom: 18px; }
    
    .alert-box { padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; font-weight: 600; border-left: 6px solid; }
    .alert-success { background: #d1fae5; border-color: #10b981; color: #065f46; }
    .alert-info { background: #dbeafe; border-color: #3b82f6; color: #1e40af; }
    .alert-warning { background: #fef3c7; border-color: #f59e0b; color: #92400e; }
    .alert-error { background: #fee2e2; border-color: #ef4444; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

EMAIL_TEMPLATES = {
    "professional": {"name": "Professional Reply", "icon": "💼", "template": "Dear {sender},\n\nThank you for your email regarding {subject}.\n\n{content}\n\nBest regards,\n{your_name}"},
    "friendly": {"name": "Friendly Reply", "icon": "😊", "template": "Hi {sender},\n\nThanks for reaching out!\n\n{content}\n\nCheers,\n{your_name}"},
    "meeting": {"name": "Meeting Request", "icon": "📅", "template": "Dear {sender},\n\nI'd like to schedule a meeting about {subject}.\n\n{content}\n\nBest regards,\n{your_name}"},
}

def init_state():
    defaults = {
        'page': 'inbox', 'selected_email': None, 'compose_mode': None, 'drafts': [], 
        'sent': [], 'smtp': {'server': 'smtp.gmail.com', 'port': 587, 'user': '', 'password': ''},
        'filter_dept': 'All', 'filter_priority': 'All', 'sort': 'Date (Newest)', 
        'search': '', 'template': None, 'email_df': None, 'gmail_service': None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_initials(name):
    parts = str(name).strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[0].upper() if name else "?"

def generate_mock_data(n=30):
    senders = [("John Smith", "john@sales.com", "Sales"), ("Sarah Lee", "sarah@marketing.com", "Marketing")]
    subjects = ["Q4 Report", "Campaign Results", "System Maintenance", "Budget Request"]
    emails = []
    for i in range(n):
        name, email, dept = random.choice(senders)
        emails.append({
            "sender name": name, "sender email": email, "subject": random.choice(subjects),
            "summary": "Important email content here.", 
            "date": (datetime.now() - timedelta(days=random.randint(0,30))).strftime("%Y-%m-%d %H:%M:%S"),
            "attachment": random.choice(["Yes", "No"]), "aireply": "AI generated reply" if random.random() > 0.6 else "",
            "department": dept, "priority": random.choice(["high","medium","low"]), "read_status": random.choice(["read","unread"])
        })
    return pd.DataFrame(emails)

def send_email(to, subject, body):
    gmail = st.session_state.get('gmail_service')
    smtp = st.session_state.get('smtp', {})
    
    if gmail:
        try:
            msg = MIMEMultipart()
            msg['To'], msg['Subject'] = to, subject
            msg.attach(MIMEText(body.replace('\n', '<br>'), 'html'))
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
            return True, "Email sent via Gmail API!"
        except Exception as e:
            return False, str(e)
    elif smtp.get('user') and smtp.get('password'):
        try:
            msg = MIMEMultipart()
            msg['From'], msg['To'], msg['Subject'] = smtp['user'], to, subject
            msg.attach(MIMEText(body.replace('\n', '<br>'), 'html'))
            server = smtplib.SMTP(smtp['server'], smtp['port'])
            server.starttls()
            server.login(smtp['user'], smtp['password'])
            server.send_message(msg)
            server.quit()
            return True, "Email sent via SMTP!"
        except Exception as e:
            return False, str(e)
    return False, "No email service configured"

def render_nav():
    st.markdown('<div class="top-nav"><span class="nav-brand">📧 InboxKeep Pro</span></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    pages = [('inbox','📥 Inbox'), ('compose','✉️ Compose'), ('drafts','📋 Drafts'), ('sent','📤 Sent'), ('settings','⚙️ Settings')]
    for i, (page, label) in enumerate(pages):
        with cols[i]:
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state['page'] = page
                st.rerun()

def render_inbox():
    st.markdown('<div class="content-wrapper"><div class="page-header"><div class="page-title">📥 Inbox</div><div class="page-subtitle">Manage your emails</div></div>', unsafe_allow_html=True)
    df = st.session_state['email_df']
    if df is None or len(df) == 0:
        st.info("No emails"); st.markdown('</div>', unsafe_allow_html=True); return
    
    total, unread = len(df), df[df['read_status']=='unread'].shape[0] if 'read_status' in df.columns else 0
    ai_count = df['aireply'].apply(lambda x: bool(x and str(x).strip())).sum()
    high = df[df['priority']=='high'].shape[0]
    
    st.markdown(f'<div class="stats-grid"><div class="stat-card"><div class="stat-icon">📧</div><div class="stat-number">{total}</div><div class="stat-label">Total</div></div><div class="stat-card"><div class="stat-icon">📬</div><div class="stat-number">{unread}</div><div class="stat-label">Unread</div></div><div class="stat-card"><div class="stat-icon">🤖</div><div class="stat-number">{ai_count}</div><div class="stat-label">AI Ready</div></div><div class="stat-card"><div class="stat-icon">🔥</div><div class="stat-number">{high}</div><div class="stat-label">High Priority</div></div></div>', unsafe_allow_html=True)
    
    st.text_input("🔎 Search", key='search_box', value=st.session_state.get('search',''))
    
    for idx, row in df.iterrows():
        email = row.to_dict()
        initials = get_initials(email.get('sender name','?'))
        subject = email.get('subject','No Subject')
        summary = email.get('summary','')
        priority = email.get('priority','low')
        unread_class = ' unread' if email.get('read_status')=='unread' else ''
        
        st.markdown(f'''<div class="email-card priority-{priority}{unread_class}">
        <div class="email-header"><div class="sender-avatar">{initials}</div><div><div class="sender-name">{email.get('sender name','Unknown')}</div><div class="sender-email">{email.get('sender email','')}</div><span class="badge priority-{priority}">{priority.upper()}</span></div></div>
        <div class="subject-line">{subject}</div><div class="email-summary">{summary}</div></div>''', unsafe_allow_html=True)
        
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            if st.button("✉️ Reply", key=f"r{idx}", use_container_width=True):
                st.session_state.update({'selected_email':email,'compose_mode':'reply','page':'compose'})
                st.rerun()
        with c2:
            if st.button("🤖 AI", key=f"ai{idx}", use_container_width=True, disabled=not email.get('aireply')):
                st.session_state.update({'selected_email':email,'compose_mode':'ai','page':'compose'})
                st.rerun()
        with c3:
            if st.button("📝 Template", key=f"t{idx}", use_container_width=True):
                st.session_state.update({'selected_email':email,'compose_mode':'template','page':'compose'})
                st.rerun()
        with c4:
            if st.button("📁 Archive", key=f"a{idx}", use_container_width=True):
                st.toast("Archived!"); st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_compose():
    st.markdown('<div class="content-wrapper"><div class="page-header"><div class="page-title">✉️ Compose</div></div>', unsafe_allow_html=True)
    
    email = st.session_state.get('selected_email')
    mode = st.session_state.get('compose_mode','new')
    
    if mode == 'template':
        st.markdown("### Choose Template")
        st.markdown('<div class="template-grid">', unsafe_allow_html=True)
        for key, tmpl in EMAIL_TEMPLATES.items():
            selected_class = ' selected' if st.session_state.get('template')==key else ''
            st.markdown(f'<div class="template-card{selected_class}"><div>{tmpl["icon"]} {tmpl["name"]}</div></div>', unsafe_allow_html=True)
            if st.button(f"Select {tmpl['name']}", key=f"sel_{key}"):
                st.session_state['template'] = key
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.get('template'):
            tmpl = EMAIL_TEMPLATES[st.session_state['template']]['template']
            with st.form("tmpl_form"):
                to = st.text_input("To:", email.get('sender email','') if email else '')
                subj = st.text_input("Subject:", f"Re: {email.get('subject','')}" if email else '')
                content = st.text_area("Content:", height=150)
                your_name = st.text_input("Your name:")
                
                if st.form_submit_button("📤 Send"):
                    if to and subj and content and your_name:
                        body = tmpl.format(sender=email.get('sender name','') if email else 'Recipient', 
                                         subject=email.get('subject','') if email else '', 
                                         content=content, your_name=your_name)
                        success, msg = send_email(to, subj, body)
                        if success:
                            st.success(msg)
                            st.session_state['sent'].append({'to':to,'subject':subj,'body':body,'time':datetime.now().strftime("%Y-%m-%d %H:%M")})
                            st.balloons()
                            time.sleep(2)
                            st.session_state['page']='inbox'
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        to_val = email.get('sender email','') if email else ''
        subj_val = f"Re: {email.get('subject','')}" if email and mode=='reply' else ''
        body_val = email.get('aireply','') if mode=='ai' and email else ''
        
        with st.form("compose_form"):
            to = st.text_input("To:", value=to_val)
            subj = st.text_input("Subject:", value=subj_val)
            body = st.text_area("Body:", value=body_val, height=400)
            
            st.markdown(f'<div class="email-preview"><strong>To:</strong> {to}<br><strong>Subject:</strong> {subj}<br><br>{body.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            
            c1,c2 = st.columns(2)
            with c1:
                if st.form_submit_button("📤 Send", use_container_width=True):
                    if to and subj and body:
                        success, msg = send_email(to, subj, body)
                        if success:
                            st.success(msg)
                            st.session_state['sent'].append({'to':to,'subject':subj,'body':body,'time':datetime.now().strftime("%Y-%m-%d %H:%M")})
                            st.balloons()
                            time.sleep(2)
                            st.session_state['page']='inbox'
                            st.rerun()
                        else:
                            st.error(msg)
            with c2:
                if st.form_submit_button("💾 Save Draft", use_container_width=True):
                    st.session_state['drafts'].append({'to':to,'subject':subj,'body':body,'time':datetime.now().strftime("%Y-%m-%d %H:%M")})
                    st.success("Draft saved!")
                    time.sleep(1)
                    st.session_state['page']='drafts'
                    st.rerun()
    
    if st.button("🔙 Back"):
        st.session_state['page']='inbox'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_drafts():
    st.markdown('<div class="content-wrapper"><div class="page-header"><div class="page-title">📋 Drafts</div></div>', unsafe_allow_html=True)
    drafts = st.session_state.get('drafts',[])
    if not drafts:
        st.info("No drafts")
    else:
        for i, d in enumerate(drafts):
            st.markdown(f'<div class="draft-card"><h3>{d["subject"]}</h3><p>To: {d["to"]}</p><p>Saved: {d["time"]}</p></div>', unsafe_allow_html=True)
            with st.expander(f"View #{i+1}"):
                st.text(d['body'])
            c1,c2 = st.columns(2)
            with c1:
                if st.button("📤 Send", key=f"sd{i}"):
                    success, msg = send_email(d['to'], d['subject'], d['body'])
                    if success:
                        st.success(msg)
                        st.session_state['sent'].append(d)
                        st.session_state['drafts'].pop(i)
                        st.rerun()
            with c2:
                if st.button("🗑️ Delete", key=f"dd{i}"):
                    st.session_state['drafts'].pop(i)
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_sent():
    st.markdown('<div class="content-wrapper"><div class="page-header"><div class="page-title">📤 Sent</div></div>', unsafe_allow_html=True)
    sent = st.session_state.get('sent',[])
    if not sent:
        st.info("No sent emails")
    else:
        for i, e in enumerate(sent):
            st.markdown(f'<div class="sent-card"><h3>{e["subject"]}</h3><p>To: {e["to"]}</p><p>Sent: {e["time"]}</p></div>', unsafe_allow_html=True)
            with st.expander(f"View #{i+1}"):
                st.text(e['body'])
    st.markdown('</div>', unsafe_allow_html=True)

def render_settings():
    st.markdown('<div class="content-wrapper"><div class="page-header"><div class="page-title">⚙️ Settings</div></div>', unsafe_allow_html=True)
    
    st.subheader("🔐 Gmail API")
    uploaded = st.file_uploader("Upload Service Account JSON", type=['json'])
    if uploaded:
        try:
            creds = json.load(uploaded)
            st.session_state['stored_credentials'] = creds
            from googleapiclient.discovery import build
            credentials = Credentials.from_service_account_info(creds, scopes=SCOPES_GMAIL)
            st.session_state['gmail_service'] = build('gmail','v1',credentials=credentials)
            st.success("✅ Gmail API connected!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.subheader("📧 SMTP Settings")
    with st.form("smtp_form"):
        server = st.text_input("Server", value=st.session_state['smtp']['server'])
        port = st.number_input("Port", value=st.session_state['smtp']['port'])
        user = st.text_input("Email", value=st.session_state['smtp']['user'])
        pwd = st.text_input("Password", type="password", value=st.session_state['smtp']['password'])
        if st.form_submit_button("💾 Save"):
            st.session_state['smtp'] = {'server':server,'port':port,'user':user,'password':pwd}
            st.success("SMTP saved!")
    
    st.subheader("📊 Data")
    if st.button("🔄 Reload Mock Data"):
        st.session_state['email_df'] = generate_mock_data(30)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_state()
    if st.session_state['email_df'] is None:
        st.session_state['email_df'] = generate_mock_data(30)
    
    render_nav()
    
    page = st.session_state['page']
    if page == 'inbox': render_inbox()
    elif page == 'compose': render_compose()
    elif page == 'drafts': render_drafts()
    elif page == 'sent': render_sent()
    elif page == 'settings': render_settings()

if __name__ == "__main__":
    main()
