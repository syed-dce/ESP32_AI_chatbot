import json
from uuid import uuid4
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="personal_info")

def query_chromadb(query_text, user_id: str = "1", top_k: int = 2):
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
    )

    # Filter results by user_id in metadata
    filtered_results = []
    for i, metadata in enumerate(results.get("metadatas", [[]])[0]):
        if metadata.get("user_id") == user_id:
            doc = results["documents"][0][i]
            filtered_results.append(doc)

    return filtered_results


def save_chat_history(chat_history):
    with open("chat_history.json", "a", encoding="utf-8") as file:
        json.dump(chat_history, file, ensure_ascii=False, indent=4)
        file.write("\n")

def extract_personal_info(user_prompt):
    prompt_template = f"""
You are an AI assistant that extracts personal information from a single user message.

TASK:
Check if the user's message contains any personal information (e.g., name, job, hobbies, location, preferences, relationships, etc.).

If it does, extract it and return a list of one or more clear natural language facts.
Example: ["The user's name is Jack", "The user likes swimming"]

If it contains no useful personal information, return the string: None

USER MESSAGE:
\"\"\"{user_prompt}\"\"\"

YOUR RESPONSE:
"""
    response = model.invoke(prompt_template).content
    return response


def store_chromadb(user_prompt, user_id: str = "1"):
    extracted = extract_personal_info(user_prompt)
    print(extracted)

    # Check if extraction returned anything useful
    if extracted and extracted.lower() != "none":
        try:
            # Ensure it's a list (you can also validate/parse JSON if needed)
            personal_facts = eval(extracted) if extracted.startswith("[") else [extracted]

            # Store each fact in ChromaDB
            for fact in personal_facts:
                collection.add(
                    documents=[fact],
                    metadatas=[{"user_id": user_id}],
                    ids=[str(uuid4())]
                )
            print(f"Stored {len(personal_facts)} personal info item(s) for user {user_id}")
        except Exception as e:
            print(f"Failed to store in ChromaDB: {e}")
    else:
        print("No personal info found to store.")

if __name__=="__main__":

    store_chromadb("my name is jackie chan and I love doing karate","5")
    store_chromadb("The sun is really warm today","5") 
    store_chromadb("I love my dog jimmy very much","5")
    store_chromadb("I work as a software Engineer","5")
    output=query_chromadb(query_text="I want to do something physical today", user_id="5", top_k=2)
    print(output)


