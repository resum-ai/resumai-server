from openai import OpenAI
import environ
from pathlib import Path
import os

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_chat_openai(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    output = response.choices[0].message.content
    return output


def get_embedding(text, model="text-embedding-3-small"):
    # text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model).data
    response = response[0].embedding
    return response
