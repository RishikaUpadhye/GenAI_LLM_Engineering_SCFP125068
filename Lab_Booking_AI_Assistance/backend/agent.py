import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from backend.database import (
    get_tests,
    get_available_slots,
    get_bookings,
    get_booking_for_user,
    book_test as save_test_booking,
    cancel_test_booking,
)

load_dotenv()


class UserContext(TypedDict):
    user_id: str


def redact_email(message):
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return re.sub(email_pattern, "[REDACTED]", message)


def create_lab_agent(checkpointer=None):
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not groq_key:
        raise ValueError("Please add GROQ_API_KEY to your .env file.")

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=groq_key
    )

    @tool
    def list_tests():
        """List laboratory tests, categories, descriptions and prices from the database."""
        return str(get_tests())

    @tool
    def check_slots(test_id: str):
        """Check available appointment slots for a test ID using the database."""
        return str(get_available_slots(test_id))

    @tool
    def my_bookings(runtime: ToolRuntime[UserContext]):
        """Show bookings belonging only to the currently logged-in patient."""
        patient_id = runtime.context["user_id"]
        return str(get_bookings(patient_id))

    @tool
    def book_test(test_id: str, slot_id: str, runtime: ToolRuntime[UserContext]):
        """Book a test after showing the patient the booking details and obtaining approval."""
        patient_id = runtime.context["user_id"]

        tests = {test["test_id"]: test for test in get_tests()}
        test = tests.get(test_id)
        if test is None:
            return "Booking failed: test ID does not exist."

        slots = get_available_slots(test_id)
        slot = next((item for item in slots if item["slot_id"] == slot_id), None)
        if slot is None:
            return "Booking failed: that slot is not available for this test."

        existing = [
            item for item in get_bookings(patient_id)
            if item["test_id"] == test_id and item["status"] == "Confirmed"
        ]
        if existing:
            return "Booking failed: you already have a confirmed booking for this test."

        approval = interrupt({
            "action": "book_test",
            "title": "Confirm laboratory test booking",
            "test_name": test["test_name"],
            "test_id": test_id,
            "price": test["price"],
            "slot_id": slot_id,
            "slot_date": slot["slot_date"],
            "slot_time": slot["slot_time"],
            "message": "Do you approve this booking?"
        })

        if not approval or approval.get("approved") is not True:
            return "The patient rejected the booking. No database changes were made."

        success, receipt = save_test_booking(patient_id, test_id, slot_id)
        if success:
            return f"Booking confirmed. Receipt from database: {receipt}"
        return f"Booking was not completed: {receipt}"

    @tool
    def cancel_booking(booking_id: str, runtime: ToolRuntime[UserContext]):
        """Cancel one of the currently logged-in patient's bookings after approval."""
        patient_id = runtime.context["user_id"]
        booking = get_booking_for_user(patient_id, booking_id)

        if booking is None:
            return "Cancellation failed: booking not found in your account."

        if booking["status"] != "Confirmed":
            return "Cancellation failed: this booking is not currently confirmed."

        approval = interrupt({
            "action": "cancel_booking",
            "title": "Confirm booking cancellation",
            "booking_id": booking["booking_id"],
            "test_name": booking["test_name"],
            "slot_date": booking["slot_date"],
            "slot_time": booking["slot_time"],
            "message": "Do you approve cancelling this booking?"
        })

        if not approval or approval.get("approved") is not True:
            return "The patient rejected the cancellation. No database changes were made."

        success, message = cancel_test_booking(patient_id, booking_id)
        return message if success else f"Cancellation was not completed: {message}"

    tools = [list_tests, check_slots, my_bookings, book_test, cancel_booking]

    if tavily_key:
        tools.append(TavilySearch(max_results=5))

    return create_agent(
        model=model,
        tools=tools,
        context_schema=UserContext,
        checkpointer=checkpointer or InMemorySaver(),
        system_prompt="""
You are a Lab Test Booking AI Assistant. Politely answer only questions related
to laboratory tests and booking appointments. For unrelated questions, say:
"I am a Lab Test Booking AI Assistant. I can help with laboratory tests,
available slots, bookings and general information about tests."

Rules:
- Use database tools for test names, prices, slots and patient bookings.
- Never guess prices or availability.
- Use web search only for general information such as what a test measures
  or whether fasting is commonly required.
- Never diagnose a patient or recommend a test based on symptoms.
- When a patient wants to book, identify the test, call check_slots, show the
  available slot choices, and ask which slot they want. Once they select a
  slot, call book_test. The tool will pause and ask the patient to approve.
  Do not claim success until the tool returns a successful receipt.
- When a patient wants to cancel, call my_bookings if needed to identify the
  booking. Confirm the exact booking ID, then call cancel_booking. The tool
  will pause and ask the patient to approve. Do not claim cancellation until
  the tool confirms it.
- The logged-in patient identity comes from runtime context. Never ask the
  patient for a user ID and never pass a user ID as a tool argument.
- Keep answers clear, polite and concise.
- Don't Answer Anything else than out work, Just tell them politely that you are Test booking AI Agent
"""
    )


def ask_agent(agent, message, user_id, thread_id):
    safe_message = redact_email(message)
    return agent.invoke(
        {"messages": [{"role": "user", "content": safe_message}]},
        config={"configurable": {"thread_id": thread_id}},
        context={"user_id": user_id}
    )


def resume_agent(agent, approved, user_id, thread_id):
    from langgraph.types import Command

    return agent.invoke(
        Command(resume={"approved": approved}),
        config={"configurable": {"thread_id": thread_id}},
        context={"user_id": user_id}
    )
