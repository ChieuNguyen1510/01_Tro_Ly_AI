import streamlit as st
from openai import OpenAI
from base64 import b64encode
import PyPDF2 # Thêm import để đọc PDF
# MỚI: Set page config để wide layout, giúp sidebar có chỗ hơn và luôn mở
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded" # Default: Luôn mở sidebar khi load
)
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
# Hàm đọc nội dung từ file văn bản (giữ nguyên cho các file khác nếu cần)
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.warning(f"File {name_file} không tìm thấy. Sử dụng mặc định.")
        return ""
# MỚI: Hàm đọc và trích xuất text từ PDF (chỉ dùng cho system data)
def read_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n" # Thêm newline giữa các trang
            return text.strip()
    except FileNotFoundError:
        st.error(f"File {pdf_path} không tìm thấy. Vui lòng đặt file vào thư mục app.")
        return ""
    except Exception as e:
        st.error(f"Lỗi khi đọc PDF: {str(e)}")
        return ""
# Hàm chuyển ảnh thành base64
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()
# MỚI: Dictionary dịch ngôn ngữ (dễ mở rộng)
translations = {
    'vi': {
        'title': 'Chào mừng đến với Chatbot AI',
        'new_chat': 'Trò chuyện mới',
        'chat_placeholder': 'Nhập câu hỏi của bạn ở đây...',
        'typing': 'Assistant đang soạn...',
    },
    'en': {
        'title': 'Welcome to AI Chatbot',
        'new_chat': 'New chat',
        'chat_placeholder': 'Enter your question here...',
        'typing': 'Assistant is typing...',
    }
}
# Chuyển ảnh sang base64
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")
# MỚI: Khởi tạo session_state cho language và theme
if "language" not in st.session_state:
    st.session_state.language = 'vi' # Default: Tiếng Việt
if "theme" not in st.session_state:
    st.session_state.theme = 'light' # Default: Light
