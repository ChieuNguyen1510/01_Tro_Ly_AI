import streamlit as st
from openai import OpenAI
from base64 import b64encode

# --- [PHẦN MỚI] 1. CÀI ĐẶT STATE & SIDEBAR ---
if "language" not in st.session_state:
    st.session_state.language = "Vietnamese"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# Tạo Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    
    # Đổi Ngôn ngữ
    lang_options = ["Vietnamese", "English"]
    lang_idx = 0 if st.session_state.language == "Vietnamese" else 1
    selected_lang = st.radio("Ngôn ngữ / Language", lang_options, index=lang_idx)
    
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
        
    st.divider()
    
    # Đổi Dark/Light Mode
    is_dark = st.toggle("Chế độ tối (Dark Mode)", value=(st.session_state.theme == "Dark"))
    new_theme = "Dark" if is_dark else "Light"
    
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# --- [PHẦN MỚI] 2. ĐỊNH NGHĨA BIẾN MÀU & CHỮ ---
# Định nghĩa màu sắc dựa trên Theme (Giữ cấu trúc layout, chỉ thay mã màu)
if st.session_state.theme == "Light":
    # Màu gốc từ code của bạn
    CONTAINER_BG = "rgba(255, 255, 255, 0.9)"
    CHAT_INPUT_BG = "rgba(255, 255, 255, 0.9)"
    ASSISTANT_BG = "#f0f7ff"
    USER_BG = "#e6ffe6"
    TEXT_COLOR = "#000000"
    SIDEBAR_BG = "rgba(255, 255, 255, 0.9)"
else:
    # Màu cho chế độ Dark Mode
    CONTAINER_BG = "rgba(30, 30, 30, 0.9)"
    CHAT_INPUT_BG = "rgba(50, 50, 50, 0.9)"
    ASSISTANT_BG = "#262730" # Màu tối
    USER_BG = "#1e3a1e"      # Xanh lá tối
    TEXT_COLOR = "#ffffff"   # Chữ trắng
    SIDEBAR_BG = "rgba(30, 30, 30, 0.9)"

# Định nghĩa văn bản dựa trên Ngôn ngữ
if st.session_state.language == "Vietnamese":
    TXT_PLACEHOLDER = "Nhập câu hỏi của bạn..."
    TXT_TYPING = "Assistant đang trả lời..."
    TXT_NEW_CHAT = "New chat" # Giữ nguyên tên nút như code gốc hoặc đổi thành "Cuộc trò chuyện mới"
else:
    TXT_PLACEHOLDER = "Enter your question here..."
    TXT_TYPING = "Assistant is typing..."
    TXT_NEW_CHAT = "New chat"

# --- [PHẦN CŨ] LOGIC GỐC ---

