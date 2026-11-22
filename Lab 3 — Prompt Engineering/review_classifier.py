from groq import Groq
import os  
from dotenv import load_dotenv
load_dotenv("../.env")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

few_shot = """Classify the sentiment of the review as Positive, Negative or Neutral. Reply with the label only.

Review: Amazing service!
Sentiment: Positive

Review: It was okay, nothing special.
Sentiment: Neutral

Review: Worst experience ever.
Sentiment: Negative

Review: Waste of time & money.
Sentiment:"""

def ask_llm(user_query,max_token = 1000,temperature = 0):
    message = [
        {
            "role":"user",
            "content":user_query
        }
    ]
    chat_completion = client.chat.completions.create( messages=message,model="openai/gpt-oss-20b",temperature=temperature,max_tokens=max_token)
    response = chat_completion.choices[0].message.content
    return response

print(ask_llm(few_shot))