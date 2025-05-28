from Email.EmailReader import EmailReader
def main():
    email_user = "chaitanya.elluru@arissaindia.com"
    email_pass = "Hanuman$25"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465

    reader = EmailReader(email_user, email_pass)    

    subject, body = reader.fetch_latest_email()
    print(subject)
    print(body)

if __name__ == "__main__":
    main()
