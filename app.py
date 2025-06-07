import firebase_admin.auth
import streamlit as st
import firebase_admin
import pyrebase
from pages.utils.sidebar import global_sidebar
from pages.utils.firebase_utils import start_pyrebase, start_firebaseadmin

if not "user" in st.session_state:
    st.session_state.user = None

fb = start_pyrebase()
fba = start_firebaseadmin()

def login(email, password):
    try:
        auth = fb.auth()
        res = auth.sign_in_with_email_and_password(email, password)
    except Exception as e:
        st.error(f"login failed cause:{e.args}")
        return None
    return res

global_sidebar("app-misc")

st.title("Small App Pages For Misc Topics")

st.markdown("use the sidebar to check all possible applications, or login bellow for extra features, if you don't have an account, you can create")

choice = st.selectbox("action", ["login/logout", "sign_in", "list users"])
if choice == "login/logout":
    if st.session_state.user is None:
        st.subheader("log in")
        email = st.text_input("email")
        password = st.text_input("senha", type="password")
        if st.button("login") and (res := login(email, password)):
            user = firebase_admin.auth.get_user_by_email(email)
            firebase_admin.auth.update_user(user.uid, display_name='John Doe')
            st.session_state.user = user
            st.rerun()
            
    else:
        st.subheader("log out")
        if st.button("unlog"):
            st.session_state.user = None
            st.rerun()
elif choice == "sign_in":
    st.subheader("sign in")
    username = st.text_input("usuario")
    email = st.text_input("email")
    password = st.text_input("senha", type="password")
    
    if st.button("sign in"):
        campos = {
            "usuario": username,
            "email": email,
            "senha": password
        }
        faltando = [nome for nome, valor in campos.items() if not valor]

        if faltando:
            for campo in faltando:
                st.error(f"preencha o campo {campo}")
                st.toast(f"preencha o campo {campo}")
        else:
            # lógica de criar usuário
            pass
elif choice == "list users":
    page = firebase_admin.auth.list_users()
    while page:
        for user in page.users:
            st.write(f'User id:{user.uid} user name:{user.display_name}')
        # Get next batch of users.
        page = page.get_next_page()