import os
from dotenv import load_dotenv
from Email.EmailReader import EmailReader
import SentimentAnalyzer.RunReviewPrompt as prompt
from Email.EmailSender import EmailSender
import datetime
import time

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
        #print(preview)


def RunPromptToGenerateResponse(reviewTable):
    for review in reviewTable:
        reviewScore = review['Review score']
        reviewTravelPurpose = review['Purpose of travel']
        reviewUser = review['Reviewer user']
        reviewText= review['Review text']
        finalReviewText= f"Here is a review from the user {reviewUser} with a {reviewScore} star review and visited here for a {reviewTravelPurpose}. The review provided by the user is {reviewText}.Provide the response for this."
        print(finalReviewText)
        response = prompt.generate_response(finalReviewText,reviewUser)
        print(response)
        review["ArissaAI Responses"] = response

def RenderEmailProcessReviewThenReply():
    load_dotenv()

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("[ERROR] Missing email credentials.")
        return

    reader = EmailReader(email_user, email_pass)

    sender_filter = os.getenv("SENDER_EMAIL")
    subject_filter = "Daily Review Report"
    unread_only = True

    
    all_mail_msg_data = reader.retrieve_unread_mails(
        sender=sender_filter,
        subject=subject_filter,
        unread_only=unread_only
    )
    
    if all_mail_msg_data is not  None:
        for maildata in all_mail_msg_data:
            
            subject, body, reviewTextTable =  reader.fetch_latest_email(maildata)    

            if subject and body:
                print_formatted_email(subject, body)
            else:
                print("[INFO] No matching email found.")
                return

            if reviewTextTable:
                #print(f"reviewTextTable: {reviewTextTable}")
                RunPromptToGenerateResponse(reviewTextTable)
                print(f"reviewTextTablewithresponse \n \n: {reviewTextTable}")
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
    else:
        print("No matching emails found")  

def main():
    load_dotenv()    
    try:
        print("Executing task...")
        RenderEmailProcessReviewThenReply()

    except ValueError:
        print(f"[ERROR] Invalid SCHEDULE_TIME format in .env")
        return

def run_at_time(target_time):
    while True:
        now = datetime.datetime.now().time()
        #if now >= target_time:
        main()
            #break
        #time.sleep(900)  # Check every second

if __name__ == "__main__":
     # Set the target time for task execution (e.g., 10:30 AM)
    print(datetime.datetime.now(datetime.timezone.utc))
    schedule_time = os.getenv("SCHEDULE_TIME", "05:30")  # Default to 05:30 if not found
    schedule_hour, schedule_minute = map(int, schedule_time.split(":"))
    target_time = datetime.time(schedule_hour, schedule_minute, 0)
    run_at_time(target_time)