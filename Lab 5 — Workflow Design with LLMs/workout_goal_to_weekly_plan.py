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

class FitnessGoalDetails(BaseModel):
    goal_type: str = Field(description="Main fitness goal")
    fitness_level: str = Field(description="Beginner, intermediate, advanced, or not specified")
    days_available: int = Field(description="Number of days available per week")
    equipment_access: str = Field(description="Available equipment or none/not specified")

class WorkoutDay(BaseModel):
    day: str = Field(description="Day of the week or workout day number")
    workout: str = Field(description="Workout activities")
    duration: str = Field(description="Approximate workout duration")
    notes: str = Field(description="Rest, warm-up, or safety notes")

class WeeklyWorkoutPlan(BaseModel):
    plan: list[WorkoutDay] = Field(description="Day-by-day workout plan matching availability")

goal_parser = PydanticOutputParser(pydantic_object=FitnessGoalDetails)
goal_prompt = PromptTemplate(
    template="""Extract fitness goal details from the description. Do not assume equipment or fitness level if not stated.
Use the separate days_per_week input for days_available.

Fitness goal description:
{fitness_goal_text}

Days available per week: {days_per_week}

{format_instructions}
""",
    input_variables=["fitness_goal_text", "days_per_week"],
    partial_variables={"format_instructions": goal_parser.get_format_instructions()}
)
goal_chain = goal_prompt | llm | goal_parser

plan_parser = PydanticOutputParser(pydantic_object=WeeklyWorkoutPlan)
plan_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a careful personal trainer. Create a beginner-safe, practical weekly plan using only the extracted goal details. Include warm-ups and rest/recovery. Do not prescribe through pain or medical conditions; advise professional guidance when appropriate. The number of workout days must match days_available."),
    ("human", "Extracted fitness details:\n{goal_data}\n\n{format_instructions}")
]).partial(format_instructions=plan_parser.get_format_instructions())
plan_chain = plan_prompt | llm | plan_parser

fitness_goal_text = "I want to improve general fitness and lose some weight. I am a beginner and have a pair of light dumbbells at home."
days_per_week = 3

goal_details = goal_chain.invoke({
    "fitness_goal_text": fitness_goal_text,
    "days_per_week": str(days_per_week)
})
print("Step 1 - Extracted Goal Details:")
print(goal_details.model_dump_json(indent=2))

weekly_plan = plan_chain.invoke({"goal_data": goal_details.model_dump_json(indent=2)})
print("\nStep 2 - Weekly Workout Plan:")
print(weekly_plan.model_dump_json(indent=2))
