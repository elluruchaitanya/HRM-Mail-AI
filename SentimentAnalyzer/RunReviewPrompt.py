import os;
import json
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
from langchain.prompts import PromptTemplate

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

def load_hotel_directory(hotel_id):
    directory = Path(__file__).parent.parent / "Frontend/HotelTemplates"
    target_path = os.path.join(directory, hotel_id)
    fallback_path = os.path.join(directory, "basic")
    if os.path.isdir(target_path):
        return target_path
    elif os.path.isdir(fallback_path):
        return fallback_path
    else:
        raise FileNotFoundError(f"Neither '{hotel_id}' nor 'basic' folder found in {directory}")
def load_hotel_profile(hotel_directory):
     filepath = os.path.join(hotel_directory,"profile_info.json")
     with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
def load_hotel_tone(hotel_directory):
    file_path = os.path.join(hotel_directory, "tone.txt")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File 'tone.txt' not found in directory '{hotel_directory}'")    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
def load_hotel_greetings(hotel_directory):
    file_path = os.path.join(hotel_directory, "greetings.txt")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File 'greetings.txt' not found in directory '{hotel_directory}'")    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
def load_hotel_usps(hotel_directory):
    file_path = os.path.join(hotel_directory, "usps.txt")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File 'usps.txt' not found in directory '{hotel_directory}'")    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
def load_hotel_signatures(hotel_directory):
    file_path = os.path.join(hotel_directory, "signatures.txt")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File 'signatures.txt' not found in directory '{hotel_directory}'")    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
def load_file_content(directory, filename):
    path = os.path.join(directory, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{filename} not found in {directory}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()    
def format_response(hotel_id, main_response,reviewuser):
    try:
        hotel_dir = load_hotel_directory(hotel_id)
        profile = json.loads(load_file_content(hotel_dir, "profile_info.json"))
        hotel_name = profile.get("hotelname", "Our Hotel")

        tone = load_file_content(hotel_dir, "tone.txt")
        greetings = load_file_content(hotel_dir, "greetings.txt").replace("{username}", reviewuser)
        usps = load_file_content(hotel_dir, "usps.txt")
        signatures = load_file_content(hotel_dir, "signatures.txt").replace("{hotel_name}", hotel_name)

        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", tone),
            ("ai", greetings),
            ("ai", main_response),
            ("ai", usps),
            ("ai", signatures)
        ])

        return chat_prompt.format_messages()
    except Exception as e:
        print(f"[ERROR] format_response: {e}")
        return "We encountered an issue while processing your request. Please try again later."

def generate_and_process_response(promptInput,reviewuser,hotel_id):
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    model_name = "ft:gpt-3.5-turbo-1106:personal::CGjZCrFr"

    try:
        messages = format_response(hotel_id, promptInput, reviewuser)
        llm = ChatOpenAI(model=model_name, temperature=0.3, max_tokens=250)
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"[ERROR] generate_and_process_response: {e}")
        return "We encountered an issue while processing your request. Please try again later."


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
        print(hotel_id)
        #if str(hotel_id).lower() == "846688":
        model_name = "ft:gpt-3.5-turbo-1106:personal::CGjZCrFr" #ft:gpt-3.5-turbo-0125:personal::C8hz9bCy"
        #else:
         #   model_name = "gpt-4-turbo"
        
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

 