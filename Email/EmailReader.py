import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import json
import os
import pandas as pd


class EmailReader:
    def __init__(self, email_user, email_pass, imap_server="imap.gmail.com"):
        self.email_user = email_user
        self.email_pass = email_pass
        self.imap_server = imap_server

    def fetch_latest_email(self, sender=None, subject=None, unread_only=False):
        try:
            print("[INFO] Connecting to IMAP server...")
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_pass)
            print("[INFO] Logged in.")

            mail.select("inbox")

            # Build IMAP search criteria
            search_criteria = []

            if unread_only:
                search_criteria.append("UNSEEN")
            if sender:
                search_criteria.append(f'FROM "{sender}"')
            if subject:
                search_criteria.append("ALL")  # Fetch everything and filter manually later
                subject_contains = subject.lower()
            else:
                subject_contains = None

            if not search_criteria:
                search_query = "ALL"
            else:
                search_query = f'({" ".join(search_criteria)})'

            print(f"[INFO] Searching with criteria: {search_query}")
            status, messages = mail.search(None, search_query)

            if status != "OK":
                print("[ERROR] Failed to search emails.")
                return None, None

            email_ids = messages[0].split()
            if not email_ids:
                print("[INFO] No matching emails found.")
                return None, None

            latest_email_id = email_ids[-1]
            print(f"[INFO] Fetching email ID: {latest_email_id.decode()}")

            status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
            if status != "OK":
                print("[ERROR] Failed to fetch the email.")
                return None, None

            msg = email.message_from_bytes(msg_data[0][1])

            # Decode subject
            # Decode subject
            raw_subject, encoding = decode_header(msg["Subject"])[0]
            subject = (
                raw_subject.decode(encoding or "utf-8", errors="replace")
                if isinstance(raw_subject, bytes)
                else raw_subject
            )

            # Manual partial match check
            if subject_contains and subject_contains not in subject.lower():
                print(f"[INFO] Skipping email: subject does not contain '{subject_contains}'")
                return None, None


            # Get HTML body
            body = ""
            reviewTextTable = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/html" and "attachment" not in content_disposition:
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(charset, errors="replace")
                        break
            else:
                if msg.get_content_type() == "text/html":
                    charset = msg.get_content_charset() or "utf-8"
                    body = msg.get_payload(decode=True).decode(charset, errors="replace")

            if not body:
                print("[INFO] No HTML body found.")
                return subject, None

            # Parse and extract specific table
            soup = BeautifulSoup(body, "html.parser")
            tables = soup.find_all("table")
            print(f"[INFO] Found {len(tables)} table(s)")

            table_data = []
            selected_table_html = None

            for index, table in enumerate(tables):
                rows = table.find_all("tr")
                if not rows or len(rows) < 2:
                    continue

                headers = [cell.get_text(strip=True) for cell in rows[0].find_all(["th", "td"])]

                # Check for specific headers
                if len(headers) < 10:
                    continue
                if not ("Review text" in headers and "Review score" in headers):
                    continue

                data_rows = []
                for row in rows[1:]:
                    cells = row.find_all(["td", "th"])
                    values = [cell.get_text(strip=True) for cell in cells]
                    if len(values) == len(headers):
                        data_rows.append(dict(zip(headers, values)))

                if data_rows:
                    table_data = data_rows
                    selected_table_html = str(table)
                    print(f"[✅] Target table found at index {index}")
                    break

            if table_data:
                # Save JSON data
                print("table_data", table_data)
                reviewTextTable = table_data
                # If table_data is your original list of review dictionaries
                # Add 'ArissaAI' column with empty strings
                for review in reviewTextTable:
                    review["ArissaAI"] = ''

    # Save to JSON file
                with open("table_data.json", "w", encoding="utf-8") as f:
                    json.dump(table_data, f, ensure_ascii=False, indent=4)
                    print("[✅] Table data saved to table_data.json")

            #     # Save HTML table only (optional)
            #     with open("selected_table.html", "w", encoding="utf-8") as f:
            #         f.write(selected_table_html)
            #     print("[✅] Raw HTML of table saved to selected_table.html")
            # else:
            #     print("[⚠️] No matching table found.")

            mail.logout()
            return subject, body , reviewTextTable

        except Exception as e:
            print(f"[ERROR] An error occurred: {str(e)}")
            return None, None


# Example usage (comment out when integrating):
# reader = EmailReader("your_email@gmail.com", "your_password")
# reader.fetch_latest_email(sender="example@domain.com", unread_only=True)
