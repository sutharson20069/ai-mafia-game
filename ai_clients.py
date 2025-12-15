import os, json, asyncio, random
from dotenv import load_dotenv

# Load keys
load_dotenv()

# --- OpenAI ---
from openai import AsyncOpenAI
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Gemini ---
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Groq (OpenAI compatible) ---
groq_client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# --- Mistral ---
from mistralai.async_client import MistralAsyncClient
mistral_client = MistralAsyncClient(api_key=os.getenv("MISTRAL_API_KEY"))


# ---------------------------------------
# SYSTEM PROMPT (VERY IMPORTANT)
# ---------------------------------------
SYSTEM_PROMPT = """
You are playing the game Mafia.

Rules:
- Choose ONLY from alive players
- Respond ONLY in valid JSON
- JSON format:
{
  "target": "AIx",
  "reason": "your reasoning"
}
Do not add extra text.
"""


# ---------------------------------------
# PROVIDER ROUTER
# ---------------------------------------
async def call_ai(role, name, alive, memory):
    provider = select_provider(name)

    prompt = f"""
Your role: {role}
You are: {name}
Alive players: {alive}

Think carefully and choose ONE target.
"""

    try:
        if provider == "openai":
            return await call_openai(prompt)

        if provider == "gemini":
            return await call_gemini(prompt)

        if provider == "groq":
            return await call_groq(prompt)

        if provider == "mistral":
            return await call_mistral(prompt)

    except Exception as e:
        # HARD SAFETY FALLBACK
        return {
            "target": random.choice(alive),
            "reason": f"Fallback used due to error: {str(e)}"
        }


# ---------------------------------------
# PROVIDER SELECTION (YOU CAN CHANGE)
# ---------------------------------------
def select_provider(name):
    return {
        "AI1": "openai",
        "AI2": "gemini",
        "AI3": "groq",
        "AI4": "mistral",
        "AI5": "openai",
        "AI6": "groq",
    }.get(name, "openai")


# ---------------------------------------
# OPENAI
# ---------------------------------------
async def call_openai(prompt):
    res = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return json.loads(res.choices[0].message.content)


# ---------------------------------------
# GROQ
# ---------------------------------------
async def call_groq(prompt):
    res = await groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return json.loads(res.choices[0].message.content)


# ---------------------------------------
# GEMINI
# ---------------------------------------
async def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    res = await model.generate_content_async(
        SYSTEM_PROMPT + "\n" + prompt
    )
    return json.loads(res.text)


# ---------------------------------------
# MISTRAL
# ---------------------------------------
async def call_mistral(prompt):
    res = await mistral_client.chat(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(res.choices[0].message.content)
