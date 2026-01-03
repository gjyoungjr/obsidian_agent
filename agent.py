import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq

load_dotenv()

# model = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0.0,
#     max_retries=2,
# )

model = init_chat_model(
    model="claude-sonnet-4-5-20250929",
    api_key=os.getenv("CLAUDE_API_KEY"),
)

agent = create_deep_agent(
    model=model,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is LangGraph?"}]})

print(result.content)
