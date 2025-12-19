import streamlit as st
from openai import OpenAI
from base64 import b64encode

# ==================================================
# PAGE CONFIG (BẮT BUỘC – PHẢI Ở ĐẦU FILE)
# ==================================================
st.set_page_config(
    page_title="AI Chatbot",
    layout="wide"
)

# ==================================================
# HIDE TOOLBAR (AN TOÀN)
# ==================================================
st.markdown(
    """
    <style>
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# UTILS
# ==================================================
def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as f:
        return f.read()

def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()

# ==================================================
# LOAD IMAGES
# ==================================================
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")
bg_image_base64 = img_to_base64("background.png")

# ==================================================
# FULL SCREEN BACKGROUND (FIX TRIỆT ĐỂ)
# ==================================================
st.markdown(
    f"""
    <style>

    /* RESET */
    html, body {{
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
    }}

    #root {{
        width: 100%;
        height: 100%;
    }}

    /* ROOT APP */
    .stApp {{
        width: 100vw;
        height: 100vh;
        margin: 0;
        padding: 0;

        background-image: url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* REMOVE STREAMLIT PADDING */
    section.main {{
        padding: 0 !important;
    }}

    .block-container {{
        padding: 20px !important;
        margin: 0 !important;
        max-width: 100% !important;
        background-color: rgba(255,255,255,0.88);
        backdrop-filter: blur(6px);
        min-height: 100vh;
    }}

    /* CHAT UI */
    .message {{
        padding: 12px;
        border-radius: 12px;
        max-width: 75%;
        display: flex;
        gap: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 16px;
    }}

    .assistant {{
        background-color: #f0f7ff;
    }}

    .user {{
        background-color: #e6ffe6;
        margin-left: auto;
        flex-direction: row-reverse;
        text-align: right;
    }}

    .icon {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 1px solid #ddd;
    }}

    .typing {{
        font-style: italic;
        color: #777;
        margin: 6px 0;
    }}

    [data-testid="stChatInput"] {{
        border-radius: 8px;
        background-color: #fafafa;
    }}

    div.stButton > button {{
        background-color: #4CAF50;
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
        border: none;
        margin: 10px 0;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# LOGO
# ==================================================
try:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# ==================================================
# TITLE
# ==================================================
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""
    <h2 style="text-align:center;border-bottom:2px solid #ddd;padding-bottom:10px;">
        {title_content}
    </h2>
    """,
    unsafe_allow_html=True
)

# ==================================================
# OPENAI
# ==================================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_MSG = {"role": "system", "content": rfile("01.system_trainning.txt")}
ASSISTANT_INIT = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_MSG, ASSISTANT_INIT]

# ==================================================
# NEW CHAT
# ==================================================
if st.button("New chat"):
    st.session_state.messages = [SYSTEM_MSG, ASSISTANT_INIT]
    st.rerun()

# ==================================================
# SHOW CHAT HISTORY
# ==================================================
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(
            f"""
            <div class="message assistant">
                <img src="data:image/png;base64,{assistant_icon}" class="icon">
                <div>{msg["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif msg["role"] == "user":
        st.markdown(
            f"""
            <div class="message user">
                <img src="data:image/png;base64,{user_icon}" class="icon">
                <div>{msg["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# CHAT INPUT + STREAM
# ==================================================
if prompt := st.chat_input("Enter your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown(
        f"""
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon">
            <div>{prompt}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    typing = st.empty()
    typing.markdown('<div class="typing">Assistant is typing...</div>', unsafe_allow_html=True)

    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=st.session_state.messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content

    typing.empty()

    st.markdown(
        f"""
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon">
            <div>{response}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.messages.append({"role": "assistant", "content": response})
