import os
from dotenv import load_dotenv
from Email.EmailReader import EmailReader
import SentimentAnalyzer.RunReviewPrompt as prompt
from Email.EmailSender import EmailSender
import datetime

def print_formatted_email(subject, body):
    print("\n" + "=" * 60)
    print("📨  NEW EMAIL RECEIVED")
    print("=" * 60)
    print(f"\n🟦 SUBJECT:\n{subject.strip()}")
    print("\n📝 BODY:\n" + "-" * 50)

    if not body.strip():
        print("[No plain text body found or empty message]")
    else:
        preview = body.strip()
        print(preview)


def RunPromptToGenerateResponse(reviewTable):
    for review in reviewTable:
        print(f"Review: {review}")
        print(f"Reviewer: {review['Reviewer user']}, Purpose of Travel: {review['Purpose of travel']}, Review Text: {review['Review text']}")
        response = prompt.generate_response(
            "Hi, I am " + review['Reviewer user'] + ". My purpose of travel is " + review['Purpose of travel'] + ". " + review['Review text'])
        review["ArissaAI"] = response
        print(f"Generated response for {review['Reviewer user']}: {response}")
    print(f"[INFO] All generated responses: {reviewTable}")

def RenderEmailProcessReviewThenReply():
    load_dotenv()

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("[ERROR] Missing email credentials.")
        return

    reader = EmailReader(email_user, email_pass)

    sender_filter = "veera.venkata@arissaindia.com"
    subject_filter = "Daily Review Report"
    unread_only = True

    subject, body, reviewTextTable = reader.fetch_latest_email(
        sender=sender_filter,
        subject=subject_filter,
        unread_only=unread_only
    )

    if subject and body:
        print_formatted_email(subject, body)
    else:
        print("[INFO] No matching email found.")
        return

    if reviewTextTable:
        print(f"reviewTextTable: {reviewTextTable}")
        RunPromptToGenerateResponse(reviewTextTable)

    html_content_With_AIResponse = EmailSender.format_html_table(reviewTextTable)
    if html_content_With_AIResponse:
        EmailSender.SendEmail(
                subject=subject,
                html_content=html_content_With_AIResponse,
                to_email=sender_filter,  # sending back to the original sender
                from_email=email_user,
                smtp_server="smtp.gmail.com",  # adjust if using different SMTP server
                smtp_port=465,
                smtp_user=email_user,
                smtp_pass=email_pass
        )  

def main():
    now = datetime.datetime.now()

    # Check if it's 5:30 AM
    if now.hour == 5 and now.minute == 30:
        print("Executing task...")  # Replace this with the actual function call
        RenderEmailProcessReviewThenReply()  # Call the function that runs the task
    else:
        print("Skipping task. Current time:", now.strftime("%H:%M"))

if __name__ == "__main__":
    main()
