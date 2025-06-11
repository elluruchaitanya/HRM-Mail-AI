import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:

    def format_html_table(reviewTable):
        if not reviewTable:
            return "<p>No review data found.</p>"

        desired_headers = ["Reviewer user", "Review text", "ArissaAI Responses", "Review Comments"]

        table_style = "width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;"
        th_style = "border: 1px solid #444444; padding: 10px; background-color: #34BDEB; color: white; text-align: left;"
        td_style = "border: 1px solid #444444; padding: 10px; text-align: left; vertical-align: top;"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333333; background-color: #ffffff; padding: 20px;">
            <h2 style="color: #2c3e50;">📬 ArissaAI Review Responses</h2>
            <table style="{table_style}">
                <tr>
        """

        for header in desired_headers:
            html += f'<th style="{th_style}">{header}</th>'
        html += "</tr>"

        for review in reviewTable:
            html += "<tr>"
            for header in desired_headers:
                value = review.get(header, "")
                if isinstance(value, str):
                    value = value.replace('\n', '<br>')
                html += f'<td style="{td_style}">{value}</td>'
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
        recipients = ["brian@thereputationlab.com", "vinay@arissaindia.com"]
        msg["Bcc"] = ", ".join(recipients)  

        part = MIMEText(html_content, 'html')
        msg.attach(part)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, recipients, msg.as_string())

        print(f"[✅] Email sent to {recipients}, {to_email} with subject: {subject}")

