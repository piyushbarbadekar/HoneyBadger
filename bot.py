import time
import os
import joblib
import streamlit as st
import openai
import PyPDF2
import io

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Honey Badger AI",
    page_icon="🦡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* ── Root variables ── */
:root {
    --red:          #E8152A;
    --red-light:    #FF3347;
    --red-dark:     #A50D1D;
    --red-glow:     rgba(232,21,42,0.35);
    --white:        #FFFFFF;
    --glass:        rgba(255,255,255,0.06);
    --glass-border: rgba(255,255,255,0.12);
    --glass-hover:  rgba(255,255,255,0.10);
    --bg-dark:      #080808;
    --text-dim:     rgba(255,255,255,0.45);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-dark);
    color: var(--white);
}

/* ── Animated mesh background ── */
.stApp {
    background:
        radial-gradient(ellipse 90% 55% at 5% 0%,   rgba(232,21,42,0.20) 0%, transparent 58%),
        radial-gradient(ellipse 60% 45% at 95% 100%, rgba(232,21,42,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 50% 35% at 50% 50%,  rgba(232,21,42,0.05) 0%, transparent 65%),
        radial-gradient(ellipse 30% 25% at 80% 20%,  rgba(180,10,25,0.08) 0%, transparent 50%),
        #080808;
    background-attachment: fixed;
    animation: bgPulse 8s ease-in-out infinite alternate;
}

@keyframes bgPulse {
    0%   { filter: brightness(1);    }
    100% { filter: brightness(1.05); }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6,6,6,0.88) !important;
    border-right: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(28px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(28px) saturate(1.4) !important;
    transform: none !important;
    min-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.8rem; }

/* ── Sidebar brand ── */
.sidebar-brand {
    text-align: center;
    padding: 0 1rem 1.4rem;
    border-bottom: 1px solid var(--glass-border);
    margin-bottom: 1.4rem;
}
.sidebar-brand .logo {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.3rem;
    animation: logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse {
    0%, 100% { filter: drop-shadow(0 0 10px rgba(232,21,42,0.5)); transform: scale(1);    }
    50%       { filter: drop-shadow(0 0 22px rgba(232,21,42,0.9)); transform: scale(1.06); }
}
.sidebar-brand h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.55rem !important;
    letter-spacing: 4px !important;
    background: linear-gradient(135deg, #fff 30%, var(--red-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important; padding: 0 !important;
}
.sidebar-brand p {
    color: var(--text-dim);
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0.35rem 0 0;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.62rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--red-light);
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: block;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--white) !important;
    backdrop-filter: blur(10px);
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--red) !important;
    box-shadow: 0 0 12px rgba(232,21,42,0.2);
}

/* ── Floating upload box ── */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, rgba(232,21,42,0.06), rgba(255,255,255,0.03)) !important;
    border: 1.5px dashed rgba(232,21,42,0.45) !important;
    border-radius: 14px !important;
    padding: 0.6rem !important;
    transition: all 0.3s ease;
    animation: floatBox 4s ease-in-out infinite;
}
@keyframes floatBox {
    0%, 100% { transform: translateY(0px);  box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 16px rgba(232,21,42,0.05); }
    50%       { transform: translateY(-5px); box-shadow: 0 9px 30px rgba(0,0,0,0.4), 0 0 26px rgba(232,21,42,0.13); }
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--red) !important;
    background: rgba(232,21,42,0.10) !important;
    box-shadow: 0 8px 32px rgba(232,21,42,0.22), 0 0 0 3px rgba(232,21,42,0.08) !important;
    animation: none;
    transform: translateY(-2px);
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: rgba(232,21,42,0.08) !important;
    border: 1px solid rgba(232,21,42,0.28) !important;
    border-radius: 10px !important;
    color: var(--white) !important;
}

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 2rem 0 1.2rem;
}
.main-header h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 4rem !important;
    letter-spacing: 8px !important;
    background: linear-gradient(270deg, #ffffff, #ffcccc, var(--red-light), #ffffff);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    line-height: 1 !important;
    animation: shimmer 5s linear infinite;
}
@keyframes shimmer {
    0%   { background-position: 0%   center; }
    100% { background-position: 300% center; }
}
.main-header .underline {
    display: block;
    width: 70px;
    height: 3px;
    background: linear-gradient(90deg, var(--red), var(--red-light), var(--red));
    background-size: 200% auto;
    margin: 0.9rem auto 0;
    border-radius: 2px;
    box-shadow: 0 0 16px rgba(232,21,42,0.7);
    animation: shimmer 2s linear infinite;
}
.main-header p {
    color: var(--text-dim);
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.6rem;
    font-style: italic;
}

