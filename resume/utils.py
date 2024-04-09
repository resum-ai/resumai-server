import os
from pathlib import Path
import environ

from pinecone import Pinecone
# from utils.openai_call import get_embedding

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

def retrieve_similar_answers(user_qa):
    try:
        pc = Pinecone()
        index = pc.Index("resumai-self-introduction-index")
        query_embedding = get_embedding(user_qa)
        retrieved_data = index.query(
            vector=query_embedding, top_k=3, include_metadata=True
        )
        return retrieved_data["matches"]

    except Exception as e:
        print(e)
        return []

def run_llm(query: str, chat_history: list[dict[str, any]]) -> any:
    chat = ChatOpenAI(verbose=True, temperature=0, model_name="gpt-4")
    conversation = ConversationChain(
        llm=chat,
        verbose=True,
    )
    return conversation.predict(input=query)
