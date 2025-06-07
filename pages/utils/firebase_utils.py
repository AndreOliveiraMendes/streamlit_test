import streamlit as st
import firebase_admin
import pyrebase

def start_pyrebase():
    pyrebase_config = dict(st.secrets.firebase_config)
    return pyrebase.initialize_app(pyrebase_config)


def start_firebaseadmin():
    if not firebase_admin._apps:
        admin_cred = dict(st.secrets.firebase_admin)
        cred = firebase_admin.credentials.Certificate(admin_cred)
        return firebase_admin.initialize_app(cred)
    else:
        return firebase_admin.get_app()