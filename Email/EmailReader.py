import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re
import time


class EmailReader:
    def __init__(self, email_user, email_pass, imap_server="imap.gmail.com"):
        self.email_user = email_user
        self.email_pass = email_pass
        self.imap_server = imap_server

    def retrieve_unread_mails(self,sender=None, subject=None, unread_only=False):
          try:
            allUnreadMessageData = []
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
                return None

            email_ids = messages[0].split()            
            if not email_ids:
                print("[INFO] No matching emails found.")
                return None
            for emailContent in email_ids:
                print(f"[INFO] Fetching email ID: {emailContent.decode()}")
                status, msg_data = mail.fetch(emailContent, "(RFC822)")
                if status != "OK":
                    print("[ERROR] Failed to fetch the email.")
                    return None
                if msg_data and isinstance(msg_data[0], tuple): 
                    allUnreadMessageData.append(msg_data[0][1])
            # Add a label (custom flag example)
                mail.store(emailContent, '+FLAGS', r'(\Flagged)')
            mail.close()
            mail.logout()
            return allUnreadMessageData
          except Exception as e:
                print(f"[ERROR] An error occurred: {str(e)}")
                return None
          


    def fetch_latest_email(self, msg_data):
        try:
            msg = email.message_from_bytes(msg_data)
            raw_subject, encoding = decode_header(msg["Subject"])[0]
            subject = (
                raw_subject.decode(encoding or "utf-8", errors="replace")
                if isinstance(raw_subject, bytes)
                else raw_subject
            )

            body = ""
            reviewTextTable = ""
            report_filters_html = ""

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
                return subject, None, None, None

            soup = BeautifulSoup(body, "html.parser")

            # --- Extract Report Filters block ---
            for tag in soup.find_all():
                if "Report Filters:" in tag.get_text(strip=True):
                    report_filters_html = str(tag)
                    hotel_id = self.fetch_hotel_id(report_filters_html)
                    time.sleep(60)
                    print("[✅] Found Report Filters block.")
                    break
            else:
                print("[⚠️] Report Filters block not found.")
            # print("[🧾] Extracted Report Filters block:\n", report_filters_html)

            # --- Find Review Table ---
            tables = soup.find_all("table")
            print(f"[INFO] Found {len(tables)} table(s)")

            table_data = []
            selected_table_html = None

            for index, table in enumerate(tables):
                rows = table.find_all("tr")
                if not rows or len(rows) < 2:
                    continue

                headers = [cell.get_text(strip=True) for cell in rows[0].find_all(["th", "td"])]
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
                reviewTextTable = table_data
                for review in reviewTextTable:
                    review["ArissaAI Responses"] = ''
                    review["Review Comments"] = ''
                with open("table_data.json", "w", encoding="utf-8") as f:
                    json.dump(reviewTextTable, f, ensure_ascii=False, indent=4)
                    print("[✅] Table data saved to table_data.json")
            else:
                print("[⚠️] No matching table found.")

            return subject, body, reviewTextTable, hotel_id

        except Exception as e:
            print(f"[ERROR] An error occurred: {str(e)}")
            return None, None, None, None
        
    def fetch_hotel_id(self, report_html):
                # parse the HTML
        soup = BeautifulSoup(report_html, 'html.parser')

        # find all text in the <td> tag
        td_text = soup.get_text(separator=' ').strip()

        # use regex to find hotel ID
        match = re.search(r'- Hotel IDs:\s*(\d+)', td_text)
        hotel_id = match.group(1) if match else None

        print(f'Hotel ID: {hotel_id}')
        return hotel_id