# Ẩn thanh công cụ và nút "Manage app" (Code gốc)
st.markdown(
    """
    <style>
        /* Ẩn các nút Share, Star, Edit, GitHub */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stAppViewBlockContainer"] > div > div > div > div > div {
            display: none !important;
        }
        /* Ẩn nút Manage app */
        [data-testid="manage-app-button"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hàm đọc nội dung từ file văn bản
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except: return ""

# Hàm chuyển ảnh thành base64
def img_to_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            return b64encode(f.read()).decode()
    except: return ""

# Chuyển ảnh sang base64
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# CSS cho background (Code gốc - Đã chèn biến màu vào)
try:
    bg_image_base64 = img_to_base64("background.png")
    st.markdown(
        f"""
        <style>
            /* Background đơn giản đã hoạt động */
            .stAppViewContainer {{
                background-image: url('data:image/png;base64,{bg_image_base64}');
                background-size: cover;
                background-position: center top;
                background-repeat: no-repeat;
                background-attachment: fixed;
                height: 100vh;
                width: 100vw;
                margin: 0;
                padding: 0;
                margin-top: -10px !important;
            }}
            body {{
                background-image: url('data:image/png;base64,{bg_image_base64}');
                background-size: cover;
                background-position: center top;
                background-repeat: no-repeat;
                background-attachment: fixed;
                height: 100vh;
                width: 100vw;
                margin: 0;
                padding: 0;
                margin-top: -10px !important;
                color: {TEXT_COLOR} !important; /* [EDIT] Thêm màu chữ động */
            }}
            
            /* Làm header transparent */
            section[data-testid="stDecoration"] {{
                background: transparent !important;
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}
            [data-testid="stHeader"] {{
                background: transparent !important;
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}
            
            /* Làm footer (chat input) transparent background */
            [data-testid="stChatInput"] {{
                background: transparent !important;
                border: none !important;
            }}
            [data-testid="stChatInput"] > div > div {{
                background: {CHAT_INPUT_BG} !important; /* [EDIT] Màu nền input động */
                border-radius: 10px !important;
                backdrop-filter: blur(5px) !important;
            }}
            [data-testid="stChatInput"] textarea {{
                color: {TEXT_COLOR} !important; /* [EDIT] Màu chữ input */
            }}
            
            /* Nội dung chính */
            .main .block-container {{
                background-color: {CONTAINER_BG} !important; /* [EDIT] Màu nền container động */
                border-radius: 10px !important;
                padding: 10px !important;
                backdrop-filter: blur(5px) !important;
                margin: 10px !important;
                max-height: 80vh !important;
                overflow-y: auto !important;
                margin-top: 0 !important;
            }}

            /* [EDIT] Style thêm cho Sidebar để đồng bộ layout */
            section[data-testid="stSidebar"] {{
                background-color: {SIDEBAR_BG} !important;
                backdrop-filter: blur(5px);
            }}
            section[data-testid="stSidebar"] h1, 
            section[data-testid="stSidebar"] label, 
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] p {{
                color: {TEXT_COLOR} !important;
            }}

        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning("File background.png không tìm thấy.")

# Hiển thị logo (nếu có)
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; color: {TEXT_COLOR};">{title_content}</h1>""",
    unsafe_allow_html=True
)

# OpenAI API
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Tin nhắn hệ thống
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# Khởi tạo session_state.messages nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Nút "Bắt đầu cuộc trò chuyện mới"
if st.button(TXT_NEW_CHAT): # [EDIT] Dùng biến ngôn ngữ
    # Reset messages về trạng thái ban đầu
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    # Làm mới giao diện bằng cách rerun ứng dụng
    st.rerun()

# CSS cải tiến (Code gốc - Đã chèn biến màu vào)
st.markdown(
    f"""
    <style>
        .message {{
            padding: 12px !important;
            border-radius: 12px !important;
            max-width: 75% !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
            margin: 8px 0 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            color: {TEXT_COLOR} !important; /* [EDIT] Màu chữ message */
        }}
        .assistant {{
            background-color: {ASSISTANT_BG} !important; /* [EDIT] Màu nền assistant */
        }}
        .user {{
            background-color: {USER_BG} !important; /* [EDIT] Màu nền user */
            text-align: right !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }}
        .icon {{
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            border: 1px solid #ddd !important;
        }}
        .text {{
            flex: 1 !important;
            font-size: 16px !important;
            line-height: 1.4 !important;
        }}
        .typing {{
            font-style: italic !important;
            color: #888 !important;
            padding: 5px 10px !important;
            display: flex !important;
            align-items: center !important;
        }}
        @keyframes blink {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        .typing::after {{
            content: "..." !important;
            animation: blink 1s infinite !important;
        }}
        [data-testid="stChatInput"] {{
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            padding: 8px !important;
            background-color: #fafafa !important;
        }}
        /* Tùy chỉnh nút "New chat" */
        div.stButton > button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 2px solid #FFFFFF !important;
            padding: 6px 6px !important;
            font-size: 14px !important;
            border: none !important;
            display: block !important;
            margin: 10px 0px !important; /* Căn giữa nút */
        }}
        div.stButton > button:hover {{
            background-color: #45a049 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Hiển thị lịch sử tin nhắn (trừ system)
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

# Ô nhập câu hỏi
if prompt := st.chat_input(TXT_PLACEHOLDER): # [EDIT] Dùng biến ngôn ngữ
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)
    # Assistant đang trả lời...
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        f'<div class="typing">{TXT_TYPING}</div>', # [EDIT] Dùng biến ngôn ngữ
        unsafe_allow_html=True
    )
    # Gọi API
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
        response = f"Lỗi: {e}"

    # Xóa dòng "Assistant is typing..."
    typing_placeholder.empty()
    # Hiển thị phản hồi từ assistant
    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})