from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0
)

class InterviewAnswer(BaseModel):
    question: str = Field(description="Interview question")
    answer: str = Field(description="Candidate's answer; use 'Not stated' if missing")

class ExtractedAnswers(BaseModel):
    answers: list[InterviewAnswer] = Field(description="Interview questions and candidate answers")

class SkillEvaluation(BaseModel):
    skill: str = Field(description="Skill being assessed")
    demonstrated: bool = Field(description="True only when clear evidence is present")
    evidence_or_gap: str = Field(description="Evidence from answers or what evidence is missing")

class SkillEvaluations(BaseModel):
    evaluations: list[SkillEvaluation] = Field(description="Evaluation for every requested skill")

class ScorecardRow(BaseModel):
    skill: str
    demonstrated: bool
    evidence_or_gap: str

class HiringScorecard(BaseModel):
    scorecard_rows: list[ScorecardRow] = Field(description="One row per skill assessed")
    overall_recommendation: str = Field(description="Evidence-based recommendation, such as Proceed, Hold, or Do Not Proceed")

answers_parser = PydanticOutputParser(pydantic_object=ExtractedAnswers)
answers_prompt = PromptTemplate(
    template="""Extract each interview question and the candidate's answer from the transcript.
Do not invent answers. If an answer is missing, write 'Not stated'.

Transcript:
{transcript_text}

{format_instructions}
""",
    input_variables=["transcript_text"],
    partial_variables={"format_instructions": answers_parser.get_format_instructions()}
)
answers_chain = answers_prompt | llm | answers_parser

evaluation_parser = PydanticOutputParser(pydantic_object=SkillEvaluations)
evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a technical interviewer evaluating skill evidence. Assess only the answers provided. Mark a skill demonstrated only if clear evidence supports it. Do not infer skills from unsupported claims."),
    ("human", "Skills to assess: {skills_to_assess}\n\nExtracted answers:\n{answers_data}\n\n{format_instructions}")
]).partial(format_instructions=evaluation_parser.get_format_instructions())
evaluation_chain = evaluation_prompt | llm | evaluation_parser

scorecard_parser = PydanticOutputParser(pydantic_object=HiringScorecard)
scorecard_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a hiring panel coordinator. Create a fair, evidence-based scorecard. Do not invent evidence. The recommendation must reflect the supplied evaluation and gaps."),
    ("human", "Skill evaluations:\n{evaluation_data}\n\n{format_instructions}")
]).partial(format_instructions=scorecard_parser.get_format_instructions())
scorecard_chain = scorecard_prompt | llm | scorecard_parser

transcript_text = """Interviewer: Tell me about a Python project you built.
Candidate: I built a small data cleaning tool using Python and pandas.
Interviewer: How do you optimize SQL queries?
Candidate: I have not worked much with query optimization yet."""

skills_to_assess = ["Python programming", "SQL query optimization", "Communication"]

answers = answers_chain.invoke({"transcript_text": transcript_text})
print("Step 1 - Extracted Answers:")
print(answers.model_dump_json(indent=2))

evaluations = evaluation_chain.invoke({
    "skills_to_assess": ", ".join(skills_to_assess),
    "answers_data": answers.model_dump_json(indent=2)
})
print("\nStep 2 - Skill Evaluation:")
print(evaluations.model_dump_json(indent=2))

scorecard = scorecard_chain.invoke({"evaluation_data": evaluations.model_dump_json(indent=2)})
print("\nStep 3 - Hiring Scorecard:")
print(scorecard.model_dump_json(indent=2))
