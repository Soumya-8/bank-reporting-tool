import streamlit as st

def render_login():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.bank_name = None
        st.session_state.username = None

    # Load users from Streamlit secrets (online) 
    # or local fallback (on your laptop)
    try:
        users = {
            key: {
                'password': st.secrets['users'][key]['password'],
                'name': st.secrets['users'][key]['name']
            }
            for key in st.secrets['users']
        }
    except Exception:
        users = {
            'vyaparscore_demo': {
                'password': 'demo123',
                'name': 'Demo Bank'
            },
            'coop_bank_bilaspur': {
                'password': 'bilaspur123',
                'name': 'Cooperative Bank Bilaspur'
            }
        }

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("""
            <div style="background:white; padding:2.5rem;
                        border-radius:16px; border:1px solid #c0cfe0;
                        box-shadow:0 4px 20px rgba(0,0,0,0.08);
                        margin-top:4rem;">
                <div style="text-align:center; margin-bottom:2rem;">
                    <h1 style="color:#1a3c5e; font-size:1.8rem; margin:0;">
                        🏦 VyaparScore</h1>
                    <p style="color:#5a7a9a; margin:0.5rem 0 0 0;
                              font-size:0.9rem;">
                        Automated Financial Reporting for Banks</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            username = st.text_input(
                "Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password",
                placeholder="Enter your password")

            if st.button("Login", use_container_width=True):
                if username in users and \
                   users[username]['password'] == password:
                    st.session_state.authenticated = True
                    st.session_state.bank_name = users[username]['name']
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        return False

    return True


def render_logout():
    with st.sidebar:
        st.markdown(f"### 🏦 {st.session_state.bank_name}")
        st.markdown(f"*{st.session_state.username}*")
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.bank_name = None
            st.session_state.username = None
            st.rerun()