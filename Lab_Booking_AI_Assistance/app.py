import streamlit as st
import pandas as pd

from backend.database import (
    setup_database,
    create_user,
    authenticate_user,
    get_user_name,
    get_tests,
    get_available_slots,
    get_bookings,
) 
from backend.agent import create_lab_agent, ask_agent, resume_agent

st.set_page_config(
    page_title="Lab Test Booking Assistant",
    page_icon="🧪",
    layout="wide"
)

setup_database()


def show_login():
    st.title("🧪 Lab Test Booking Assistant")
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        st.subheader("Patient Login")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            login_clicked = st.form_submit_button("Login", type="primary")

        if login_clicked:
            patient = authenticate_user(email, password)
            if patient:
                st.session_state.authenticated = True
                st.session_state.user_id = patient["user_id"]
                st.session_state.patient_name = patient["name"]
                st.session_state.chat_history = []
                st.session_state.pending_approval = None
                st.session_state.agent = None
                st.session_state.agent_user_id = None
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with signup_tab:
        st.subheader("Create Patient Account")
        with st.form("signup_form"):
            name = st.text_input("Full name", key="signup_name")
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input(
                "Confirm password", type="password", key="signup_confirm_password"
            )
            signup_clicked = st.form_submit_button("Create Account", type="primary")

        if signup_clicked:
            if not name.strip() or not email.strip() or not password:
                st.error("Please complete all fields.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            elif len(password) < 8:
                st.error("Password must contain at least 8 characters.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, patient_id, message = create_user(name, email, password)
                if success:
                    st.success("Account created. You can now log in.")
                else:
                    st.error(message)


def get_agent_for_user(user_id):
    if (
        st.session_state.get("agent") is None
        or st.session_state.get("agent_user_id") != user_id
    ):
        st.session_state.agent = create_lab_agent()
        st.session_state.agent_user_id = user_id
    return st.session_state.agent


def get_interrupt_payload(result):
    interrupts = result.get("__interrupt__", ())
    if not interrupts:
        return None
    item = interrupts[0]
    return item.value if hasattr(item, "value") else item


def save_agent_result(result):
    payload = get_interrupt_payload(result)
    if payload:
        st.session_state.pending_approval = payload
        return

    st.session_state.pending_approval = None
    messages = result.get("messages", [])
    if messages:
        answer = messages[-1].content
        if isinstance(answer, list):
            answer = str(answer)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": str(answer)
        })


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login()
    st.stop()

user_id = st.session_state.user_id
patient_name = st.session_state.patient_name

st.sidebar.title("🧪 Lab Booking")
st.sidebar.write(f"Welcome, **{patient_name}**")
st.sidebar.caption(f"Patient ID: {user_id}")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Test Catalogue", "My Bookings", "AI Assistant"]
)

if st.sidebar.button("Logout"):
    for key in [
        "authenticated", "user_id", "patient_name", "agent",
        "agent_user_id", "chat_history", "pending_approval"
    ]:
        st.session_state.pop(key, None)
    st.rerun()

st.title("🧪 Lab Test Booking Assistant")

if page == "Dashboard":
    tests = get_tests()
    bookings = get_bookings(user_id)
    available_count = sum(
        len(get_available_slots(test["test_id"])) for test in tests
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Laboratory Tests", len(tests))
    col2.metric("Available Slots", available_count)
    col3.metric("Your Bookings", len(bookings))

    st.subheader(f"Welcome, {patient_name}!")
    st.write(
        "Use the AI Assistant to ask about laboratory tests, check available "
        "slots, book appointments and cancel your bookings."
    )
    st.info("Bookings and cancellations can be completed directly in the AI conversation after your approval.")

elif page == "Test Catalogue":
    st.subheader("Laboratory Test Catalogue")
    df = pd.DataFrame(get_tests()).rename(columns={
        "test_id": "Test ID",
        "test_name": "Test Name",
        "category": "Category",
        "description": "Description",
        "price": "Price (₹)"
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "My Bookings":
    st.subheader("My Bookings")
    bookings = get_bookings(user_id)
    if bookings:
        df = pd.DataFrame(bookings).rename(columns={
            "booking_id": "Booking ID",
            "test_name": "Test",
            "slot_date": "Date",
            "slot_time": "Time",
            "status": "Status",
            "price": "Price (₹)",
            "test_id": "Test ID",
            "slot_id": "Slot ID"
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("To cancel a booking, ask the AI Assistant. It will request your approval.")
    else:
        st.info("You do not have any bookings yet. Ask the AI Assistant to book a test.")

elif page == "AI Assistant":
    st.subheader("Chat with your Lab Test Booking AI")
    st.caption(
        "You can ask about tests, prices and slots, and book or cancel appointments "
        "directly in this conversation."
    )

    try:
        agent = get_agent_for_user(user_id)
    except Exception as error:
        st.error(f"Could not start the AI assistant: {error}")
        st.stop()

    for item in st.session_state.get("chat_history", []):
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    pending = st.session_state.get("pending_approval")

    if pending:
        st.warning("The AI is waiting for your approval. No database change has been made yet.")
        st.markdown(f"### {pending.get('title', 'Approval required')}")
        if pending.get("action") == "book_test":
            st.write(f"**Test:** {pending.get('test_name')} ({pending.get('test_id')})")
            st.write(f"**Price:** ₹{pending.get('price')}")
            st.write(f"**Date:** {pending.get('slot_date')}")
            st.write(f"**Time:** {pending.get('slot_time')}")
            st.write(f"**Slot ID:** {pending.get('slot_id')}")
        elif pending.get("action") == "cancel_booking":
            st.write(f"**Booking ID:** {pending.get('booking_id')}")
            st.write(f"**Test:** {pending.get('test_name')}")
            st.write(f"**Date:** {pending.get('slot_date')}")
            st.write(f"**Time:** {pending.get('slot_time')}")

        st.write(pending.get("message", "Do you approve this action?"))
        approve_col, reject_col = st.columns(2)

        if approve_col.button("Approve", type="primary", use_container_width=True):
            try:
                result = resume_agent(
                    agent, True, user_id, f"patient-{user_id}"
                )
                save_agent_result(result)
                st.rerun()
            except Exception as error:
                st.error(f"Could not complete the approved action: {error}")

        if reject_col.button("Reject", use_container_width=True):
            try:
                result = resume_agent(
                    agent, False, user_id, f"patient-{user_id}"
                )
                save_agent_result(result)
                st.rerun()
            except Exception as error:
                st.error(f"Could not process the rejection: {error}")

    prompt = st.chat_input(
        "Ask about tests, slots, bookings or cancellations...",
        disabled=bool(pending)
    )

    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = ask_agent(
                        agent,
                        prompt,
                        user_id,
                        f"patient-{user_id}"
                    )
                    payload = get_interrupt_payload(result)
                    if payload:
                        st.session_state.pending_approval = payload
                        st.rerun()
                    else:
                        messages = result.get("messages", [])
                        answer = messages[-1].content if messages else "I could not generate a response."
                        if isinstance(answer, list):
                            answer = str(answer)
                        st.markdown(answer)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": str(answer)
                        })
                except Exception as error:
                    st.error(f"Assistant error: {error}")
