import os;
import streamlit as st
import requests
from pathlib import Path
import openai
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import SentimentAnalyzer.sentimentAnalysis as sentiment

from dotenv import load_dotenv
# Verify API key

# Load environment variables
load_dotenv()
google_api_key = os.getenv("OPEN_API_KEY_INFO_Account")
OPENAI_API_KEY=google_api_key

logged_in_manager_profile={
    "username" : "Manager",
    "Email":"Manager@YopMail.com"
}

hotelname="Royal Sonesta Chase Park"

signature_template = "\n\nBest regards,\nAI Assistant"

def generate_assistant_prompt(sentimentResponse):
    if sentimentResponse == "Positive":
        return "Respond in under 250 tokens. Be concise and complete. Always starts the response with 'Dear {user_name}' and end the response with '{signature_template}'.Express appreciation and reinforce the positive aspects mentioned by the user. Encourage engagement and loyalty by highlighting standout features."
    elif sentimentResponse == "Neutral":
        return "Respond in under 250 tokens. Be concise and complete. Always starts the response with 'Dear {user_name}' and end the response with '{signature_template}'.You are an informative assistant. Provide factual and helpful responses in a neutral manner."
    elif sentimentResponse == "Negative":
        return "Respond in under 250 tokens. Be concise and complete. Always starts the response with 'Dear {user_name}' and end the response with '{signature_template}'.Be empathetic and solution-oriented. Address concerns carefully, offer resolutions or clarifications, and provide actionable steps to improve customer experience."
    else:
        return "Respond in under 250 tokens. Be concise and complete. Always starts the response with 'Dear {user_name}' and end the response with '{signature_template}'.You are an assistant that provides general guidance."

hyperlink = f'<a href="https://www.sonesta.com/royal-sonesta/mo/st-louis/chase-park-plaza-royal-sonesta-st-louis?utm_source=google&utm_medium=organic&utm_campaign=gmb">{hotelname}</a>'


def generate_response(promptInput):    
    sentimentResponse = sentiment.AnalyzeSentiment(promptInput)
    assistant_prompt = generate_assistant_prompt(sentimentResponse+"Be concise. Use plain language. Avoid repetition.")
    openai.api_key = OPENAI_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    llm = ChatOpenAI(model = "gpt-4-turbo", temperature=0.7, max_tokens=250)
    try:
        messages = [
            SystemMessage(content=assistant_prompt),
            HumanMessage(content=promptInput)
        ]
        result = llm.invoke(messages)
        response = result.content[:1000].strip()
        print(f"Generated response: {response}")
        max_response_length = 1000
        response = response[:max_response_length]
        if hotelname in response:
            return response.replace(hotelname,hyperlink)
        else:
            return response
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "We encountered an issue while processing your request. Please try again later."

 