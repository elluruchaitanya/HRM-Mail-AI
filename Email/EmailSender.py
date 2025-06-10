import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:

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

    def SendEmail(subject, html_content, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_pass):
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
