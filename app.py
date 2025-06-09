import os
from dotenv import load_dotenv
from Email.EmailReader import EmailReader
import SentimentAnalyzer.RunReviewPrompt as prompt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


def format_html_table(reviewTable):
    if not reviewTable:
        return "<p>No review data found.</p>"

    headers = list(reviewTable[0].keys())

    html = """
    <html>
    <head>
        <style>
            table {
                width: 100%%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }
            th {
                background-color: #f4f4f4;
            }
            tr:nth-child(even) {
                background-color: #fafafa;
            }
        </style>
    </head>
    <body>
        <h2>📬 ArissaAI Review Responses</h2>
        <table>
            <tr>
    """

    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr>"

    for review in reviewTable:
        html += "<tr>"
        for header in headers:
            value = review.get(header, "")
            if isinstance(value, str):
                value = value.replace('\n', '<br>')
            html += f"<td>{value}</td>"
        html += "</tr>"

    html += """
        </table>
    </body>
    </html>
    """
    return html


def send_email(subject, html_content, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_pass):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())

    print(f"[✅] Email sent to {to_email} with subject: {subject}")


def main():
    load_dotenv()

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("[ERROR] Missing email credentials.")
        return

    reader = EmailReader(email_user, email_pass)

    sender_filter = "veera.venkata@arissaindia.com"
    subject_filter = "Daily Review Report"
    unread_only = False

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

        html_content = format_html_table(reviewTextTable)

        send_email(
            subject=subject,
            html_content=html_content,
            to_email=sender_filter,  # sending back to the original sender
            from_email=email_user,
            smtp_server="smtp.gmail.com",  # adjust if using different SMTP server
            smtp_port=465,
            smtp_user=email_user,
            smtp_pass=email_pass
        )


if __name__ == "__main__":
    main()
