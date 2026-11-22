from groq import Groq
import os
from dotenv import load_dotenv
import json

load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a resume field extractor.
Extract only the fields requested by the user from the given resume text.
Return the output in strict JSON format.
Include only the requested fields in the JSON.
If a requested field is not available in the resume, return an empty string for that field.
Do not include explanations, markdown, or any text outside the JSON object.
"""

USER_PROMPT = """Resume Text:{resume_text}
Fields to Extract:{fields_to_extract}"""

def ask_llm_system(system_prompt, user_query, max_token=1000, temperature=0):
    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    chat_completion = client.chat.completions.create(
        messages=message,
        model="openai/gpt-oss-20b",
        temperature=temperature,
        max_tokens=max_token
    )

    return chat_completion.choices[0].message.content


resume_text = """
Name: Rishika
Email: rishika@example.com
Phone: 9876543210
Education: Master of Computer Applications
Skills: Python, SQL, Machine Learning
Experience: 1 year as a Data Analyst
"""

fields_to_extract = ["name", "email", "education", "skills"]

user_query = USER_PROMPT.format(
    resume_text=resume_text,
    fields_to_extract=fields_to_extract
)

response = ask_llm_system(SYSTEM_PROMPT, user_query)

print(json.dumps(json.loads(response), indent=4))