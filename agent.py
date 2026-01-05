import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq

from prompt import OPTIMIZED_SYSTEM_PROMPT

load_dotenv()

model = init_chat_model(
    model="openai:gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

agent = create_deep_agent(
    model=model,
    system_prompt=OPTIMIZED_SYSTEM_PROMPT,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is LangGraph?"}]})

print(result)
