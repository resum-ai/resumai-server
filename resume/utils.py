import os
from pathlib import Path

import pinecone

from utils.openai_call import get_embedding

env = os.environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent.parent
os.environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


def retrieve_similar_answers(user_qa):
    try:
        pinecone.init(api_key=os.environ.get('PINECONE_API_KEY'), environment="gcp-starter")
        index = pinecone.Index("resumai-self-introduction-index")
        query_embedding = get_embedding(user_qa)
        retrieved_data = index.query(
            vector=query_embedding, top_k=3, include_metadata=True
        )
        return retrieved_data["matches"]

    except Exception as e:
        return []