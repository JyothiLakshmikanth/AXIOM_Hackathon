"""
AXIOM Authentication UI Component for Streamlit.
Provides login and signup pages with user management.
"""

import streamlit as st
from agents.tools.auth_tools import (
    firestore_authenticate_user,
    firestore_create_user,
    firestore_create_session,
    firestore_log_audit_entry,
    firestore_get_user
)


def render_login_page():
    """Render login/signup page."""
    st.set_page_config(
        page_title="AXIOM | Login",
        page_icon="⬡",
        layout="centered"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 40px 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #3b82f6;'>⬡ AXIOM</h2>", unsafe_allow_html=True)
        st.title("🔐 Authentication")
        st.caption("Evidence-Driven Multi-Agent System")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        # ────────────────────────────────────────────────────────────────────────
        # LOGIN TAB
        # ────────────────────────────────────────────────────────────────────────
        with tab_login:
            st.subheader("Welcome Back")

            email = st.text_input(
                "Email",
                placeholder="demo@axiom.ai",
                key="login_email"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="login_password"
            )

            st.caption("Demo: email=demo@axiom.ai, password=demo123")

            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("Login", key="login_btn", use_container_width=True)
            with col_b:
                demo_btn = st.button("Demo Login", key="demo_btn", use_container_width=True)

            if demo_btn:
                # Demo login
                user_id = firestore_authenticate_user("demo@axiom.ai", "demo123")
                if user_id:
                    ip_address = st.session_state.get("client_ip", "0.0.0.0")
                    user_agent = st.session_state.get("user_agent", "streamlit")
                    session_id = firestore_create_session(user_id, ip_address, user_agent)

                    firestore_log_audit_entry(
                        user_id,
                        session_id,
                        "login",
                        {"method": "demo", "email": "demo@axiom.ai"}
                    )

                    st.session_state.user_id = user_id
                    st.session_state.session_id = session_id
                    st.session_state.authenticated = True

                    st.success("✅ Demo login successful!")
                    st.balloons()
                    st.rerun()

            if login_btn:
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    # Authenticate
                    user_id = firestore_authenticate_user(email, password)
                    if user_id:
                        ip_address = st.session_state.get("client_ip", "0.0.0.0")
                        user_agent = st.session_state.get("user_agent", "streamlit")
                        session_id = firestore_create_session(user_id, ip_address, user_agent)

                        firestore_log_audit_entry(
                            user_id,
                            session_id,
                            "login",
                            {"email": email}
                        )

                        st.session_state.user_id = user_id
                        st.session_state.session_id = session_id
                        st.session_state.authenticated = True

                        st.success(f"✅ Welcome back, {email}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")

        # ────────────────────────────────────────────────────────────────────────
        # SIGNUP TAB
        # ────────────────────────────────────────────────────────────────────────
        with tab_signup:
            st.subheader("Create Account")

            signup_email = st.text_input(
                "Email",
                placeholder="user@company.com",
                key="signup_email"
            )
            signup_name = st.text_input(
                "Full Name",
                placeholder="John Doe",
                key="signup_name"
            )
            signup_password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="signup_password"
            )
            signup_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="••••••••",
                key="signup_password_confirm"
            )

            role = st.selectbox(
                "Role (optional)",
                ["user", "engineer", "pm", "admin"],
                key="signup_role"
            )

            signup_btn = st.button("Sign Up", key="signup_btn", use_container_width=True)

            if signup_btn:
                if not signup_email or not signup_name or not signup_password:
                    st.error("❌ Please fill in all required fields")
                elif signup_password != signup_password_confirm:
                    st.error("❌ Passwords do not match")
                elif len(signup_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    # Create user
                    user_id = firestore_create_user(
                        signup_email,
                        signup_name,
                        signup_password,
                        role=role
                    )

                    if user_id:
                        # Auto-login
                        ip_address = st.session_state.get("client_ip", "0.0.0.0")
                        user_agent = st.session_state.get("user_agent", "streamlit")
                        session_id = firestore_create_session(user_id, ip_address, user_agent)

                        firestore_log_audit_entry(
                            user_id,
                            session_id,
                            "account_created",
                            {"email": signup_email, "role": role}
                        )

                        st.session_state.user_id = user_id
                        st.session_state.session_id = session_id
                        st.session_state.authenticated = True

                        st.success(f"✅ Account created successfully! Welcome, {signup_name}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error creating account. Please try again.")

    # ────────────────────────────────────────────────────────────────────────────
    # Footer
    # ────────────────────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "**AXIOM** — Evidence-Driven Multi-Agent Intelligence Platform | "
        "Powered by LangGraph + Gemini"
    )


def render_user_menu(user_id: str):
    """Render user profile menu in sidebar."""
    user = firestore_get_user(user_id)

    with st.sidebar:
        st.divider()
        st.subheader("👤 Profile")

        if user:
            st.write(f"**{user.get('full_name', 'User')}**")
            st.caption(f"📧 {user.get('email', 'unknown@axiom.ai')}")
            st.caption(f"🎯 Role: `{user.get('role', 'user')}`")

            # Preferences
            with st.expander("⚙️ Preferences"):
                prefs = user.get("preferences", {})
                st.write(f"Response Style: {prefs.get('response_style', 'visual_first')}")
                st.write(f"Visual Model: {prefs.get('preferred_visual_model', 'imagen-2')}")
                st.write(f"Notify Blockers: {prefs.get('notify_on_blocker', True)}")

            # Logout
            if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                firestore_log_audit_entry(user_id, st.session_state.get("session_id", ""), "logout", {})
                st.session_state.clear()
                st.success("✅ Logged out successfully")
                st.rerun()
