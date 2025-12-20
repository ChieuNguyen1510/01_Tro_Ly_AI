import streamlit as st
from openai import OpenAI
from base64 import b64encode

# Thiết lập trang (phải để đầu tiên)
st.set_page_config(page_title="AI Chat", layout="wide")

# --- 1. QUẢN LÝ TRẠNG THÁI (STATE) ---
if "language" not in st.session_state:
    st.session_state.language = "Vietnamese"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# --- 2. THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.header("Cài đặt / Settings")
    
    # Đổi ngôn ngữ
    lang = st.radio("Ngôn ngữ / Language", ["Vietnamese", "English"], 
                    index=0 if st.session_state.language == "Vietnamese" else 1)
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()
        
    st.divider()
    
    # Đổi giao diện
    is_dark = st.toggle("Chế độ Tối / Dark Mode", value=(st.session_state.theme == "Dark"))
    new_theme = "Dark" if is_dark else "Light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# --- 3. THIẾT LẬP BIẾN MÀU SẮC & NGÔN NGỮ ---
if st.session_state.theme == "Light":
    # Màu gốc của bạn
    MAIN_BG_COLOR = "rgba(255, 255, 255, 0.9)"
    TEXT_COLOR = "#000000"
    ASSISTANT_BG = "#f0f7ff"
    USER_BG = "#e6ffe6"
    INPUT_BG = "rgba(255, 255, 255, 0.9)"
else:
    # Màu Dark Mode
    MAIN_BG_COLOR = "rgba(30, 30, 30, 0.9)"
    TEXT_COLOR = "#ffffff"
    ASSISTANT_BG = "#2c3e50" # Xanh tối
    USER_BG = "#1e3a1e"      # Xanh lá tối
    INPUT_BG = "rgba(50, 50, 50, 0.9)"

# Thiết lập văn bản theo ngôn ngữ
if st.session_state.language == "Vietnamese":
    txt_new_chat = "Bắt đầu cuộc trò chuyện mới"
    txt_placeholder = "Nhập câu hỏi của bạn..."
    txt_typing = "Assistant đang trả lời..."
else:
    txt_new_chat = "New chat"
    txt_placeholder = "Enter your question here..."
    txt_typing = "Assistant is typing..."

# --- 4. CODE XỬ LÝ FILE & ẢNH (GIỮ NGUYÊN) ---
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except: return ""

def img_to_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            return b64encode(f.read()).decode()
    except: return ""

assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")
bg_image_base64 = img_to_base64("background.png")

# --- 5. CSS (GIỮ NGUYÊN LAYOUT, CHỈ THAY MÀU VÀO CHỖ CẦN THIẾT) ---
st.markdown(
    f"""
    <style>
        /* Ẩn toolbar (giữ nguyên yêu cầu của bạn) */
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="manage-app-button"] {{ display: none !important; }}
        
        /* Background chính */
        .stAppViewContainer {{
            background-image: url('data:image/png;base64,{bg_image_base64}');
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            height: 100vh; width: 100vw;
            margin: 0; padding: 0;
            margin-top: -10px !important;
        }}
        
        /* Header transparent */
        section[data-testid="stDecoration"], [data-testid="stHeader"] {{
            background: transparent !important;
            padding-top: 0 !important; margin-top: 0 !important;
        }}
        
        /* Chat Input (Footer) - Thay màu nền động */
        [data-testid="stChatInput"] {{
            background: transparent !important;
            border: none !important;
        }}
        [data-testid="stChatInput"] > div > div {{
            background: {INPUT_BG} !important;
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            color: {TEXT_COLOR} !important;
        }}
        /* Màu chữ khi gõ trong ô input */
        [data-testid="stChatInput"] textarea {{
            color: {TEXT_COLOR} !important; 
            background: transparent !important;
        }}

        /* Nội dung chính (Container) - Thay màu nền động */
        .main .block-container {{
            background-color: {MAIN_BG_COLOR} !important;
            border-radius: 10px !important;
            padding: 10px !important;
            backdrop-filter: blur(5px) !important;
            margin: 10px !important;
            max-height: 80vh !important;
            overflow-y: auto !important;
        }}

        /* Màu chữ toàn bộ trang */
        body, p, div, h1, h2 {{
            color: {TEXT_COLOR} !important;
        }}

        /* CSS Message Box (Giữ nguyên layout, chỉ thay màu) */
        .message {{
            padding: 12px !important;
            border-radius: 12px !important;
            max-width: 75% !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
            margin: 8px 0 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            color: {TEXT_COLOR} !important; /* Thêm màu chữ cho message */
        }}
        .assistant {{
            background-color: {ASSISTANT_BG} !important;
        }}
        .user {{
            background-color: {USER_BG} !important;
            text-align: right !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }}
        .icon {{
            width: 32px !important; height: 32px !important;
            border-radius: 50% !important; border: 1px solid #ddd !important;
        }}
        .text {{
            flex: 1 !important; font-size: 16px !important; line-height: 1.4 !important;
        }}
        .typing {{
            font-style: italic !important; color: #888 !important;
            padding: 5px 10px !important; display: flex !important; align-items: center !important;
        }}
        
        /* CSS cho Sidebar (để nhìn đẹp hơn trên nền kính) */
        section[data-testid="stSidebar"] {{
            background-color: {MAIN_BG_COLOR} !important;
            backdrop-filter: blur(10px);
        }}
        
        /* Nút New chat */
        div.stButton > button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            padding: 6px 6px !important;
            width: 100%;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 6. LOGIC CHAT (GIỮ NGUYÊN) ---

# Hiển thị logo
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except: pass

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; color: {TEXT_COLOR};">{title_content}</h1>""",
    unsafe_allow_html=True
)

openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

if st.button(txt_new_chat):
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.rerun()

# Hiển thị lịch sử
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'''
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'''
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# Ô nhập câu hỏi (dùng biến ngôn ngữ txt_placeholder)
if prompt := st.chat_input(txt_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        f'<div class="typing">{txt_typing}</div>',
        unsafe_allow_html=True
    )
    
    response = ""
    try:
        stream = client.chat.completions.create(
            model=rfile("module_chatgpt.txt").strip(),
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                response += chunk.choices[0].delta.content or ""
    except Exception as e:
        response = f"Error: {e}"

    typing_placeholder.empty()
    
    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})