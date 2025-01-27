from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def generate_response(user_input, user_id, past_conversations,user_info):
    # user_info = query_chromadb(user_input)
    context = " ".join(past_conversations[-10:]) + " " + str(user_info)
    prompt_template = PromptTemplate(
        input_variables=["context", "input", "user_info"],
        template="""
        You are a personalized AI assistant. Use the following past conversations and user information (some of which might be in past conversations) to provide a relevant response.
        If the user asks for personal details you have seen, retrieve them from the conversation or user information.
        Keep replies simple, informative, and engaging.
        Avoid emojis, asterisks, and symbols. MAKE SURE THE RESPONSES DO NOT EXCEED 2 SENTENCES AND IT'S SMALL AND CONCISE.

        Context:
        {context}

        User Information:
        {user_info}

        User:
        {input}

        Assistant:
        """

    )
    prompt = prompt_template.format(context=context, user_info=user_info, input=user_input)
    response = llm.invoke(prompt).content
    return response

if __name__=="__main__":
    output = generate_response("what are some things I can do in summer?", 1,["oof this summer is really bad and warm"],["The users likes having icecreams during summer","The user likes having watermelon juice in summer"])
    print(output)

    