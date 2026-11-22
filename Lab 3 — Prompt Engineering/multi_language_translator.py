from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a multi-language translator.
Translate the given sentence into the requested target language.
Follow the requested formality level.
If the formality is formal, use polite and professional language.
If the formality is informal, use casual and friendly language.
Return only the translated sentence without any explanation.
"""

USER_PROMPT = """Sentence: {sentence}
Target Language: {target_language}
Formality: {formality}"""

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

sentence = "How are you? I hope you are doing well."
user_query = USER_PROMPT.format(
    sentence=sentence,
    target_language="Hindi",
    formality="Formal"
)
response = ask_llm_system(SYSTEM_PROMPT, user_query)
print(response)