import streamlit as st
import yaml
from yaml.loader import SafeLoader
import bcrypt
import datetime


def load_users():
    # On local laptop — read from credentials.yaml
    try:
        with open('credentials.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config['credentials']['usernames']
    except Exception:
        pass

    # On Streamlit Cloud — read from secrets
    try:
        users = {}
        for key in st.secrets['users']:
            users[key] = {
                'password': st.secrets['users'][key]['password'],
                'name': st.secrets['users'][key]['name']
            }
        return users
    except Exception:
        return {}


def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.encode())
    except Exception:
        return False


def init_session():
    defaults = {
        'authenticated': False,
        'bank_name': None,
        'username': None,
        'login_time': None,
        'audit_log': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_session_timeout():
    if st.session_state.authenticated:
        login_time = st.session_state.login_time
        if login_time:
            elapsed = (datetime.datetime.now() -
                       login_time).total_seconds()
            # Auto logout after 30 minutes
            if elapsed > 1800:
                log_action("SESSION", "Auto logout due to timeout")
                st.session_state.authenticated = False
                st.session_state.bank_name = None
                st.session_state.username = None
                st.session_state.login_time = None
                st.warning(
                    "Session expired after 30 minutes. "
                    "Please login again.")
                st.rerun()


def log_action(action, detail=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = st.session_state.get('username', 'unknown')
    entry = f"[{timestamp}] USER:{username} ACTION:{action} {detail}"
    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = []
    st.session_state.audit_log.append(entry)


def render_login():
    init_session()
    check_session_timeout()

    if not st.session_state.authenticated:
        # Center the login card
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("""
            <div style="background:white; padding:2.5rem;
                        border-radius:16px; border:1px solid #c0cfe0;
                        box-shadow:0 4px 20px rgba(0,0,0,0.08);
                        margin-top:4rem;">
                <div style="text-align:center; margin-bottom:2rem;">
                    <h1 style="color:#1a3c5e; font-size:1.8rem;
                               margin:0;">🏦 VyaparScore</h1>
                    <p style="color:#5a7a9a; margin:0.5rem 0 0 0;
                              font-size:0.9rem;">
                        Automated Financial Reporting for Banks</p>
                    <p style="color:#8a9bb0; margin:0.3rem 0 0 0;
                              font-size:0.75rem;">
                        🔒 Secure | Encrypted | RBI Compliant</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            username = st.text_input(
                "Username",
                placeholder="Enter your bank username")
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password")

            if st.button("Login", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    users = load_users()
                    if username in users:
                        stored_hash = users[username]['password']
                        if verify_password(password, stored_hash):
                            st.session_state.authenticated = True
                            st.session_state.bank_name = \
                                users[username]['name']
                            st.session_state.username = username
                            st.session_state.login_time = \
                                datetime.datetime.now()
                            log_action("LOGIN", "Successful login")
                            st.rerun()
                        else:
                            log_action(
                                "LOGIN_FAILED",
                                f"Failed attempt for {username}")
                            st.error(
                                "Incorrect password. Please try again.")
                    else:
                        log_action(
                            "LOGIN_FAILED",
                            f"Unknown username: {username}")
                        st.error(
                            "Username not found. Please try again.")

            st.markdown("""
            <div style="text-align:center; margin-top:1rem;
                        font-size:0.75rem; color:#8a9bb0;">
                Having trouble? Contact support@vyaparscore.com
            </div>
            """, unsafe_allow_html=True)

        return False

    return True


def render_logout():
    with st.sidebar:
        st.markdown(f"### 🏦 {st.session_state.bank_name}")
        st.markdown(f"*{st.session_state.username}*")

        if st.session_state.login_time:
            elapsed = int(
                (datetime.datetime.now() -
                 st.session_state.login_time).total_seconds() / 60)
            remaining = max(0, 30 - elapsed)
            st.caption(f"⏱ Session expires in {remaining} min")

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            log_action("LOGOUT", "User logged out")
            st.session_state.authenticated = False
            st.session_state.bank_name = None
            st.session_state.username = None
            st.session_state.login_time = None
            st.rerun()

        # Show audit log to admin
        if st.session_state.username == 'vyaparscore_demo':
            with st.expander("🔍 Audit Log"):
                for entry in reversed(
                        st.session_state.audit_log[-20:]):
                    st.caption(entry)