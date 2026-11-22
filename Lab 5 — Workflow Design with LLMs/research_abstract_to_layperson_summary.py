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

class ResearchData(BaseModel):
    research_question: str = Field(description="The question the research investigates")
    method: str = Field(description="The method used in the research")
    key_finding: str = Field(description="The main finding reported in the abstract")

parser = PydanticOutputParser(pydantic_object=ResearchData)

extract_prompt = PromptTemplate(
    template="""Extract the research question, method, and key finding from this abstract.
Do not add details that are not present.

Abstract:
{abstract_text}

{format_instructions}
""",
    input_variables=["abstract_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

extract_chain = extract_prompt | llm | parser

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a science communicator explaining research to a general audience. Use simple language and only the supplied structured information."),
    ("human", "Research information:\n{research_data}\n\nExplain the research in a short, clear paragraph for a non-expert.")
])

summary_chain = summary_prompt | llm | StrOutputParser()

abstract_text = """This study examined whether a daily walking program improved sleep quality in adults.
Researchers followed 120 adults for eight weeks and compared sleep questionnaire scores before and after the program.
Participants reported improved sleep quality after eight weeks."""

research_data = extract_chain.invoke({"abstract_text": abstract_text})
print("Step 1 - Structured Research Data:")
print(research_data.model_dump_json(indent=2))

summary = summary_chain.invoke({"research_data": research_data.model_dump_json()})
print("\nStep 2 - Layperson Summary:")
print(summary)