# MỚI: Sidebar cho ngôn ngữ và theme (sẽ luôn mở nhờ page_config)
with st.sidebar:
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
# Lấy text theo ngôn ngữ hiện tại
t = translations[st.session_state.language]
# MỚI: Chọn ảnh background dựa trên theme
bg_file = "background_light.png" if st.session_state.theme == 'light' else "background_dark.png"
# CSS cho background với base64 (cải tiến để cover thêm phần trên, loại bỏ margin/padding top)
try:
    bg_image_base64 = img_to_base64(bg_file)
    st.markdown(
        f"""
        <style>
            /* MỚI: CSS theme động dựa trên session_state */
            :root {{
                --bg-color: {'#ffffff' if st.session_state.theme == 'light' else '#0e1117'};
                --text-color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'};
                --card-bg: {'rgba(255, 255, 255, 0.9)' if st.session_state.theme == 'light' else 'rgba(0, 0, 0, 0.8)'};
                --assistant-bg: {'#f0f7ff' if st.session_state.theme == 'light' else '#1e293b'};
                --user-bg: {'#e6ffe6' if st.session_state.theme == 'light' else '#1e4a2e'};
                --input-bg: {'rgba(255, 255, 255, 0.1)' if st.session_state.theme == 'light' else 'rgba(0, 0, 0, 0.3)'}; /* SỬA: Giảm opacity để transparent hơn */
            }}
         
            /* Background đơn giản đã hoạt động - thêm transparent cho header và footer, fix crop top */
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
        
            /* SỬA: Làm footer (chat input) transparent hoàn toàn hơn, loại bỏ nền trắng */
            [data-testid="stChatInput"] {{
                background: transparent !important;
                border: none !important;
                color: var(--text-color);
                /* Thêm: Đảm bảo toàn bộ container input transparent */
                box-shadow: none !important;
            }}
            [data-testid="stChatInput"] > div > div {{
                background: transparent !important; /* SỬA: Transparent hoàn toàn, không dùng var(--input-bg) nữa */
                border: 1px solid rgba(255, 255, 255, 0.2) !important; /* Thêm border nhẹ để phân biệt */
                border-radius: 10px !important;
                backdrop-filter: blur(5px) !important; /* Giữ blur để text dễ đọc trên background */
                color: var(--text-color);
                padding: 8px 12px !important; /* Thêm padding cho thoải mái */
            }}
            [data-testid="stChatInput"] input {{
                background: transparent !important; /* Đảm bảo input field bên trong cũng transparent */
                border: none !important;
                color: var(--text-color);
                outline: none !important;
            }}
            [data-testid="stChatInput"] input::placeholder {{
                color: rgba(255, 255, 255, 0.7) !important; /* Placeholder dễ thấy hơn trên background */
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
                margin-top: 0 !important;
                color: var(--text-color);
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning(f"File {bg_file} không tìm thấy. Vui lòng đặt file vào thư mục app.")
# Hiển thị logo (nếu có)
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass
# Hiển thị tiêu đề
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; color: var(--text-color);">{t['title']}</h1>""",
    unsafe_allow_html=True
)
# OpenAI API
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
# MỚI: System từ PDF (data), Assistant từ file text cũ, Model từ file text
pdf_data = read_pdf("data.pdf") # Chỉ dùng cho system prompt (data)
assistant_content = rfile("02.assistant.txt") # Lời chào giữ nguyên
model_name = rfile("module_chatgpt.txt").strip() or "gpt-4o-mini" # Model từ file hoặc fallback
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": pdf_data} # System dùng PDF data
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": assistant_content or "Xin chào! Tôi là trợ lý AI của bạn. Hãy hỏi tôi bất cứ điều gì."} # Fallback nếu file không có
# Khởi tạo session_state.messages nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
# Nút "Bắt đầu cuộc trò chuyện mới"
if st.button(t['new_chat']):
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.rerun()
# CSS cải tiến (FIX: Cho phép toggle sidebar với <<<)
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
            content: "{t['typing']}" !important;
            animation: blink 1s infinite !important;
        }}
        /* SỬA: Loại bỏ background cho stChatInput ở phần CSS này để tránh override */
        [data-testid="stChatInput"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px !important;
            color: var(--text-color);
            box-shadow: none !important;
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
            margin: 10px 0px !important;
        }}
        div.stButton > button:hover {{
            background-color: #45a049 !important;
        }}
        /* FIX: Cho phép toggle sidebar - Không force mở nữa, hiển thị nút <<< */
        section[data-testid="stSidebar"] {{
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
            /* Không force transform nữa, để Streamlit xử lý collapse */
        }}
        /* Hiển thị nút toggle sidebar (<<<) để có thể thu gọn/mở rộng */
        [data-testid="collapsedControl"] {{
            display: block !important; /* Hiển thị nút collapse */
        }}
        /* Media query cho mobile: Sidebar có thể slide, nhưng mở mặc định */
        @media (max-width: 768px) {{
            section[data-testid="stSidebar"] {{
                width: 100% !important;
                min-width: unset !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                height: 100vh !important;
                z-index: 999 !important;
                /* Không force translateX(0), để có thể slide khi toggle */
                box-shadow: 2px 0 5px rgba(0,0,0,0.1) !important;
            }}
            .main {{
                margin-left: 0 !important;
                padding-left: 0 !important;
            }}
            /* Hiển thị toggle trên mobile */
            [data-testid="collapsedControl"] {{
                display: block !important;
            }}
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
if prompt := st.chat_input(t['chat_placeholder']):
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
        '<div class="typing">Assistant is typing..</div>',
        unsafe_allow_html=True
    )
    # Gọi API - Sử dụng model_name từ file text
    response = ""
    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""
    # Xóa dòng typing
    typing_placeholder.empty()
    # Hiển thị phản hồi
    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)
 
    st.session_state.messages.append({"role": "assistant", "content": response})