/* ── PDF banner ── */
.pdf-banner {
    background: linear-gradient(135deg, rgba(232,21,42,0.10), rgba(232,21,42,0.04));
    border: 1px solid rgba(232,21,42,0.22);
    border-radius: 12px;
    padding: 0.65rem 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.83rem;
    color: rgba(255,255,255,0.75);
    margin-bottom: 1rem;
    backdrop-filter: blur(12px);
}
.gradient-text {
    background: linear-gradient(135deg, #fff 20%, var(--red-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

/* ── Glass chat messages ── */
[data-testid="stChatMessageContainer"],
[data-testid="stChatMessage"] {
    max-width: 750px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
[data-testid="stChatMessage"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(16px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    margin-bottom: 0.75rem !important;
    padding: 0.3rem 0.6rem !important;
    transition: border-color 0.25s, background 0.25s, transform 0.2s;
    animation: msgFadeIn 0.35s ease-out both;
}
@keyframes msgFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(232,21,42,0.28) !important;
    background: var(--glass-hover) !important;
    transform: translateY(-1px);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-left: 3px solid var(--red) !important;
    background: rgba(232,21,42,0.05) !important;
}

/* ── Typing dots ── */
.typing-dots {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.5rem 0.3rem;
}
.typing-dots span {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--red-light);
    display: inline-block;
    animation: dotBounce 1.3s infinite ease-in-out;
    box-shadow: 0 0 8px var(--red-glow);
}
.typing-dots span:nth-child(1) { animation-delay: 0s;    }
.typing-dots span:nth-child(2) { animation-delay: 0.22s; }
.typing-dots span:nth-child(3) { animation-delay: 0.44s; }
@keyframes dotBounce {
    0%, 80%, 100% { transform: scale(0.65); opacity: 0.35; }
    40%            { transform: scale(1.25); opacity: 1;    }
}

/* ── Animated response text ── */
[data-testid="stChatMessage"] p {
    animation: textReveal 0.25s ease-out both;
}
@keyframes textReveal {
    from { opacity: 0; transform: translateX(-5px); }
    to   { opacity: 1; transform: translateX(0);    }
}

/* ── Chat input ── */
[data-testid="stBottom"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}
[data-testid="stBottom"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-top: none !important;
    max-width: 700px !important;
    margin: 0 auto !important;
}
[data-testid="stChatInput"] > div {
    border-radius: 14px !important;
    overflow: hidden !important;
    background: rgba(255,255,255,0.055) !important;
    border: 1px solid var(--glass-border) !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div {
    border-radius: 14px !important;
    overflow: hidden !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.055) !important;
    border: 0px solid var(--glass-border) !important;
    border-radius: 14px !important;
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.25s, box-shadow 0.25s;
    margin-left: 0 !important;
    padding-left: 1rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(232,21,42,0.12), 0 0 20px rgba(232,21,42,0.08) !important;
    outline: none !important;
}

/* ── Send button ── */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--red-light), var(--red-dark)) !important;
    border: none !important;
    border-radius: 12px !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
    box-shadow: 0 2px 14px rgba(232,21,42,0.32) !important;
}
[data-testid="stChatInput"] button:hover {
    transform: scale(1.07) !important;
    box-shadow: 0 4px 26px rgba(232,21,42,0.58) !important;
}

/* ── Stop button ── */
.stop-bar {
    display: flex;
    justify-content: center;
    margin-bottom: 0.5rem;
}
.stop-bar button {
    background: rgba(232,21,42,0.15) !important;
    border: 1px solid rgba(232,21,42,0.4) !important;
    border-radius: 10px !important;
    color: var(--white) !important;
    padding: 0.3rem 1.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    cursor: pointer !important;
    transition: background 0.2s, box-shadow 0.2s !important;
}
.stop-bar button:hover {
    background: rgba(232,21,42,0.3) !important;
    box-shadow: 0 0 14px rgba(232,21,42,0.4) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(232,21,42,0.35); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--red); }

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid var(--glass-border) !important; margin: 1.1rem 0 !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }

