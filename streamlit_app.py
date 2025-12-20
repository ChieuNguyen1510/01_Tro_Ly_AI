import streamlit as st
from openai import OpenAI
from base64 import b64encode
# Ẩn thanh công cụ và nút "Manage app"
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
    with open(name_file, "r", encoding="utf-8") as file:
        return file.read()
# Hàm chuyển ảnh thành base64
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()
# MỚI: Dictionary dịch ngôn ngữ (dễ mở rộng)
translations = {
    'vi': {
        'title': 'Chào mừng đến với Chatbot AI', # Sử dụng rfile("00.xinchao.txt") nếu muốn từ file
        'new_chat': 'Bắt đầu cuộc trò chuyện mới',
        'chat_placeholder': 'Nhập câu hỏi của bạn ở đây...',
        'typing': 'Assistant đang gõ...',
        'show_sidebar': 'Hiện thanh bên (Ngôn ngữ & Theme)',
    },
    'en': {
        'title': 'Welcome to AI Chatbot',
        'new_chat': 'New chat',
        'chat_placeholder': 'Enter your question here...',
        'typing': 'Assistant is typing...',
        'show_sidebar': 'Show Sidebar (Language & Theme)',
    }
}
# Chuyển ảnh sang base64
try:
    assistant_icon = img_to_base64("assistant_icon.png")
except FileNotFoundError:
    assistant_icon = ""  # Fallback nếu thiếu file
try:
    user_icon = img_to_base64("user_icon.png")
except FileNotFoundError:
    user_icon = ""  # Fallback nếu thiếu file
# MỚI: Khởi tạo session_state cho language và theme
if "language" not in st.session_state:
    st.session_state.language = 'vi' # Default: Tiếng Việt
if "theme" not in st.session_state:
    st.session_state.theme = 'light' # Default: Light
# Lấy text theo ngôn ngữ hiện tại (ĐẶT TRƯỚC SIDEBAR ĐỂ TRÁNH LỖI)
t = translations[st.session_state.language]
# TÍNH TOÁN CSS VARIABLES TRƯỚC ĐỂ TRÁNH LỖI F-STRING
if st.session_state.theme == 'light':
    bg_color = '#ffffff'
    text_color = '#000000'
    card_bg = 'rgba(255, 255, 255, 0.9)'
    assistant_bg = '#f0f7ff'
    user_bg = '#e6ffe6'
    input_bg = '#fafafa'
else:
    bg_color = '#0e1117'
    text_color = '#ffffff'
    card_bg = 'rgba(0, 0, 0, 0.8)'
    assistant_bg = '#1e293b'
    user_bg = '#1e4a2e'
    input_bg = '#1f2937'
