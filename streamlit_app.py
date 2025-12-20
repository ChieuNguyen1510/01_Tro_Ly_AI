import streamlit as st
from openai import OpenAI
from base64 import b64encode

# =========================
# 🔴 QUAN TRỌNG – FIX SIDEBAR
# =========================
st.set_page_config(
    page_title="AI Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"  # <-- FIX MẤT SIDEBAR
)

# =========================
# Ẩn toolbar nhưng KHÔNG phá sidebar
# =========================
st.markdown(
    """
    <style>
        /* Ẩn toolbar */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* ❌ KHÔNG ẩn toàn bộ header */
        /* ❌ KHÔNG ẩn nút sidebar */

        /* Ẩn nút Manage app */
        [data-testid="manage-app-button"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Utils
# =========================
def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as file:
        return file.read()

def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()

# =========================
# Language dictionary
# =========================
translations = {
    'vi': {
        'title': 'Chào mừng đến với Chatbot AI',
        'new_chat': 'Bắt đầu cuộc trò chuyện mới',
        'chat_placeholder': 'Nhập câu hỏi của bạn ở đây...',
        'typing': 'Assistant đang gõ...',
    },
    'en': {
        'title': 'Welcome to AI Chatbot',
        'new_chat': 'New chat',
        'chat_placeholder': 'Enter your question here...',
        'typing': 'Assistant is typing...',
    }
}

assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# =========================
# Session state
# =========================
if "language" not in st.session_state:
    st.session_state.language = "vi"

if "theme" not in st.session_state:
    st.session_state.theme = "light"

# =========================
# Sidebar (LUÔN HIỆN)
# =========================
with st.sidebar:
    st.header("⚙️ Cài đặt / Settings")

    selected_lang = st.selectbox(
        "Ngôn ngữ / Language",
        ["vi", "en"],
        index=0 if st.session_state.language == "vi" else 1,
        format_func=lambda x: "Tiếng Việt" if x == "vi" else "English"
    )

    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

    selected_theme = st.radio(
        "Theme",
        ["light", "dark"],
        index=0 if st.session_state.theme == "light" else 1
    )

    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

t = translations[st.session_state.language]

# =========================
# Background + Theme CSS
# =========================
try:
    bg_image_base64 = img_to_base64("background.png")
    st.markdown(
        f"""
        <style>
        :root {{
            --bg-color: {'#ffffff' if st.session_state.theme == 'light' else '#0e1117'};
            --text-color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'};
            --card-bg: {'rgba(255,255,255,0.9)' if st.session_state.theme == 'light' else 'rgba(0,0,0,0.8)'};
            --assistant-bg: {'#f0f7ff' if st.session_state.theme == 'light' else '#1e293b'};
            --user-bg: {'#e6ffe6' if st.session_state.theme == 'light' else '#1e4a2e'};
            --input-bg: {'#fafafa' if st.session_state.theme == 'light' else '#1f2937'};
        }}

        .stAppViewContainer {{
            background-image: url('data:image/png;base64,{bg_image_base64}');
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            color: var(--text-color);
        }}

        .main .block-container {{
            background: var(--card-bg);
            border-radius: 10px;
            padding: 12px;
            max-height: 80vh;
            overflow-y: auto;
        }}

        .message {{
            padding: 12px;
            border-radius: 12px;
            max-width: 75%;
            display: flex;
            gap: 12px;
            margin: 8px 0;
        }}

        .assistant {{ background: var(--assistant-bg); }}
        .user {{
            background: var(--user-bg);
            margin-left: auto;
            flex-direction: row-reverse;
        }}

        .icon {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
        }}

        .typing::after {{
            content: "{t['typing']}";
            animation: blink 1s infinite;
        }}

        @keyframes blink {{
            0% {{opacity:1}}
            50% {{opacity:0.5}}
            100% {{opacity:1}}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except:
    pass

# =========================
# Logo
# =========================
try:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# =========================
# Title
# =========================
st.markdown(
    f"<h2 style='text-align:center'>{t['title']}</h2>",
    unsafe_allow_html=True
)

# =========================
# OpenAI
# =========================
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [
        INITIAL_SYSTEM_MESSAGE,
        INITIAL_ASSISTANT_MESSAGE
    ]

# =========================
# New Chat
# =========================
if st.button(t["new_chat"]):
    st.session_state.messages = [
        INITIAL_SYSTEM_MESSAGE,
        INITIAL_ASSISTANT_MESSAGE
    ]
    st.rerun()

# =========================
# Chat history
# =========================
for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(
            f"""
            <div class="message assistant">
                <img src="data:image/png;base64,{assistant_icon}" class="icon"/>
                <div>{m['content']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif m["role"] == "user":
        st.markdown(
            f"""
            <div class="message user">
                <img src="data:image/png;base64,{user_icon}" class="icon"/>
                <div>{m['content']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# Chat input
# =========================
if prompt := st.chat_input(t["chat_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})

    typing = st.empty()
    typing.markdown('<div class="typing"></div>', unsafe_allow_html=True)

    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=st.session_state.messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    typing.empty()

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    st.rerun()
