from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a customer support assistant.
Generate a polite, professional, and helpful reply to the customer's message.
Maintain the same tone for every response.
Keep the reply within the specified maximum word limit.
Do not exceed the word limit.
Do not make promises that are not supported by the customer's message.
"""

USER_PROMPT = """Company Name: {company_name}
Customer Message: {customer_message}
Maximum Words: {max_words}
Generate a customer support reply."""

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

customer_message = "I received a damaged product. Please help me with a replacement."
user_query = USER_PROMPT.format(
    company_name="ABC Electronics",
    customer_message=customer_message,
    max_words=50
)
response = ask_llm_system(SYSTEM_PROMPT, user_query)
print(response)