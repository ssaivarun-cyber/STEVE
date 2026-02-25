import streamlit as st
import datetime as dt
import wikipedia as wiki
import webbrowser
import hashlib
import urllib.parse

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Steve – Voice Assistant",
    page_icon="🤖",
    layout="centered",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body { background-color: #0e1117; }
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%); }

    /* ══════ AUTH STYLES ══════ */
    .auth-logo-text {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b2fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.18em;
        display: block;
        text-align: center;
    }
    .auth-subtitle {
        color: #8892a4;
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
    }
    .auth-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #2d3748, transparent);
        margin: 1rem 0 1.4rem 0;
    }
    .auth-sys-label {
        text-align: center;
        font-size: 0.6rem;
        letter-spacing: 0.22em;
        color: #00d4ff;
        text-transform: uppercase;
        opacity: 0.65;
        margin-bottom: 1.3rem;
    }
    .status-online {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.45rem;
        font-size: 0.7rem;
        letter-spacing: 0.1em;
        color: #10b981;
        text-transform: uppercase;
        margin-bottom: 1.3rem;
    }
    .dot-pulse {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #10b981;
        display: inline-block;
        animation: dotpulse 2s infinite;
    }
    @keyframes dotpulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:0.35; transform:scale(0.65); }
    }
    .msg-error {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.35);
        color: #f87171;
        border-radius: 9px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        text-align: center;
        margin-top: 0.6rem;
    }
    .msg-success {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.35);
        color: #34d399;
        border-radius: 9px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        text-align: center;
        margin-top: 0.6rem;
    }

    /* ══════ MAIN APP STYLES ══════ */
    .steve-header { text-align: center; padding: 1.5rem 0 1rem 0; }
    .steve-header h1 {
        font-size: 3.2rem; font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b2fff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .steve-header p { color: #8892a4; font-size: 1rem; margin-top: 0.3rem; }
    .welcome-badge {
        background: linear-gradient(135deg, #1e2a3a, #162032);
        border: 1px solid #2d3748; border-radius: 10px;
        padding: 0.45rem 0.9rem; color: #00d4ff;
        font-size: 0.78rem; letter-spacing: 0.06em;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #7b2fff, #5a23c8); color: white;
        padding: 0.75rem 1.2rem; border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0 0.5rem 3rem; font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(123,47,255,0.3);
    }
    .chat-bubble-steve {
        background: linear-gradient(135deg, #1e2a3a, #162032); color: #e2e8f0;
        padding: 0.75rem 1.2rem; border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 3rem 0.5rem 0; font-size: 0.95rem;
        border: 1px solid #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    .chat-bubble-steve .label { color: #00d4ff; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .chat-bubble-user .label  { color: #c4b5fd; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .capability-card {
        background: #1a1f2e; border: 1px solid #2d3748;
        border-radius: 12px; padding: 1rem; text-align: center;
        color: #8892a4; font-size: 0.85rem;
    }
    .capability-card .icon  { font-size: 1.5rem; margin-bottom: 0.3rem; }
    .capability-card .title { color: #e2e8f0; font-weight: 600; margin-bottom: 0.2rem; }
    div.stButton > button {
        width: 100%; border-radius: 12px; font-weight: 600;
        padding: 0.6rem 1rem; border: none; transition: all 0.2s;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00d4ff, #7b2fff); color: white;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(123,47,255,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  USER DATABASE
# ══════════════════════════════════════════════════════════════════════
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# Default accounts (seeded once)
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "admin": _hash("admin123"),
        "steve": _hash("steve@123"),
        "user1": _hash("pass1234"),
    }

# ─── Session State ───────────────────────────────────────────────────────────────
for k, v in {
    "logged_in":  False,
    "username":   "",
    "auth_page":  "login",    # "login"  or  "signup"
    "auth_msg":   ("", ""),   # (text, "error"|"success")
    "history":    [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

VA_NAME = "steve"

# ─── Utilities ───────────────────────────────────────────────────────────────────
def set_msg(text, kind="error"):
    st.session_state.auth_msg = (text, kind)

def clear_msg():
    st.session_state.auth_msg = ("", "")

# ─── Replacement helpers for pywhatkit (browser-based, cloud-safe) ──────────────
def playonyt(query: str) -> str:
    """Returns a YouTube search URL (opens via st.link_button)."""
    encoded = urllib.parse.quote(query)
    return f"https://www.youtube.com/results?search_query={encoded}"

def google_search_url(query: str) -> str:
    """Returns a Google search URL."""
    encoded = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded}"

# ─── Command Processor ──────────────────────────────────────────────────────────
def process_command(command: str):
    """Returns (response_text, optional_url_tuple) where url_tuple = (label, url) or None."""
    cmd = command.lower().strip()
    if VA_NAME in cmd:
        cmd = cmd.replace(VA_NAME, "").strip()
    if not cmd:
        return "I didn't catch that. Please try again.", None

    if "close" in cmd or "exit" in cmd or "goodbye" in cmd or "bye" in cmd:
        return "👋 See you again! Call me whenever you need me.", None
    elif "time" in cmd:
        return f"🕐 The current time is **{dt.datetime.now().strftime('%I:%M %p')}**.", None
    elif "date" in cmd:
        return f"📅 Today is **{dt.datetime.now().strftime('%A, %B %d, %Y')}**.", None
    elif "play" in cmd:
        query = cmd.replace("play", "").strip()
        if not query:
            return "⚠️ Please tell me what to play. E.g. *play telugu songs*", None
        url = playonyt(query)
        return f"▶️ Click below to play **{query}** on YouTube!", ("▶️ Open YouTube", url)
    elif "search for" in cmd or "google" in cmd or "search" in cmd:
        query = cmd.replace("search for","").replace("google","").replace("search","").strip()
        if not query:
            return "⚠️ What would you like me to search for?", None
        url = google_search_url(query)
        return f"🔍 Click below to search Google for **{query}**!", ("🔍 Open Google", url)
    elif "who is" in cmd or "what is" in cmd or "tell me about" in cmd:
        query = cmd.replace("who is","").replace("what is","").replace("tell me about","").strip()
        if not query:
            return "⚠️ Please specify what you'd like to know about.", None
        try:
            summary = wiki.summary(query, sentences=3)
            return f"📖 **{query.title()}**\n\n{summary}", None
        except wiki.exceptions.DisambiguationError as e:
            return f"🔀 That's ambiguous! Did you mean: {', '.join(e.options[:5])}?", None
        except wiki.exceptions.PageError:
            return f"❌ Couldn't find Wikipedia info on **{query}**.", None
        except Exception as e:
            return f"❌ Error: {e}", None
    elif "joke" in cmd:
        import random
        return random.choice([
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "I told my computer I needed a break. Now it won't stop sending me Kit Kat ads. 🍫",
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        ]), None
    elif "hello" in cmd or "hi" in cmd or "hey" in cmd:
        return "👋 Hello Boss! I'm Steve, ready to assist. Ask me about time, play music, search the web, or look something up!", None
    elif "help" in cmd or "what can you do" in cmd:
        return (
            "🤖 **Steve's Capabilities:**\n\n"
            "- 🕐 *steve what time is it* – Current time\n"
            "- 📅 *steve what's today's date* – Today's date\n"
            "- ▶️ *steve play [song/artist]* – Play on YouTube\n"
            "- 🔍 *steve search for [query]* – Google search\n"
            "- 📖 *steve who is [person]* – Wikipedia info\n"
            "- 😄 *steve tell me a joke* – Random joke\n"
            "- 👋 *steve close* – Say goodbye"
        ), None
    else:
        return f"🤔 I'm not sure how to handle *\"{command}\"*. Try saying **help** to see what I can do!", None


# ══════════════════════════════════════════════════════════════════════
#  ░░  SIGN IN PAGE  ░░
# ══════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <span class="auth-logo-text">🤖 STEVE</span>
    <div class="auth-subtitle">Personal AI Voice Assistant</div>
    <div class="auth-divider"></div>
    <div class="status-online"><span class="dot-pulse"></span> System Online — Awaiting Authentication</div>
    <div class="auth-sys-label">[ SECURE SIGN IN ]</div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 Sign In")

    with st.form("login_form", clear_on_submit=False):
        uid = st.text_input("👤  User ID",  placeholder="Enter your User ID",  key="li_uid")
        pw  = st.text_input("🔒  Password", placeholder="Enter your Password", type="password", key="li_pw")
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn, _ = st.columns([2, 3])
        with col_btn:
            submitted = st.form_submit_button("⚡  SIGN IN", use_container_width=True)

    if submitted:
        uid, pw = uid.strip(), pw.strip()
        if not uid or not pw:
            set_msg("⚠️ Please enter both User ID and Password.", "error")
        elif uid in st.session_state.user_db and st.session_state.user_db[uid] == _hash(pw):
            st.session_state.logged_in = True
            st.session_state.username  = uid
            clear_msg()
            st.rerun()
        else:
            set_msg("❌ Incorrect User ID or Password. Please try again.", "error")

    msg_text, msg_type = st.session_state.auth_msg
    if msg_text:
        st.markdown(f'<div class="msg-{msg_type}">{msg_text}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#8892a4;font-size:0.82rem;'>"
        "Don't have an account?</div>", unsafe_allow_html=True
    )
    if st.button("📝  Go to Sign Up", key="goto_signup", use_container_width=False):
        st.session_state.auth_page = "signup"
        clear_msg()
        st.rerun()

    st.markdown("""
    <div style="text-align:center;color:#4a5568;font-size:0.72rem;margin-top:1.5rem;letter-spacing:0.05em;">
        Steve Voice Assistant &nbsp;•&nbsp; Built with Streamlit
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  ░░  SIGN UP PAGE  ░░
# ══════════════════════════════════════════════════════════════════════
def show_signup():
    st.markdown("""
    <span class="auth-logo-text">🤖 STEVE</span>
    <div class="auth-subtitle">Personal AI Voice Assistant</div>
    <div class="auth-divider"></div>
    <div class="status-online"><span class="dot-pulse"></span> System Online — New User Registration</div>
    <div class="auth-sys-label">[ CREATE ACCOUNT ]</div>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 Create a New Account")

    with st.form("signup_form", clear_on_submit=True):
        new_uid  = st.text_input("👤  Choose User ID",   placeholder="Pick a unique User ID (min 3 chars)",  key="su_uid")
        new_pw   = st.text_input("🔒  Create Password",  placeholder="At least 6 characters",                type="password", key="su_pw")
        new_pw2  = st.text_input("🔒  Confirm Password", placeholder="Repeat your password",                  type="password", key="su_pw2")
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn, _ = st.columns([2, 3])
        with col_btn:
            submitted = st.form_submit_button("🚀  CREATE ACCOUNT", use_container_width=True)

    if submitted:
        uid = new_uid.strip()
        pw  = new_pw.strip()
        pw2 = new_pw2.strip()
        if not uid or not pw or not pw2:
            set_msg("⚠️ All fields are required.", "error")
        elif len(uid) < 3:
            set_msg("⚠️ User ID must be at least 3 characters.", "error")
        elif len(pw) < 6:
            set_msg("⚠️ Password must be at least 6 characters.", "error")
        elif pw != pw2:
            set_msg("❌ Passwords do not match. Please try again.", "error")
        elif uid in st.session_state.user_db:
            set_msg(f"❌ User ID '{uid}' is already taken. Choose another.", "error")
        else:
            st.session_state.user_db[uid] = _hash(pw)
            set_msg(f"✅ Account created for '{uid}'! Please sign in.", "success")
            st.session_state.auth_page = "login"
            st.rerun()

    msg_text, msg_type = st.session_state.auth_msg
    if msg_text:
        st.markdown(f'<div class="msg-{msg_type}">{msg_text}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#8892a4;font-size:0.82rem;'>"
        "Already have an account?</div>", unsafe_allow_html=True
    )
    if st.button("🔑  Go to Sign In", key="goto_login", use_container_width=False):
        st.session_state.auth_page = "login"
        clear_msg()
        st.rerun()

    st.markdown("""
    <div style="text-align:center;color:#4a5568;font-size:0.72rem;margin-top:1.5rem;letter-spacing:0.05em;">
        Steve Voice Assistant &nbsp;•&nbsp; Built with Streamlit
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  ░░  MAIN APP  ░░
# ══════════════════════════════════════════════════════════════════════
def show_app():
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(
            f'<div class="welcome-badge">👤 Welcome, <strong>{st.session_state.username.upper()}</strong></div>',
            unsafe_allow_html=True
        )
    with top_r:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.history   = []
            st.session_state.auth_page = "login"
            clear_msg()
            st.rerun()

    st.markdown("""
    <div class="steve-header">
        <h1>🤖 STEVE</h1>
        <p>Your Personal AI Voice Assistant</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="capability-card"><div class="icon">🕐</div><div class="title">Time & Date</div>Ask anytime</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="capability-card"><div class="icon">▶️</div><div class="title">YouTube</div>Play anything</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="capability-card"><div class="icon">🔍</div><div class="title">Web Search</div>Google it</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="capability-card"><div class="icon">📖</div><div class="title">Wikipedia</div>Who/What is</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("⚙️ Settings", expanded=False):
        if st.button("🗑️ Clear Chat History"):
            st.session_state.history = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        if not st.session_state.history:
            st.markdown("""
            <div class="chat-bubble-steve">
                <div class="label">🤖 STEVE</div>
                Hello! I'm Steve, your personal assistant. Type a command below.<br><br>
                Try: <em>"what time is it"</em>, <em>"play relaxing music"</em>, <em>"who is Elon Musk"</em>,
                or say <strong>"help"</strong> for all commands.
            </div>""", unsafe_allow_html=True)
        else:
            for entry in st.session_state.history:
                st.markdown(f'<div class="chat-bubble-user"><div class="label">👤 YOU</div>{entry["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-bubble-steve"><div class="label">🤖 STEVE</div>{entry["steve"]}</div>', unsafe_allow_html=True)
                if entry.get("link"):
                    label, url = entry["link"]
                    st.link_button(label, url)

    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.text_input("Command", placeholder="Type a command (e.g. 'play lo-fi music')...",
                               label_visibility="collapsed", key="text_input")

    send_col, _ = st.columns([1, 4])
    with send_col:
        send_clicked = st.button("Send ➤", key="send_btn")

    if send_clicked and user_input.strip():
        response, link = process_command(user_input.strip())
        st.session_state.history.append({"user": user_input.strip(), "steve": response, "link": link})
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#4a5568;font-size:0.78rem;">
        Steve Voice Assistant • Built with Streamlit •
        Say <strong style="color:#7b2fff">help</strong> for all commands
    </div>""", unsafe_allow_html=True)


# ─── ROUTER ──────────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    show_app()
elif st.session_state.auth_page == "signup":
    show_signup()
else:
    show_login()
