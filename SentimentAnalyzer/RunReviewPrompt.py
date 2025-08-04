import os;
import streamlit as st
import requests
from pathlib import Path
import openai
import logging
import time
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts.chat import (    
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

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
        
        llm = ChatOpenAI(model = "gpt-4-turbo", temperature=0.7, max_tokens=250)
        # Format messages with actual user input
        messages = chat_prompt.format_messages(user_query=promptInput,username=reviewuser)

        # Run the model
        response = llm.invoke(messages)
        #print(f'generated response: \n', response.content)
        return response.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "We encountered an issue while processing your request. Please try again later."

 