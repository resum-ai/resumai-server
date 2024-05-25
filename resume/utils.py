import os
from pathlib import Path
import environ

from pinecone import Pinecone
from utils.openai_call import get_embedding

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

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
            vector=query_embedding, top_k=2, include_metadata=True
        )
        return retrieved_data["matches"]

    except Exception as e:
        print(e)
        return []


llm = ChatOpenAI(verbose=True, temperature=0, model_name="gpt-4")
memory = ConversationBufferMemory()


def run_llm(query: str, chat_history: list[dict[str, any]]) -> any:
    # for chat in chat_history:
    #     memory.save_context(
    #         inputs={"human": chat["query"]}, outputs={"ai": chat["response"]}
    #     )
    conversation = ConversationChain(llm=llm, verbose=True)
    return conversation.predict(input=query)
