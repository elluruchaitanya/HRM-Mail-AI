import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY_INFO_Account")


# ---------------------------------------------------------
# File Loaders
# ---------------------------------------------------------
def load_hotel_directory(hotel_id):
    """
    Locate the hotel’s template directory, fallback to 'basic' if not found.
    """
    directory = Path(__file__).parent.parent / "Frontend/HotelTemplates"
    target_path = os.path.join(directory, hotel_id)
    fallback_path = os.path.join(directory, "basic")
    if os.path.isdir(target_path):
        return target_path
    elif os.path.isdir(fallback_path):
        return fallback_path
    else:
        raise FileNotFoundError(f"Neither '{hotel_id}' nor 'basic' folder found in {directory}")


def load_file_content(directory, filename):
    """
    Load text content from a file.
    """
    path = os.path.join(directory, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{filename} not found in {directory}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def pick_random_greeting(greetings_raw, username):
    """Randomly select greeting and personalize it with username."""
    greetings = greetings_raw.split(",")
    chosen = random.choice(greetings).strip()
    # Insert space before username
    greeting = chosen.replace("{username}", f"{username}")
    if not greeting.endswith(","):
        greeting += ","
    # Ensure 'Dear Chris,' not 'DearChris,'
    greeting = greeting.replace(f"Dear{username}", f"Dear {username}")
    greeting = greeting.replace(f"Hello{username}", f"Hello {username}")
    return greeting




# ---------------------------------------------------------
# Prompt Formatter
# ---------------------------------------------------------
def format_response(hotel_id, main_response, reviewuser, debug=False):
    """
    Build the structured messages for the model with tone, greetings, usps, and signatures.
    Returns formatted messages, greeting, and signature.
    """
    try:
        hotel_dir = load_hotel_directory(hotel_id)

        # Load profile info
        profile = json.loads(load_file_content(hotel_dir, "profile_info.json"))
        hotel_name = profile.get("hotelname", "Our Hotel")

        # Load templates
        tone = load_file_content(hotel_dir, "tone.txt")
        greetings_raw = load_file_content(hotel_dir, "greetings.txt")
        greeting = pick_random_greeting(greetings_raw, reviewuser)
        usps = load_file_content(hotel_dir, "usps.txt")
        signature = load_file_content(hotel_dir, "signatures.txt").replace("{hotel_name}", hotel_name)
        signature = signature.replace("\\n", "\n").strip()  # fix line breaks

        if debug:
            print("========== DEBUG INFO ==========")
            print(f"ReviewUser passed in: {reviewuser}")
            print(f"Greeting chosen: {greeting}")
            print(f"Signature loaded: {signature}")
            print("================================")

        # System prompt
        system_prompt = f"""
You are a hotel manager assistant. 
Follow these rules strictly when writing responses:

{tone}

Here are hotel-specific details (use them naturally, not as a list):
{usps}
"""

        # User prompt (with enforced greeting + signature)
        wrapped_prompt = f"""
You must start the response with exactly this greeting:
{greeting}

You must end the response with exactly this signature:
{signature}

Here is the guest review you are responding to:
\"\"\"{main_response}\"\"\"

Guidelines:
- Do not remove or rewrite the greeting or the signature.
- Use the tone and USP instructions from the system prompt.
- Keep the response concise (under 250 tokens).
"""

        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", wrapped_prompt),
        ])

        return chat_prompt.format_messages(), greeting, signature

    except Exception as e:
        print(f"[ERROR] format_response: {e}")
        return [{"role": "system", "content": "We encountered an issue while processing your request."}], "", ""


# ---------------------------------------------------------
# Response Generator
# ---------------------------------------------------------
def generate_response(promptInput, reviewuser, hotel_id, debug=False):
    """
    Generates a response using hotel templates + fine-tuned model.
    Always enforces greeting and signature.
    """
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    model_name = "ft:gpt-3.5-turbo-1106:personal::CGjZCrFr"
    # model_name = "gpt-4-turbo"

    try:
        messages, greeting, signature = format_response(hotel_id, promptInput, reviewuser, debug)
        llm = ChatOpenAI(model=model_name, temperature=0.3, max_tokens=250)
        response = llm.invoke(messages)
        content = response.content.strip()

        # Remove stray commas at the very beginning
        if content.startswith(","):
            content = content.lstrip(",").strip()

        # ✅ Enforce greeting at the start
        if greeting and not content.startswith(greeting):
            content = f"{greeting}\n\n{content}"

        # ✅ Normalize and enforce single signature
        if signature:
            # Strip duplicates
            if signature in content:
                # Keep only the last occurrence
                parts = content.split(signature)
                content = parts[0].strip()
            # Append clean signature
            content = f"{content}\n\n{signature}"

        return content

    except Exception as e:
        print(f"[ERROR] generate_response: {e}")
        return "We encountered an issue while processing your request. Please try again later."
