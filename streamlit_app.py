import streamlit as st
from openai import OpenAI
from base64 import b64encode

# [MỚI] Thiết lập cấu hình trang để sidebar hiển thị mặc định
st.set_page_config(page_title="AI Chatbot", layout="wide", initial_sidebar_state="expanded")

# --- 1. QUẢN LÝ TRẠNG THÁI (STATE) ---
# Khởi tạo ngôn ngữ mặc định nếu chưa có
if "language" not in st.session_state:
    st.session_state.language = "Vietnamese"

# Khởi tạo giao diện mặc định nếu chưa có
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Cài đặt / Settings")
    
    # Tùy chọn 1: Đổi ngôn ngữ
    st.subheader("🌐 Ngôn ngữ / Language")
    lang_choice = st.radio(
        "Chọn ngôn ngữ:",
        ["Vietnamese", "English"],
        index=0 if st.session_state.language == "Vietnamese" else 1
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

    st.divider()

    # Tùy chọn 2: Đổi giao diện (Dark/Light)
    st.subheader("🎨 Giao diện / Theme")
    theme_choice = st.toggle("Chế độ Tối / Dark Mode", value=(st.session_state.theme == "Dark"))
    
    new_theme = "Dark" if theme_choice else "Light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.info(f"Current Mode: {st.session_state.theme} | Lang: {st.session_state.language}")

# --- 3. ĐỊNH NGHĨA MÀU SẮC THEO THEME ---
# [MỚI] Biến màu sắc động
if st.session_state.theme == "Light":
    TEXT_COLOR = "#000000"
    BG_Overlay = "rgba(255, 255, 255, 0.85)" # Trắng mờ
    USER_BG = "#e6ffe6"
    ASSISTANT_BG = "#f0f7ff"
    INPUT_BG = "#fafafa"
else: # Dark Mode
    TEXT_COLOR = "#ffffff"
    BG_Overlay = "rgba(30, 30, 30, 0.85)"    # Đen mờ
    USER_BG = "#2b5c2b"                     # Xanh lá đậm
    ASSISTANT_BG = "#2c3e50"                # Xanh dương đậm
    INPUT_BG = "#404040"

# --- 4. CÁC HÀM CŨ (GIỮ NGUYÊN) ---
def rfile(name_file):
    # [MỚI] Logic chọn file theo ngôn ngữ (Ví dụ)
    # Nếu bạn có file system_en.txt và system_vn.txt
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except:
        return ""

def img_to_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            return b64encode(f.read()).decode()
    except:
        return ""

# Tải ảnh (dùng placeholder nếu không có file)
try:
    assistant_icon = img_to_base64("assistant_icon.png")
    user_icon = img_to_base64("user_icon.png")
    bg_image_base64 = img_to_base64("background.png")
except:
    assistant_icon = ""
    user_icon = ""
    bg_image_base64 = ""

# --- 5. CSS ĐỘNG (CẬP NHẬT THEO THEME) ---
# Lưu ý: Phần background-image vẫn giữ, chỉ thay đổi màu nền các khối
st.markdown(
    f"""
    <style>
        /* Ẩn Toolbar mặc định */
        [data-testid="stToolbar"], [data-testid="manage-app-button"] {{ display: none !important; }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        
        /* Background chính */
        .stAppViewContainer {{
            background-image: url('data:image/png;base64,{bg_image_base64}');
            background-size: cover;
            background-attachment: fixed;
        }}
        
        /* Container chính (Chat box) - Màu nền thay đổi theo Theme */
        .main .block-container {{
            background-color: {BG_Overlay} !important;
            border-radius: 15px !important;
            padding: 20px !important;
            backdrop-filter: blur(10px) !important;
            color: {TEXT_COLOR} !important;
        }}

        /* Bong bóng chat */
        .message {{
            padding: 12px !important;
            border-radius: 12px !important;
            max-width: 80% !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
            margin: 10px 0 !important;
            color: {TEXT_COLOR} !important; /* Màu chữ */
        }}
        
        .assistant {{ background-color: {ASSISTANT_BG} !important; }}
        .user {{ 
            background-color: {USER_BG} !important; 
            flex-direction: row-reverse !important;
            text-align: right;
            margin-left: auto !important;
        }}
        
        .icon {{ width: 35px; height: 35px; border-radius: 50%; }}
        
        /* Ô nhập liệu - Màu nền thay đổi */
        [data-testid="stChatInput"] {{ background: transparent !important; }}
        [data-testid="stChatInput"] textarea {{
            background-color: {INPUT_BG} !important;
            color: {TEXT_COLOR} !important;
            border: 1px solid #555 !important;
        }}
        
        /* Chỉnh màu chữ tiêu đề sidebar và text chung */
        h1, h2, h3, p, div {{ color: {TEXT_COLOR}; }}
        
        /* Sidebar styling (tùy chọn) */
        [data-testid="stSidebar"] {{
            background-color: {BG_Overlay} !important;
            backdrop-filter: blur(10px);
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 6. LOGIC HIỂN THỊ NỘI DUNG ---

# Thay đổi tiêu đề dựa trên ngôn ngữ
if st.session_state.language == "Vietnamese":
    st.markdown("<h1 style='text-align: center;'>Trợ lý ảo AI</h1>", unsafe_allow_html=True)
    input_placeholder = "Nhập câu hỏi của bạn..."
    typing_text = "Đang trả lời..."
    btn_new_chat = "Cuộc trò chuyện mới"
else:
    st.markdown("<h1 style='text-align: center;'>AI Assistant</h1>", unsafe_allow_html=True)
    input_placeholder = "Enter your question here..."
    typing_text = "Assistant is typing..."
    btn_new_chat = "New Chat"

# OpenAI Setup
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    st.error("Chưa có API Key" if st.session_state.language == "Vietnamese" else "Missing API Key")

# Lịch sử chat
if "messages" not in st.session_state:
    # Bạn có thể tạo file 01.system_en.txt và 01.system_vn.txt để load tùy ngôn ngữ
    sys_content = rfile("01.system_trainning.txt") 
    welcome_content = rfile("02.assistant.txt")
    
    st.session_state.messages = [
        {"role": "system", "content": sys_content},
        {"role": "assistant", "content": welcome_content}
    ]

# Nút New Chat
if st.button(btn_new_chat):
    st.session_state.messages = [st.session_state.messages[0], st.session_state.messages[1]]
    st.rerun()

# Hiển thị lịch sử
for message in st.session_state.messages:
    if message["role"] == "system": continue
    
    role_class = "assistant" if message["role"] == "assistant" else "user"
    icon_src = assistant_icon if message["role"] == "assistant" else user_icon
    
    st.markdown(f'''
    <div class="message {role_class}">
        <img src="data:image/png;base64,{icon_src}" class="icon" />
        <div class="text">{message["content"]}</div>
    </div>
    ''', unsafe_allow_html=True)

# Xử lý nhập liệu
if prompt := st.chat_input(input_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Hiển thị ngay câu hỏi user
    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Typing effect
    with st.spinner(typing_text):
        try:
            model_name = rfile("module_chatgpt.txt").strip()
            if not model_name: model_name = "gpt-3.5-turbo"
            
            stream = client.chat.completions.create(
                model=model_name,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            
            response = st.write_stream(stream) # Cách mới của Streamlit để hiển thị stream mượt hơn
            
            # Nếu muốn dùng kiểu custom cũ thì giữ logic cũ, 
            # nhưng st.write_stream không chèn được vào HTML custom div ngay lập tức.
            # Ở đây tôi lưu vào history để vòng lặp sau nó hiện đúng style.
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun() # Rerun để CSS áp dụng đúng cho tin nhắn mới
            
        except Exception as e:
            st.error(f"Error: {e}")