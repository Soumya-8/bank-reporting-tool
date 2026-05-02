import streamlit as st
from modules.auth import render_login, render_logout
from modules.ui import run_app

st.set_page_config(
    page_title="VyaparScore",
    page_icon="🏦",
    layout="wide"
)

if render_login():
    render_logout()
    run_app()