# MỚI: Sidebar cho ngôn ngữ và theme - ĐẶT SỚM NHẤT ĐỂ ƯU TIÊN HIỂN THỊ
with st.sidebar:
    st.markdown(f'<div style="background-color: {bg_color}; color: {text_color}; padding: 10px; height: 100vh;">', unsafe_allow_html=True)
    st.header("Cài đặt / Settings")
   
    # 1. Chọn ngôn ngữ
    selected_lang = st.selectbox(
        "Ngôn ngữ / Language",
        options=['vi', 'en'],
        index=0 if st.session_state.language == 'vi' else 1,
        format_func=lambda x: 'Tiếng Việt' if x == 'vi' else 'English'
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun() # Refresh để áp dụng ngôn ngữ mới
   
    # 2. Chọn theme
    selected_theme = st.radio(
        "Theme",
        options=['light', 'dark'],
        index=0 if st.session_state.theme == 'light' else 1
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun() # Refresh để áp dụng theme mới
    st.markdown('</div>', unsafe_allow_html=True)
# CSS cho background với base64 (cải tiến để cover thêm phần trên, loại bỏ margin/padding top)
try:
    bg_image_base64 = img_to_base64("background.png")
    st.markdown(
        f"""
        <style>
            /* MỚI: CSS theme động dựa trên session_state */
            :root {{
                --bg-color: {bg_color};
                --text-color: {text_color};
                --card-bg: {card_bg};
                --assistant-bg: {assistant_bg};
                --user-bg: {user_bg};
                --input-bg: {input_bg};
            }}
           
            /* Background đơn giản đã hoạt động - thêm transparent cho header và footer, fix crop top */
            .stAppViewContainer {{
                background-image: url('data:image/png;base64,{bg_image_base64}');
                background-size: cover;
                background-position: center top; /* Căn giữa theo top để tránh crop trên */
                background-repeat: no-repeat;
                background-attachment: fixed;
                height: 100vh;
                width: 100vw;
                margin: 0;
                padding: 0;
                margin-top: -10px !important; /* Kéo lên để cover phần top bị mất */
                color: var(--text-color);
            }}
            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
            }}
          
            /* Làm header transparent để thấy background, loại bỏ padding top */
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
                color: var(--text-color);
            }}
            [data-testid="stChatInput"] > div > div {{
                background: var(--input-bg) !important;
                border-radius: 10px !important;
                backdrop-filter: blur(5px) !important;
                color: var(--text-color);
            }}
          
            /* Nội dung chính */
            .main .block-container {{
                background-color: var(--card-bg) !important;
                border-radius: 10px !important;
                padding: 10px !important;
                backdrop-filter: blur(5px) !important;
                margin: 10px !important;
                max-height: 80vh !important;
                overflow-y: auto !important;
                margin-top: 0 !important; /* Đảm bảo không margin top thêm */
                color: var(--text-color);
            }}
            /* FORCE SIDEBAR HIỂN THỊ */
            section[data-testid="stSidebar"] {{
                display: block !important;
                visibility: visible !important;
                width: 250px !important;
                position: fixed !important;
                left: 0 !important;
                top: 0 !important;
                z-index: 999 !important;
            }}
            .css-1d391kg {{
                display: block !important;
                width: 250px !important;
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
                height: 100vh !important;
            }}
            /* Ẩn hamburger icon toggle sidebar để tránh ẩn nhầm */
            [data-testid="collapsedControl"] {{
                display: none !important;
            }}
            .stSidebar {{
                display: block !important;
                transform: translateX(0) !important;
                width: 250px !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning("File background.png không tìm thấy. Vui lòng đặt file vào thư mục app.")
# Hiển thị logo (nếu có)
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass
# Hiển thị tiêu đề (MỚI: Sử dụng text từ translations, hoặc giữ rfile nếu file hỗ trợ đa ngôn ngữ)
# title_content = rfile("00.xinchao.txt") # Giữ nếu file là tiếng Việt, hoặc tách file riêng
st.markdown(
    f'<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; color: {text_color};">{t["title"]}</h1>',
    unsafe_allow_html=True
)
# THÊM: Nút toggle sidebar thủ công trong main area (nếu sidebar bị ẩn)
if st.button(t['show_sidebar'], key="toggle_sidebar"):
    st.rerun()  # Rerun để force refresh sidebar
# OpenAI API
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
# Tin nhắn hệ thống (MỚI: Có thể dịch system prompt nếu cần, nhưng giữ nguyên vì là training)
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}
# Khởi tạo session_state.messages nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
# Nút "Bắt đầu cuộc trò chuyện mới" (MỚI: Text động)
if st.button(t['new_chat'], key="new_chat"):
    # Reset messages về trạng thái ban đầu
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    # Làm mới giao diện bằng cách rerun ứng dụng
    st.rerun()
# CSS cải tiến (MỚI: Áp dụng theme cho messages và buttons) - SỬ DỤNG CONCAT ĐỂ TRÁNH LỖI
typing_content = t['typing'].replace('"', '\\"')  # Escape quotes if any
css_messages = f"""
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
        color: var(--text-color);
    }}
    .assistant {{
        background-color: var(--assistant-bg) !important;
    }}
    .user {{
        background-color: var(--user-bg) !important;
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
        color: var(--text-color);
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
        content: "{typing_content}" !important;
        animation: blink 1s infinite !important;
    }}
    [data-testid="stChatInput"] {{
        border: 2px solid #ddd !important;
        border-radius: 8px !important;
        padding: 8px !important;
        background-color: var(--input-bg) !important;
        color: var(--text-color);
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
    /* Nút toggle sidebar */
    div.stButton > button:first-of-type {{
        background-color: #FF6B6B !important;
        margin-top: 10px !important;
    }}
</style>
"""
st.markdown(css_messages, unsafe_allow_html=True)
# Hiển thị lịch sử tin nhắn (trừ system)
for message in st.session_state.messages:
    if message["role"] == "assistant":
        icon_html = f'<img src="data:image/png;base64,{assistant_icon}" class="icon" />' if assistant_icon else '<div class="icon" style="background: #ccc; width: 32px; height: 32px; border-radius: 50%;"></div>'
        st.markdown(f'''
        <div class="message assistant">
            {icon_html}
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message["role"] == "user":
        icon_html = f'<img src="data:image/png;base64,{user_icon}" class="icon" />' if user_icon else '<div class="icon" style="background: #ccc; width: 32px; height: 32px; border-radius: 50%;"></div>'
        st.markdown(f'''
        <div class="message user">
            {icon_html}
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
# Ô nhập câu hỏi (MỚI: Placeholder động theo ngôn ngữ)
if prompt := st.chat_input(t['chat_placeholder']):
    st.session_state.messages.append({"role": "user", "content": prompt})
    icon_html = f'<img src="data:image/png;base64,{user_icon}" class="icon" />' if user_icon else '<div class="icon" style="background: #ccc; width: 32px; height: 32px; border-radius: 50%;"></div>'
    st.markdown(f'''
    <div class="message user">
        {icon_html}
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)
    # Assistant đang trả lời...
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        '<div class="typing"></div>', # Sử dụng ::after trong CSS
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
            if chunk.choices and chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
    except Exception as e:
        response = f"Lỗi API: {str(e)}"
    # Xóa dòng "Assistant is typing..."
    typing_placeholder.empty()
    # Hiển thị phản hồi từ assistant
    icon_html = f'<img src="data:image/png;base64,{assistant_icon}" class="icon" />' if assistant_icon else '<div class="icon" style="background: #ccc; width: 32px; height: 32px; border-radius: 50%;"></div>'
    st.markdown(f'''
    <div class="message assistant">
        {icon_html}
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)
   
    st.session_state.messages.append({"role": "assistant", "content": response})