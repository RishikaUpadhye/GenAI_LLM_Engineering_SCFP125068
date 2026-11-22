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

class ComplaintData(BaseModel):
    complaint: str = Field(description="The customer's main complaint")
    product_or_feature: str = Field(description="Product or feature mentioned")
    sentiment: str = Field(description="Customer sentiment: Positive, Negative, or Neutral")

parser = PydanticOutputParser(pydantic_object=ComplaintData)

extract_prompt = PromptTemplate(
    template="""Extract the complaint, product or feature, and sentiment from this customer review.
Use only information in the review.

Review: {review_text}

{format_instructions}
""",
    input_variables=["review_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

extract_chain = extract_prompt | llm | parser

ticket_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support ticket writer. Write a concise internal support ticket summary using only the structured complaint data provided. Do not add facts."),
    ("human", "Complaint data:\n{complaint_data}\n\nWrite the support ticket summary.")
])

ticket_chain = ticket_prompt | llm | StrOutputParser()

review_text = "The headphones stopped working after two days. The sound feature keeps cutting out and I am very disappointed."

complaint_data = extract_chain.invoke({"review_text": review_text})
print("Step 1 - Structured Complaint Data:")
print(complaint_data.model_dump_json(indent=2))

ticket_summary = ticket_chain.invoke({"complaint_data": complaint_data.model_dump_json()})
print("\nStep 2 - Support Ticket Summary:")
print(ticket_summary)
