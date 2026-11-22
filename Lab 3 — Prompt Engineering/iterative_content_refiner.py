from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a content refinement assistant.
Improve the given draft by fixing the specific issue mentioned by the user.
Keep the original meaning of the draft.
Do not make unnecessary changes.
Return only the revised draft without explanations.
"""

USER_PROMPT = """Draft Text: {draft_text}
Issue to Fix: {issue_to_fix}"""

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

draft_text = "Our company provide good service to customer and we always try to solving their problems quickly."
issue_to_fix = "Fix grammatical errors."

for round_number in range(1, 4):
    print(f"\nRound {round_number}:")
    user_query = USER_PROMPT.format(
        draft_text=draft_text,
        issue_to_fix=issue_to_fix
    )
    response = ask_llm_system(SYSTEM_PROMPT, user_query)
    print(response)
    draft_text = response