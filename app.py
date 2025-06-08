import os
from dotenv import load_dotenv
from Email.EmailReader import EmailReader
import SentimentAnalyzer.RunReviewPrompt as prompt

def print_formatted_email(subject, body):
    print("\n" + "=" * 60)
    print("📨  NEW EMAIL RECEIVED")
    print("=" * 60)
    print(f"\n🟦 SUBJECT:\n{subject.strip()}")
    print("\n📝 BODY:\n" + "-" * 50)
    
    if not body.strip():
        print("[No plain text body found or empty message]")
    else:
        # Limit body preview for very long messages
        preview = body.strip()

        print(preview)

def RunPromptToGenerateResponse(reviewTable):
    for review in reviewTable:
       response = prompt.generate_response("Hi, I am"+review.Revieweruser+". My purpose of travel is "+review.purposeOfTravel+"."+review.reviewText)
       review["ArissaAI"] = response
    print(reviewTable)

def main():
    load_dotenv()

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("[ERROR] Missing email credentials.")
        return

    reader = EmailReader(email_user, email_pass)

    # Filters – customize as needed
    sender_filter = "veera.venkata@arissaindia.com"    # ← or None
    subject_filter = "Daily Review Report"         # ← or None
    unread_only = False                    # ← change to False to include all

    subject, body, reviewTextTable = reader.fetch_latest_email(
        sender=sender_filter,
        subject=subject_filter,
        unread_only=unread_only
    )

    if subject and body:
        print_formatted_email(subject, body)
    else:
        print("[INFO] No matching email found.")
    if reviewTextTable :
        # call the prompt that returns the response.
        reviewTextTable.insert(len(reviewTextTable.columns),"ArissaAI",'')
        RunPromptToGenerateResponse(reviewTextTable)
        print(reviewTextTable)

if __name__ == "__main__":
    main()
