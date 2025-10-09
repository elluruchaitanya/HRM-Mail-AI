from SentimentAnalyzer.hotel_responder import generate_response

# Example Test
if __name__ == "__main__":
    reviewScore = "4"
    # reviewTravelPurpose = "wedding"
    reviewUser = "Hannah Barahona"
    reviewText = (
    "I pulled into the garage a couple of hours before check-in. "
    "When I asked if our room was ready the person at the front desk told me that it was ready "
    "but I would have to pay $50 to access it early, even though it was ready and no one was using it. "
    "When I told her I’d parked in the garage she said I’d have to pay to leave the garage and come back later. "
    "Since I didn’t want to pay for parking twice, I felt I didn’t really have a choice but to pay the early check in fee. "
    "We were assigned a room and when we opened the door to it, there was someone else already inside! "
    "She said she didn’t know how that happened but I spent the rest of our stay worried that someone else would be given a key to our room. "
    "The location is great and close to Navy Pier, I chose this hotel because it had decent reviews and the price was excellent. "
    "But I would not stay here again because of security concerns."
    )


    hotel_id = "870301"
    reviewLength = len(reviewText.strip().split())
    reviewSource = "Google.com"

    finalReviewText = (
        f"Here is a review from the user {reviewUser} with a {reviewScore} star review from the review source {reviewSource}. "
        f"The review provided by the user is \"{reviewText}\" having the length of {reviewLength}. "
        f"Provide the response for this."
    )

    print("========== INPUT REVIEW ==========")
    print(finalReviewText)
    print("==================================")

    response = generate_response(finalReviewText, reviewUser, hotel_id, debug=True)

    print("========== MODEL RESPONSE ==========")
    print(response)
    print("===================================")
