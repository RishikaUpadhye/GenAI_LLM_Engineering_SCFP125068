from groq import Groq
import os  
from dotenv import load_dotenv
load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a helpful AI assistant. You will work as doctor summary generator. Collect raw data i.e patient_notes and patient_name. then provide the summary with fixed sections - Symptoms, Diagnosis, Treatment, and Recommendations. In the same format every time, regardless of input. And if Input is not related to medical thing then respond with 'I am sorry, I can only provide medical summaries.'"""

USER_PROMPT = "{patient_name} has the following medical notes: {patient_notes}."

def ask_llm_system(system_prompt, user_query, max_token=1000, temperature=0):
    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    chat_completion = client.chat.completions.create(messages=message, model="openai/gpt-oss-20b", temperature=temperature, max_tokens=max_token)
    return chat_completion.choices[0].message.content

print(ask_llm_system(SYSTEM_PROMPT, USER_PROMPT.format(patient_name="John Doe", patient_notes="Patient complains of severe headaches and nausea. Blood pressure is elevated. MRI shows no abnormalities.")))