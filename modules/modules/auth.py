import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

def load_auth():
    with open('credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator, config

def render_login():
    authenticator, config = load_auth()

    name, authentication_status, username = authenticator.login(
        location='main')

    if authentication_status == False:
        st.error("Incorrect username or password. Please try again.")
        return None, None, None, None

    if authentication_status == None:
        st.markdown("""
        <div style="text-align:center; margin-top: 2rem;">
            <h2 style="color:#1a3c5e;">Welcome to VyaparScore</h2>
            <p style="color:#5a7a9a;">Automated Financial Reporting for Banks</p>
            <p style="color:#8a9bb0; font-size:0.85rem;">
                Please enter your bank credentials to continue</p>
        </div>
        """, unsafe_allow_html=True)
        return None, None, None, None

    return authenticator, name, authentication_status, username