</style>
""", unsafe_allow_html=True)

# ── Constants ───────────────────────────────────────────────────────────────────
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]  # paste your key here
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '🦡'

client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

new_chat_id = f'{time.time()}'

try:
    os.mkdir('data/')
except:
    pass

try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="logo">🦡</span>
        <h1>HONEY BADGER</h1>
        <p>Powered by Nemotron 3 Super</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="section-label">💬 Conversations</span>', unsafe_allow_html=True)
    if st.session_state.get('chat_id') is None:
        st.session_state.chat_id = st.selectbox(
            label='',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, '＋ New Chat'),
            placeholder='_',
            label_visibility='collapsed',
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label='',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x, '＋ New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
            label_visibility='collapsed',
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<span class="section-label">📄 Document</span>', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader('', type='pdf', label_visibility='collapsed')
    if uploaded_pdf is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_pdf.read()))
        pdf_text = ''
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + '\n'
        st.session_state.pdf_text = pdf_text
        st.success(f'✓ {uploaded_pdf.name} — {len(pdf_reader.pages)} pages')
    else:
        if 'pdf_text' not in st.session_state:
            st.session_state.pdf_text = ''

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.18);font-size:0.62rem;text-align:center;letter-spacing:1.5px;">HONEY BADGER AI © 2025</p>', unsafe_allow_html=True)

# ── Chat title init ──────────────────────────────────────────────────────────────
if 'chat_title' not in st.session_state:
    st.session_state.chat_title = 'New Chat'

# ── Stop state init ──────────────────────────────────────────────────────────────
if 'stop_stream' not in st.session_state:
    st.session_state.stop_stream = False

# ── Main header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>HONEY BADGER AI</h1>
    <span class="underline"></span>
    <p>Fearless Intelligence &nbsp;·&nbsp; Powered by NVIDIA Nemotron 3 Super</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.get('pdf_text'):
    st.markdown("""
    <div class="pdf-banner">
        📄 <span class="gradient-text">Document loaded</span> &nbsp;— Ask me anything about it
    </div>
    """, unsafe_allow_html=True)

# ── Load chat history ────────────────────────────────────────────────────────────
try:
    st.session_state.messages = joblib.load(f'data/{st.session_state.chat_id}-st_messages')
    st.session_state.chat_history = joblib.load(f'data/{st.session_state.chat_id}-nemotron_messages')
except:
    st.session_state.messages = []
    st.session_state.chat_history = []

# ── Display past messages ────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(name=message['role'], avatar=message.get('avatar')):
        st.markdown(message['content'])

# ── Chat input ───────────────────────────────────────────────────────────────────
if prompt := st.chat_input('Ask Honey Badger anything...'):

    st.session_state.stop_stream = False

    # Use first 40 chars of prompt as chat title
    if st.session_state.chat_title == 'New Chat':
        st.session_state.chat_title = prompt[:40].strip()

    past_chats[st.session_state.chat_id] = st.session_state.chat_title
    joblib.dump(past_chats, 'data/past_chats_list')

    with st.chat_message('user', avatar='💭'):
        st.markdown(prompt)

    st.session_state.messages.append({'role': 'user', 'content': prompt})

    if st.session_state.get('pdf_text'):
        messages_to_send = [
            {'role': 'system', 'content': f'You are Honey Badger AI, a fearless and highly intelligent assistant. Use the following PDF content to answer questions:\n\n{st.session_state.pdf_text[:12000]}'}
        ] + st.session_state.chat_history + [{'role': 'user', 'content': prompt}]
    else:
        messages_to_send = [
            {'role': 'system', 'content': 'You are Honey Badger AI, a fearless and highly intelligent assistant. Be sharp, concise, and helpful.'}
        ] + st.session_state.chat_history + [{'role': 'user', 'content': prompt}]

    st.session_state.chat_history.append({'role': 'user', 'content': prompt})

    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        message_placeholder = st.empty()

        # Stop button right above the chat input
        stop_placeholder = st.empty()
        stop_clicked = stop_placeholder.button('⏹ Stop responding', key='stop_button')
        if stop_clicked:
            st.session_state.stop_stream = True

        # Show typing dots while API responds
        message_placeholder.markdown("""
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
        """, unsafe_allow_html=True)

        # Call API and stream
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b",
            messages=messages_to_send,
            temperature=1.0,
            top_p=0.95,
            max_tokens=1024,
            stream=True
        )

        full_response = ''
        stopped = False
        for chunk in response:
            if st.session_state.stop_stream:
                stopped = True
                break
            if chunk.choices and chunk.choices[0].delta.content is not None:
                chunk_text = chunk.choices[0].delta.content
                for letter in chunk_text:
                    full_response += letter
                    message_placeholder.markdown(full_response + ' ▍')
                    time.sleep(0.02)

        # Hide stop button after done
        stop_placeholder.empty()

        if stopped:
            message_placeholder.markdown(full_response + '\n\n*⏹ Response stopped.*')
        else:
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({
        'role': MODEL_ROLE,
        'content': full_response,
        'avatar': AI_AVATAR_ICON,
    })
    st.session_state.chat_history.append({'role': 'assistant', 'content': full_response})

    joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.chat_history, f'data/{st.session_state.chat_id}-nemotron_messages')