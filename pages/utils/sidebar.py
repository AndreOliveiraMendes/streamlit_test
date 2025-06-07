import streamlit as st

def global_sidebar(title):
    with st.sidebar:
        st.title(title)
        user = st.session_state.user
        if user:
            st.markdown(f"usuario:{user.display_name}")