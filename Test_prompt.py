# hotel_review_formatter.py

# Sample metadata for hotel-source formatting rules
hotel_source_config = {
    ("HotelA", "tripadvisor"): {
        "greeting": "Dear {username},",
        "signature": "Warm Regards,\nHotelA Team",
        "stopwords": ["very", "really", "just"],
        "usps": ["Prime location", "Award-winning service"]
    },
    ("HotelB", "google"): {
        "greeting": "Hello {username},",
        "signature": "Best Wishes,\nHotelB Concierge",
        "stopwords": ["actually", "basically"],
        "usps": ["Eco-friendly rooms", "24/7 support"]
    }
    # Add more hotel-source pairs as needed
}

def format_review_response(raw_response: str, hotel: str, source: str, username: str) -> str:
    # Load formatting config or fallback to default
    config = hotel_source_config.get((hotel, source), {
        "greeting": "Hi {username},",
        "signature": "Regards,\nHotel Team",
        "stopwords": [],
        "usps": []
    })

    # Format greeting
    greeting = config["greeting"].format(username=username)

    # Remove stopwords (basic implementation)
    for word in config["stopwords"]:
        raw_response = raw_response.replace(f" {word} ", " ")

    # Inject USPs if not already present
    for usp in config["usps"]:
        if usp.lower() not in raw_response.lower():
            raw_response += f"\n\nDid you know? {usp}"

    # Assemble final message
    formatted_response = f"{greeting}\n\n{raw_response.strip()}\n\n{config['signature']}"
    return formatted_response

# Example usage
if __name__ == "__main__":
    # Simulated GPT response
    gpt_response = "Thank you for your feedback. We are very happy you enjoyed your stay. Our staff is just thrilled to hear this."

    # Format the response
    formatted = format_review_response(
        raw_response=gpt_response,
        hotel="HotelA",
        source="tripadvisor",
        username="Chaitanya"
    )

    # Output the result
    print("\n--- Formatted Review Response ---\n")
    print(formatted)