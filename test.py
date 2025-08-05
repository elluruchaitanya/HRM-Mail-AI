import SentimentAnalyzer.RunReviewPrompt as prompt
reviewScore = '10'
reviewTravelPurpose =  'wedding'
reviewUser =  'User1'
reviewText=  'Great location, staff, and facility. Dog friendly'
hotel_id='The Royal Sonesta Chase Park Plaza Hotel-846688'
reviewLength = len(reviewText.strip())  # ✅ Get length of the review

finalReviewText = (
            f"Here is a review from the user {reviewUser} with a {reviewScore} star review "
            f"and visited here for a {reviewTravelPurpose}. "
            f"The review provided by the user is \"{reviewText}\" having the length of {reviewLength} characters. "
            f"Provide the response for this."
)
print(finalReviewText)
response = prompt.generate_response(finalReviewText,reviewUser, hotel_id)
print(response)
