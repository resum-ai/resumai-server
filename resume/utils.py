import os
from pathlib import Path
import environ

from pinecone import Pinecone

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

from utils.openai_call import get_embedding

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


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