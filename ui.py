import streamlit as st
import requests
import os
import re
import json
import boto3
from api.services.kb_query import KB_CONFIG
 
# CONFIG
DJANGO_API = os.getenv("DJANGO_API", "http://localhost:8000")
 
# Load KB Config
kb_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "api", "services", "kb_config.json")
)
 
with open(kb_config_path) as f:
    KB_CONFIG = json.load(f)
kb_list = list(KB_CONFIG.keys())
 
# Domain categories
DOMAINS = {
    "D1": "Contract & Order Management",
    "D2": "Scheduling & Logistics",
    "D3": "Operational Metrics & QA",
    "D4": "Accounting & Accruals",
    "D5": "Invoicing",
}
 
# CUSTOM THEME
def apply_custom_theme():
    st.markdown("""
    <style>

      body, .stText, .stMarkdown, .stButton, .stMetric, .stSelectbox, .stTextInput {
        font-family: "Inter", -apple-system, BlinkMacSystemFont,
                     "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
      }
                
      h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
      }
    </style>
""", unsafe_allow_html=True)
    

    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-black: #000000;
        --primary-white: #FFFFFF;
        --bold-yellow: #FFD700;
        --yellow-hover: #FFC107;
        --dark-gray: #1A1A1A;
        --light-gray: #F5F5F5;
    }
   
    /* Global styles */
    .main {
        background-color: var(--primary-white);
        color: var(--primary-black);
    }
   
    .stApp {
        background-color: var(--primary-white);
    }
   
    /* Headers */
    h1 {
        color: var(--bold-yellow) !important;
        font-weight: bold !important;
    }
   
    h2, h3, h4, h5, h6 {
        color: var(--primary-black) !important;
        font-weight: bold !important;
    }
   
    /* Buttons */
    .stButton > button {
        background-color: var(--bold-yellow) !important;
        color: var(--primary-black) !important;
        font-weight: bold !important;
        border: 2px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
    }
   
    .stButton > button:hover {
        background-color: var(--yellow-hover) !important;
        border-color: var(--yellow-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3) !important;
    }
   
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: var(--primary-white) !important;
        color: var(--primary-black) !important;
        border: 2px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }
   
    .stTextInput > div > div > input:focus {
        border-color: var(--yellow-hover) !important;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2) !important;
    }
   
    /* Select boxes */
    .stSelectbox > div > div > div {
        background-color: var(--primary-white) !important;
        color: var(--primary-black) !important;
        border: 2px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }
   
    /* File uploader */
    .stFileUploader > div {
        background-color: var(--dark-white) !important;
        border: 2px dashed var(--bold-yellow) !important;
        border-radius: 8px !important;
        color: var(--primary-black) !important;
    }
   
    /* Chat messages */
    .stChatMessage {
        background-color: var(--primary-white) !important;
        color: var(--primary-black) !important;
        border: 1px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }

   
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--dark-gray) !important;
        color: var(--bold-yellow) !important;
        border: 1px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
   
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        padding: 8px 0 !important;
        border-radius: 6px 6px 0 0 !important;
    }
   
    .stTabs [data-baseweb="tab"] {
        color: #856404 !important;
        background-color: #FFF3CD !important;
        font-weight: 500 !important;
        border-color: #856404 !important;
    }
   
    /* Single consolidated rule for selected tabs */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #856404 !important;
        background-color: #FFF3CD !important;
        font-weight: bold !important;
        border-bottom: 3px solid #856404 !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
   
    /* Remove any red underlines and pseudo-elements */
    .stTabs [aria-selected="true"]::after,
    .stTabs [aria-selected="true"]::before {
        display: none !important;
    }
                
    /* Override the tab highlight element that causes red underline */
    .stTabs [data-baseweb="tab-highlight"],
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
   
    /* Focus and hover states */
    .stTabs [data-baseweb="tab"]:focus {
        border-color: #856404 !important;
        outline-color: #856404 !important;
    }
   
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #856404 !important;
    }
   
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--dark-gray) !important;
    }
   
    /* Success/Error messages */
    .stAlert {
        border: 2px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }
   
    /* Code blocks */
    .stCodeBlock {
        background-color: var(--dark-gray) !important;
        border: 1px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }
   
    /* Metrics */
    .stMetric {
        background-color: var(--primary-white) !important;
        border: 1px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
   
    /* Radio buttons */
    .stRadio > div > div > div {
        background-color: var(--dark-gray) !important;
        color: var(--primary-white) !important;
    }
   
    /* Checkboxes */
    .stCheckbox > div > div > div {
        background-color: var(--dark-gray) !important;
        color: var(--primary-white) !important;
    }
   
    /* Download buttons */
    .stDownloadButton > button {
        background-color: var(--bold-yellow) !important;
        color: var(--primary-black) !important;
        font-weight: bold !important;
        border: 2px solid var(--bold-yellow) !important;
        border-radius: 8px !important;
    }
   
   
    /* Additional theme improvements */
    .stMarkdown {
        color: #000000 !important;
    }
   
    .stMarkdown p {
        color: #000000 !important;
    }
   
    .stMarkdown code {
        background-color: #1A1A1A !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }
   
    .stMarkdown pre {
        background-color: #1A1A1A !important;
        color: #FFD700 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
   
    /* Chat input styling */
    .stChatInput {
        background-color: #FFFFFF !important;
        border: 2px solid #FFD700 !important;
        border-radius: 8px !important;
        color: #000000 !important;
    }
   
    .stChatInput:focus {
        border-color: #FFC107 !important;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2) !important;
    }
   
    /* Success/Error message styling */
    .stAlert[data-baseweb="notification"] {
        border: 2px solid #FFD700 !important;
        border-radius: 8px !important;
        background-color: #F5F5F5 !important;
    }
   
    /* Spinner styling */
    .stSpinner > div {
        border-color: #FFD700 !important;
        border-top-color: transparent !important;
    }
   
    /* Container styling */
    .main .block-container {
        background-color: #FFFFFF !important;
        padding: 2rem !important;
    }
   
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1A1A1A !important;
        border-right: 2px solid #FFD700 !important;
    }
   
    /* Info boxes */
    .stAlert[data-baseweb="notification"][data-testid="stAlert"] {
        background-color: #F5F5F5 !important;
        border: 2px solid #FFD700 !important;
        color: #000000 !important;
    }
   
    /* Warning boxes */
    .stAlert[data-baseweb="notification"][data-testid="stAlert"] .stAlert {
        background-color: #F5F5F5 !important;
        border: 2px solid #FFD700 !important;
        color: #FFD700 !important;
    }
   
    /* Error boxes */
    .stAlert[data-baseweb="notification"][data-testid="stAlert"] .stAlert {
        background-color: #F5F5F5 !important;
        border: 2px solid #FF6B6B !important;
        color: #FF6B6B !important;
    }
   
    /* Success boxes */
    .stAlert[data-baseweb="notification"][data-testid="stAlert"] .stAlert {
        background-color: #F5F5F5 !important;
        border: 2px solid #4CAF50 !important;
        color: #4CAF50 !important;
    }
                
    .logout-btn {
    background: linear-gradient(135deg, #FFD700 0%, #FFC107 100%);
    color: #000000 !important;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85em;
    text-decoration: none;
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    transition: all 0.2s ease;
    cursor: pointer;
    }
                
    .logout-btn:hover {
    filter: brightness(0.9);
    }
   
    /* Add padding to main content to account for sticky header */
    .main .block-container {
        padding-top: 140px !important;
    }
   
    </style>
    """, unsafe_allow_html=True)
 
# Cache API calls to improve performance
@st.cache_data(ttl=600)  # Cache 
def fetch_kb_summaries(kb_id):
    """Cached function to fetch KB summaries"""
    try:
        res = requests.get(f"{DJANGO_API}/api/kb/{kb_id}/summaries/", timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching summaries: {e}")
        return []
   
 
@st.cache_data(ttl=600)  # Cache data
def list_kb_files(kb_id):
    try:
        res = requests.get(f"{DJANGO_API}/api/kb/{kb_id}/files/")
        if res.headers.get("Content-Type", "").startswith("application/json"):
            return res.json().get("files", [])
        else:
            st.warning("⚠️ Non-JSON response from backend. Showing raw content below.")
            st.text(res.text)
            return []
    except Exception as e:
        st.error(f"Error fetching KB files: {e}")
        return []
 
# LOGIN PAGE
def login_page():
    st.set_page_config(page_title="Login - SyncScribe", layout="centered")
   
    # Apply custom theme
    apply_custom_theme()
   
    # Add custom CSS for the modern login design
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px 20px;
        text-align: center;
    }
   
    .login-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #000000;
        margin: 0 0 10px 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .login-subtitle {
        font-size: 1.1em;
        color: #666666;
        margin: 0 0 40px 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .login-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 40px 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        text-align: left;
    }
   
    .form-group {
        margin-bottom: 20px;
    }
   
    .form-label {
        display: block;
        font-size: 0.9em;
        font-weight: 500;
        color: #333333;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .form-input {
        width: 100%;
        padding: 12px 16px;
        border: 1px solid #E1E5E9;
        border-radius: 8px;
        font-size: 1em;
        transition: border-color 0.3s ease;
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .form-input:focus {
        outline: none;
        border-color: #2F67E8;
        box-shadow: 0 0 0 3px rgba(47, 103, 232, 0.1);
    }
   
    .form-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
    }
   
    .checkbox-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }
   
    .checkbox-group input[type="checkbox"] {
        width: 16px;
        height: 16px;
        accent-color: #2F67E8;
    }
                
   
    .checkbox-label {
        font-size: 0.9em;
        color: #333333;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
                

    .forgot-link {
        font-size: 0.9em;
        color: #2F67E8;
        text-decoration: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .forgot-link:hover {
        text-decoration: underline;
    }
   
    .signin-button {
        width: 100%;
        background: #2F67E8;
        color: #FFFFFF;
        border: none;
        padding: 14px 20px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
   
    .signin-button:hover {
        background: #1E4FD8;
    }
   
    /* KB‐Query overrides */
                
    .kb-container .stButton > button,
    .kb-container .stDownloadButton > button {
        background-color: var(--primary-white) !important;
        color: var(--primary-black) !important;
        border: 1px solid var(--primary-black) !important;
    }
    .kb-container .stButton > button:hover,
    .kb-container .stDownloadButton > button:hover {
        background-color: var(--yellow-hover) !important;
    }

    /* Stats cards */
    .kb-container .stat-card {
        display: inline-block;
        background: var(--primary-white);
        border: 1px solid var(--primary-black);
        border-radius: 6px;
        padding: 8px 12px;
        margin-right: 10px;
        text-align: center;
    }

    /* Meeting cards */
    .kb-container .meeting-card {
        background: var(--primary-white);
        border: 1px solid var(--light-gray);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }

    /* Tighten up the meeting‐title spacing */
    .kb-container .meeting-title {
        margin-bottom: 8px;
        font-weight: 500;
    }

   
    /* Hide Streamlit elements */
    .stApp > header {
        display: none;
    }
   
    .stApp > footer {
        display: none;
    }
   
    .stApp > .main > .block-container {
        padding: 0;
        max-width: none;
    }
    </style>
    """, unsafe_allow_html=True)
   
    # Create a centered container
    col1, col2, col3 = st.columns([1, 2, 1])
   
    with col2:
        # Logo section
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #000000; font-size: 2.2em; font-weight: bold; margin: 0 0 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">SyncScribe</h1>
            <p style="color: #666666; font-size: 1.1em; margin: 0 0 40px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">AI-powered meeting intelligence</p>
        </div>
        """, unsafe_allow_html=True)
       
        # Login card
        with st.container():
           
            # Clear any existing session state
            if 'username_input' not in st.session_state:
                st.session_state.username_input = ""
            if 'password_input' not in st.session_state:
                st.session_state.password_input = ""
 
            # Email field
            st.markdown("""
            <label style="display: block; font-size: 0.9em; font-weight: 500; color: #333333; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">Email address</label>
            """, unsafe_allow_html=True)
           
            username = st.text_input("", key="username_field", value="", placeholder="your.email@coreresources.com", label_visibility="collapsed")
           
            # Password field
            st.markdown("""
            <label style="display: block; font-size: 0.9em; font-weight: 500; color: #333333; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">Password</label>
            """, unsafe_allow_html=True)
           
            password = st.text_input("", type="password", key="password_field", value="", placeholder="Enter your password", label_visibility="collapsed")
           
            # Remember me and forgot password row
            col_a, col_b = st.columns([1, 1])
            with col_a:
                remember_me = st.checkbox("Remember me", key="remember_me")
            with col_b:
                st.markdown("""
                <div style="text-align: right; margin-top: 5px;">
                    <a href="#" style="font-size: 0.9em; color: #2F67E8; text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">Forgot password?</a>
                </div>
                """, unsafe_allow_html=True)
           
            # Sign in button
            if st.button("Sign in", key="login_button", use_container_width=True):
                res = requests.post(
                    f"{DJANGO_API}/api/login/",
                    json={"username": username, "password": password}
                )
 
                if res.status_code == 200 and res.json().get("success"):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful! Welcome to SyncScribe")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password. Please try again.")
           
            st.markdown("</div>", unsafe_allow_html=True)
       
       
 

def render_mermaid_block(answer: str):
    patterns = [r"```mermaid\s+(.*?)```"]
    mermaid_code = None
    for pattern in patterns:
        match = re.search(pattern, answer, re.DOTALL | re.IGNORECASE)
        if match:
            mermaid_code = match.group(1).strip()
            break
 
    if mermaid_code:
        try:
            import streamlit.components.v1 as components
            st.markdown("### 🧭 Flowchart")
            components.html(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <style>
                        .mermaid {{
                            background-color: #f9f9f9;
                            padding: 1rem;
                            border-radius: 8px;
                            overflow-x: auto;
                            font-family: Arial, sans-serif;
                        }}
                        body {{
                            margin: 0;
                            padding: 10px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="mermaid">{mermaid_code}</div>
                    <script>
                        mermaid.initialize({{ startOnLoad: true }});
                    </script>
                </body>
                </html>
                """,
                height=600,
                scrolling=True,
            )
        except Exception as e:
            st.error(f"Failed to render flowchart: {e}")
            st.code(mermaid_code, language="mermaid")
        return True
    return False
 
@st.cache_data(ttl=600)
def get_kb_summary_data(kb_id):
    try:
        res = requests.get(f"{DJANGO_API}/api/kb/{kb_id}/summaries/")
        st.write("DEBUG status code:", res.status_code)
        st.write("DEBUG text:", res.text[:500])  # limit for readability
       
        if res.status_code == 200:
            return res.json()
        else:
            st.error("❌ Failed to load summaries.")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []
    
# MAIN INTERFACE 
def upload_interface():
    # Safe init
    st.session_state.setdefault("summaries",[])
    st.session_state.setdefault("single_summaries", [])
    st.session_state.setdefault("kb_summaries", {})
    st.session_state.setdefault("chat_history", [])
    
    # Clean mode selection with visual feedback
    with st.container():
        mode = st.radio("Mode", ["Single Upload", "KnowledgeBase Uploads"], horizontal=True, key="upload_mode")
        
        # KB selection 
        kb_id = None
        if mode == "KnowledgeBase Uploads":
            kb_id = st.selectbox("📂 Knowledge Base ID", kb_list, key="kb_selector_main")
            if kb_id:
                st.success(f"✅ Selected: {kb_id}")
        else:
            st.info("ℹ️ Single Upload Mode - Files will be processed individually")
    
    # File upload section
    st.markdown("### 📁 Upload Meeting Files")
    
    uploaded_files = st.file_uploader("Upload files (.mp4, .txt, .vtt, .docx)",
                                  type=["mp4", "txt", "vtt", "docx"],
                                  accept_multiple_files=True,
                                  key="file_uploader_main")

    # Prevent duplicate re-processing of files on rerun
    processed_files = {s["filename"] for s in st.session_state["summaries"]}

    # Only upload new files
    new_files = [file for file in uploaded_files if file.name not in processed_files] if uploaded_files else []

    if new_files:
        with st.spinner("🔄 Processing new files to generate summary..."):
            for file in new_files:
                files = {"file": file}
                data = {"kb_id": kb_id} if kb_id else {}
                try:
                    res = requests.post(f"{DJANGO_API}/upload/", files=files, data=data)
                    if res.status_code == 200:
                        summary = res.json().get("summary", "")
                        st.session_state["summaries"].append({
                            "filename": file.name,
                            "summary": summary,
                            "file_key": file.name.rsplit(".", 1)[0]
                        })
                        if mode == "KnowledgeBase Uploads":
                            st.session_state["uploaded_kb_summary"] = summary
                        st.success(f"✅ {file.name} processed successfully")
                    else:
                        st.error(f"❌ {file.name} failed to process")
                except Exception as e:
                    st.error(f"❌ Upload failed for {file.name}: {e}")

    # SINGLE UPLOAD MODE
    if mode == "Single Upload":
        if st.session_state["summaries"]:
            st.markdown("---")
            
            # Expandable file summaries (keeps UI clean)
            with st.expander(f"📝 Uploaded Files ({len(st.session_state['summaries'])} files)", expanded=False):
                for s in st.session_state["summaries"]:
                    st.markdown(f"**📄 {s['filename']}**")
                    st.code(s["summary"], language="markdown")
                    if s != st.session_state["summaries"][-1]:  # Don't add divider after last item
                        st.divider()

            # Chat section with persistent collapsible history
            st.markdown("## 💬 Ask Anything About These Meetings")
            
            # Always show chat history first (before input) so it persists
            if st.session_state["chat_history"]:
                with st.expander(f"💬 Chat History ({len(st.session_state['chat_history'])} messages)", expanded=True):
                    for msg in st.session_state["chat_history"]:
                        with st.chat_message(msg["role"]):
                            if msg["role"] == "assistant" and render_mermaid_block(msg["content"]):
                                st.markdown("✅ Flowchart rendered above.")
                            else:
                                st.markdown(msg["content"])
            
            # Chat input
            chat_container = st.container()
            with chat_container:
                user_input = st.chat_input("Ask your question...", key="single_upload_chat")
                
                # Process user input
                if user_input:
                    # Add user message to history and show immediately
                    st.session_state["chat_history"].append({"role": "user", "content": user_input})
                    
                    # Show the user's question immediately
                    with st.chat_message("user"):
                        st.markdown(user_input)

                    # Prepare API call
                    last_file = st.session_state["summaries"][-1]["file_key"]
                    summary = st.session_state["summaries"][-1]["summary"]
                    payload = {
                        "question": user_input,
                        "summary": summary,
                        "file_key": f"single-uploads/{last_file}"
                    }

                    # Show assistant thinking and get response
                    with st.chat_message("assistant"):
                        with st.spinner("_Generating answer..._"):
                            try:
                                res = requests.post(f"{DJANGO_API}/ask/", json=payload)
                                if res.status_code == 200:
                                    answer = res.json()["answer"]
                                    if render_mermaid_block(answer):
                                        st.markdown("✅ Flowchart rendered above.")
                                    else:
                                        st.markdown(answer)
                                    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                                else:
                                    error_msg = "❌ Failed to fetch answer."
                                    st.error(error_msg)
                                    st.session_state["chat_history"].append({"role": "assistant", "content": error_msg})
                            except Exception as e:
                                error_msg = f"❌ Error: {str(e)}"
                                st.error(error_msg)
                                st.session_state["chat_history"].append({"role": "assistant", "content": error_msg})
        else:
            st.markdown("⚠️ Upload one or more meeting files to start.")

    # KNOWLEDGE BASE MODE
    elif mode == "KnowledgeBase Uploads" and kb_id:
        st.markdown("---")
        
        # Show just uploaded summary if available
        if st.session_state.get("uploaded_kb_summary"):
            with st.expander("📄 Just Uploaded File Summary", expanded=False):
                st.code(st.session_state["uploaded_kb_summary"], language="markdown")

        # File selection section
        st.markdown("### 📚 Query Knowledge Base")
        
        available_files = list_kb_files(kb_id)
        
        # Refresh button in a better location
        col1, col2 = st.columns([3, 1])
        with col1:
            if available_files:
                st.success(f"✅ Found {len(available_files)} files in Knowledge Base")
            else:
                st.warning("⚠️ No files found in Knowledge Base. Please upload files first.")
        with col2:
            if st.button("🔄 Refresh", key="refresh_kb_files"):
                available_files = list_kb_files(kb_id)  # Refresh the list
                st.rerun()

        
        # File selection options
        if available_files:
            file_selection_mode = st.radio("Select files to query:", 
                                         ["All uploaded meetings", "Manually select meetings"], 
                                         horizontal=True, key="kb_file_selection_mode")

            if file_selection_mode == "All uploaded meetings":
                selected_files = available_files
                st.info(f"✅ All {len(selected_files)} files selected")
            else:
                selected_files = st.multiselect("Choose meetings to include:", 
                                               available_files, key="kb_file_multiselect")
                if selected_files:
                    st.success(f"✅ {len(selected_files)} files selected")
        else:
            selected_files = []

        # Chat section for KB with persistent collapsible history
        st.markdown("### 💬 Ask Questions About Knowledge Base")
        
        chat_key = f"chat_history_{kb_id}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        # Always show chat history first (before input) so it persists
        if st.session_state[chat_key]:
            with st.expander(f"💬 Chat History ({len(st.session_state[chat_key])} messages)", expanded=True):
                for msg in st.session_state[chat_key]:
                    with st.chat_message(msg["role"]):
                        if msg["role"] == "assistant" and render_mermaid_block(msg["content"]):
                            st.markdown("✅ Flowchart rendered above.")
                        else:
                            st.markdown(msg["content"])

        # KB chat input
        kb_question = st.chat_input("Ask your KB question...", key="kb_chat_input")

        # Process KB question
        if kb_question:
            if selected_files:
                # Show user message immediately
                st.chat_message("user").markdown(kb_question)

                # Add user message to history
                st.session_state[chat_key].append({"role": "user", "content": kb_question})
                
                # Process KB query
                with st.spinner("_Generating answer..._"):
                    payload = {
                        "question": kb_question,
                        "kb_id": kb_id,
                        "files": selected_files
                    }
                    try:
                        res = requests.post(f"{DJANGO_API}/ask/", json=payload)
                        if res.status_code == 200:
                            answer = res.json()["answer"]
                            st.session_state[chat_key].append({"role": "assistant", "content": answer})
                        else:
                            error_msg = "❌ KB Query failed."
                            st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"❌ KB Error: {str(e)}"
                        st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
                    
                    # Force a rerun to update the chat history display
                    st.rerun()
            else:
                st.warning("⚠️ Please select at least one meeting file before asking.")

    elif mode == "KnowledgeBase Uploads" and not kb_id:
        st.info("👆 Please select a Knowledge Base ID to continue.")


def kb_summary_viewer_clean():
    st.title("📚 Knowledge Base Summary Viewer")

    # — KB Selection & Search —
    hdr_col, search_col = st.columns([2, 3])
    with hdr_col:
        kb_id = st.selectbox("Select Knowledge Base", kb_list, key="kb_selector")
    with search_col:
        search_term = st.text_input("🔍 Search meetings…", placeholder="Title or Recording ID", key="search_input")

    if not kb_id:
        st.info("Please select a Knowledge Base to view summaries.")
        return

    summaries = fetch_kb_summaries(kb_id)
    if not summaries:
        st.info("No summaries found for this Knowledge Base.")
        return

    # — Dedupe & date extraction —
    unique = {}
    for s in summaries:
        rid = s["recording_id"]
        if rid not in unique or len(s["summary_markdown"]) > len(unique[rid]["summary_markdown"]):
            unique[rid] = s

    processed = []
    for s in unique.values():
        processed.append({
            **s,
            "extracted_date": extract_date_from_title(s["title"]) or "–"
        })

    # — Filter —
    filtered = [
        s for s in processed
        if not search_term
        or search_term.lower() in s["title"].lower()
        or search_term.lower() in s["recording_id"].lower()
    ]

    # — Stats —
    stat1, stat2 = st.columns(2)
    stat1.metric("Total Meetings", len(processed))
    stat2.metric("Filtered", len(filtered))
    st.markdown("---")

    if not filtered:
        st.info("No meetings match your search criteria.")
        return

    # — Meeting list —
    for idx, s in enumerate(filtered):
        with st.container():
            # header: ID + title + date
            txt_col, date_col = st.columns([3, 1])
            with txt_col:
                st.markdown(f"### 📌 {s['recording_id']}")
                st.markdown(f"**{s['title']}**")
           

            # action buttons + char count
            btn1, btn2, btn3, info = st.columns([1, 1, 1, 2])
            with btn1:
                if st.button("👁️ View Summary", key=f"view_{idx}"):
                    st.session_state[f"show_{idx}"] = not st.session_state.get(f"show_{idx}", False)
            with btn2:
                st.download_button(
                    "📄 Transcript",
                    data=requests.get(s["transcript_url"]).content,
                    file_name=f"{s['recording_id']}_transcript.txt",
                    mime="text/plain",
                    key=f"dl_trans_{idx}"
                )
            with btn3:
                st.download_button(
                    "🎥 Recording",
                    data=requests.get(s["video_url"]).content,
                    file_name=f"{s['recording_id']}_recording.mp4",
                    mime="video/mp4",
                    key=f"dl_vid_{idx}"
                )
            with info:
                st.caption(f"📝 {len(s['summary_markdown']):,} chars")

            # expandable summary
            if st.session_state.get(f"show_{idx}", False):
                with st.expander("📋 Meeting Summary", expanded=True):
                    st.markdown(s["summary_markdown"])

            st.markdown("---")
       
@st.cache_data(ttl=600) 
def extract_date_from_title(title):
    """Extract date from title if it contains date information"""
    import re
    date_patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
        r'(\w+ \d{1,2},? \d{4})',    # Month DD, YYYY
        r'(\d{1,2}-\d{1,2}-\d{4})',  # MM-DD-YYYY
    ]
   
    for pattern in date_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
 
# ENTRY
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
 
    if not st.session_state.logged_in:
        login_page()
        return
 
    # Set page config for better layout
    st.set_page_config(
        page_title="SyncScribe - AI-Powered Meeting Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
   
    # Apply custom theme
    apply_custom_theme()

    # set up header layout
    left, right = st.columns([9, 1])  # tweak these ratios to shift your button further right/left


    with left:
        st.markdown(f"""
        <div style="width:100%;">

        <!-- flex row with title on left and welcome on right -->
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h1 style="margin:-20px 0 -10px; color:#000;">SyncScribe</h1>
            <span style="color: #6C757D; font-size:0.9em; font-weight:500;">
            Welcome, {st.session_state.get('username', 'User')}
            </span>
        </div>

        <!-- subtitle below -->
        <p style="margin-top:4px; color:#666;">AI-powered meeting intelligence</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        if st.button("Logout", key="logout_header", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()


   
    # Tab Navigation with updated names
    tab1, tab2 = st.tabs(["📤 Upload & Chat", "📚 Knowledge Base Summary Viewer"])
   
    with tab1:
        upload_interface()
   
    with tab2:
        kb_summary_viewer_clean()
   
 
if __name__ == "__main__":
    main()
