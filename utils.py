import os
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_host = os.getenv("PINECONE_HOST")
qroq_api_key = os.getenv("GROQ_API_KEY")

pc = Pinecone(
    api_key=pinecone_api_key,
)
index = pc.Index(host = pinecone_host)

# From image to text
def img2text(url):
    # Define the prompt template
    template = """
        Bạn là một trợ lý hữu ích, mô tả hình ảnh một cách chi tiết, tập trung vào các từ khóa chính nhưng không quá dài dòng (không quá 3 câu). 
        Hãy trả lời bằng tiếng Việt.
        HÌNH ẢNH: {url}
        MÔ TẢ:
    """
    prompt = PromptTemplate(template=template, input_variables=["url"])

    llm = ChatGroq(
        model="llama-3.2-90b-vision-preview",
        temperature=0.6,
        max_retries=2,
        api_key=qroq_api_key
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )

    description = chain.run(url=url)
    return description


# Get songs from context
@tool
def get_songs(context: str) -> dict:
    """
    Retrieve the top 5 most relevant songs for a given context using a vector search.

    Args:
        context (str): A short description of the desired mood, vibe, or situation 
                       (e.g., "a calm evening beach walk").

    Returns:
        dict: A dictionary with a 'result' key containing a 'hits' list.
              Each hit includes:
                - '_id': the song ID
                - '_score': similarity score
                - 'fields': a dictionary containing:
                    - 'category': song genre or style
                    - 'text': full description including title, artist, genre, and lyrics
    """
    query_payload = {
        "inputs": {"text": context},
        "top_k": 5
    }
    
    results = index.search(namespace="", query=query_payload)
    return results


tools = [get_songs]


# Pick music
def pick_music(context, tools):
    music_prompt_template = PromptTemplate(
    input_variables=["context"],
    template="""
    You are a great music recommendation system that can use external tools when needed.

    One of the tools available to you is called 'get_songs', which can retrieve the top 5 most relevant songs based on a given context (such as mood, place, time of day, etc). These songs include metadata like genre, title, and lyrics.

    Use the tool if you want inspiration from existing songs.

    Your task is to recommend 5 songs that best fit the provided context, suitable as background music 
    for Instagram or Facebook stories. Provide the song titles (separated by commas).

    CONTEXT: {context}

    RECOMMENDATIONS:
    """
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        max_retries=2,
    )

    tools = [get_songs]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    prompt = music_prompt_template.format(context=context)
    response = agent.invoke(prompt)

    print(response)

def img2music_chain(url):
    # First, generate a text description from the image
    context = img2text(url)
    print("Generated context from image:")
    print(context)
    
    # Then, use the text as context to pick music recommendations
    pick_music(context, tools)
    
if __name__ == "__main__":
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"  
    img2music_chain(image_url)

# print(get_songs("Hình ảnh miêu tả con ong"))