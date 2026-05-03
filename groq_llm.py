from groq import Groq
import json
from langsmith import traceable
from dotenv import load_dotenv
import os

load_dotenv()  

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# 🚀 GROQ TOOL CALLER
# =========================
@traceable(name="groq_call")
def call_groq(prompt, model="llama-3.3-70b-versatile", temperature=0.2):

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        # =========================
        # 🧹 CLEAN OUTPUT
        # =========================
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        return content

    except Exception as e:
        return str(e)