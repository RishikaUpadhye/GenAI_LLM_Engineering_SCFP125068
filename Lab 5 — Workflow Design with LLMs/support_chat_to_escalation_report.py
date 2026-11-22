from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0
)

class ChatSummary(BaseModel):
    issue: str = Field(description="Main customer issue")
    customer_tone: str = Field(description="Customer's tone")
    resolution_attempted: str = Field(description="Troubleshooting or resolution already attempted")

class EscalationReadiness(BaseModel):
    missing_fields: list[str] = Field(description="Important missing information such as account ID or error code")
    is_ready_to_escalate: bool = Field(description="True only if enough information is available to escalate")

summary_parser = PydanticOutputParser(pydantic_object=ChatSummary)
summary_prompt = PromptTemplate(
    template="""Normalize this support chat into the main issue, customer tone, and resolution attempted.
Do not invent details. Use 'Not provided' when information is absent.

Chat log:
{chat_log_text}

{format_instructions}
""",
    input_variables=["chat_log_text"],
    partial_variables={"format_instructions": summary_parser.get_format_instructions()}
)
summary_chain = summary_prompt | llm | summary_parser

readiness_parser = PydanticOutputParser(pydantic_object=EscalationReadiness)
readiness_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an escalation-readiness reviewer. Identify important missing information that a support lead would need, such as account ID, error code, affected service, or troubleshooting results. Do not invent values."),
    ("human", "Structured chat summary:\n{summary_data}\n\n{format_instructions}")
]).partial(format_instructions=readiness_parser.get_format_instructions())
readiness_chain = readiness_prompt | llm | readiness_parser

report_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support operations lead. Write a prioritized escalation report based only on the summary and gap review. State missing information clearly and do not invent details."),
    ("human", "Chat summary:\n{summary_data}\n\nEscalation readiness:\n{readiness_data}\n\nCreate the escalation report with priority, issue, attempted resolution, missing information, and next action.")
])
report_chain = report_prompt | llm | StrOutputParser()

chat_log_text = """Customer: My account keeps showing error E104 when I try to sign in. This is very frustrating.
Agent: Please restart the app and try again.
Customer: I restarted it, but the same error appears."""

summary = summary_chain.invoke({"chat_log_text": chat_log_text})
print("Step 1 - Structured Summary:")
print(summary.model_dump_json(indent=2))

readiness = readiness_chain.invoke({"summary_data": summary.model_dump_json(indent=2)})
print("\nStep 2 - Escalation Gap Check:")
print(readiness.model_dump_json(indent=2))

report = report_chain.invoke({
    "summary_data": summary.model_dump_json(indent=2),
    "readiness_data": readiness.model_dump_json(indent=2)
})
print("\nStep 3 - Escalation Report:")
print(report)
