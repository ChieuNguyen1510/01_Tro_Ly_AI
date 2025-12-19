import streamlit as st
from openai import OpenAI
from base64 import b64encode
# Ẩn thanh công cụ và nút "Manage app"aaaaâ
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
# Chuyển ảnh sang base64
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")
# CSS cho background với base64 (cải tiến để cover thêm phần trên, loại bỏ margin/padding top)
try:
    bg_image_base64 = img_to_base64("background.png")
    st.markdown(
        f"""
        <style>
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
            }}
            [data-testid="stChatInput"] > div > div {{
                background: rgba(255, 255, 255, 0.9) !important;
                border-radius: 10px !important;
                backdrop-filter: blur(5px) !important;
            }}
            
            /* Nội dung chính */
            .main .block-container {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                border-radius: 10px !important;
                padding: 10px !important;
                backdrop-filter: blur(5px) !important;
                margin: 10px !important;
                max-height: 80vh !important;
                overflow-y: auto !important;
                margin-top: 0 !important; /* Đảm bảo không margin top thêm */
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
# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{title_content}</h1>""",
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
if st.button("New chat"):
    # Reset messages về trạng thái ban đầu
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    # Làm mới giao diện bằng cách rerun ứng dụng
    st.rerun()
# CSS cải tiến
st.markdown(
    """
    <style>
        .message {
            padding: 12px !important;
            border-radius: 12px !important;
            max-width: 75% !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
            margin: 8px 0 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        .assistant {
            background-color: #f0f7ff !important;
        }
        .user {
            background-color: #e6ffe6 !important;
            text-align: right !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }
        .icon {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            border: 1px solid #ddd !important;
        }
        .text {
            flex: 1 !important;
            font-size: 16px !important;
            line-height: 1.4 !important;
        }
        .typing {
            font-style: italic !important;
            color: #888 !important;
            padding: 5px 10px !important;
            display: flex !important;
            align-items: center !important;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .typing::after {
            content: "..." !important;
            animation: blink 1s infinite !important;
        }
        [data-testid="stChatInput"] {
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            padding: 8px !important;
            background-color: #fafafa !important;
        }
        /* Tùy chỉnh nút "New chat" */
        div.stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 2px solid #FFFFFF !important;
            padding: 6px 6px !important;
            font-size: 14px !important;
            border: none !important;
            display: block !important;
            margin: 10px 0px !important; /* Căn giữa nút */
        }
        div.stButton > button:hover {
            background-color: #45a049 !important;
        }
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
if prompt := st.chat_input("Enter your question here..."):
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
    # Gọi API
    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""
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