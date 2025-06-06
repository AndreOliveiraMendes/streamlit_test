import streamlit as st

def global_sidebar(title):
    with st.sidebar:
        st.title(title)
        username = st.session_state.username if "username" in st.session_state else None
        if username:
            st.markdown(f"usuario:{username}")