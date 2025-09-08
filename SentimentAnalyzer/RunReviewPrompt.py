import os;
import streamlit as st
import requests
from pathlib import Path
import openai
import logging
import time
import unicodedata
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts.chat import (    
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.globals import set_llm_cache
# Disable caching globally
set_llm_cache(None)


#import SentimentAnalyzer.sentimentAnalysis as sentiment

from dotenv import load_dotenv
# Verify API key

# Load environment variables
load_dotenv()
google_api_key = os.getenv("OPEN_API_KEY_INFO_Account")
OPENAI_API_KEY=google_api_key

def find_file_by_hotelid(hotel_id):
    directory = Path(__file__).parent.parent / "Frontend/HotelTemplates"
    print("searching for the file")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt') and f"-{hotel_id}.txt" in file:
                print("found the file")
                return os.path.join(root, file)
    print("file doesnot exists so returning basic template file")
    return  Path(__file__).parent.parent/f"Frontend/HotelTemplates/basic_template.txt"
def clean_template_text(file_path: str) -> str:
    """
    Reads and cleans special characters from a template file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Normalize and remove special characters
    cleaned_text = unicodedata.normalize("NFKD", raw_text)
    cleaned_text = cleaned_text.encode("ascii", "ignore").decode("ascii")

    return cleaned_text

def generate_assistant_prompt(hotel_id):   
   template_path =find_file_by_hotelid(hotel_id)   
   print(f'template path',template_path)
   time.sleep(60)
   return SystemMessagePromptTemplate.from_template_file(template_path,
    input_variables=["username"] )

def generate_response(promptInput, reviewuser, hotel_id):    
    #sentimentResponse = sentiment.AnalyzeSentiment(promptInput)
    assistant_prompt = generate_assistant_prompt(hotel_id)
    #print(f'system prompt generated as ',assistant_prompt)
    openai.api_key = OPENAI_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    try:
        # Human prompt with a placeholder
        human_prompt = HumanMessagePromptTemplate.from_template("{user_query}")

        # Combine into ChatPromptTemplate
        chat_prompt = ChatPromptTemplate.from_messages([assistant_prompt, human_prompt])
        if str(hotel_id) == "The Royal Sonesta Chase Park Plaza Hotel-846688":
            model_name = "ft:gpt-3.5-turbo-0125:personal::C8hz9bCy"
        else:
            model_name = "gpt-4-turbo"
        
        print(f"[DEBUG] Using model: {model_name} for hotel_id={hotel_id}")
        llm = ChatOpenAI(model = model_name, temperature=0.3, max_tokens=250)
        # Format messages with actual user input
        messages = chat_prompt.format_messages(user_query=promptInput,username=reviewuser)

        # Run the model
        response = llm.invoke(messages)
        #print(f'generated response: \n', response.content)
        return response.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "We encountered an issue while processing your request. Please try again later."

 