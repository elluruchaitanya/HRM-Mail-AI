# HRM-Mail-AI
HotelReviewManagement ViaEmail Integrated with AI
We are splitting the project into 4 major components
1. Email Reader – Fetches email content.
2. Sentiment Analyzer – Determines sentiment (positive, negative, neutral).
3. Response Generator – Crafts a reply based on sentiment.
4. Email Sender – Sends the generated response.

First we will focus on Email Reader.

# You are an sales manager for an hotels group and also an expert in providing the responses to the customer reviews by considering the purpose of the travel. Your responses should consider the purpose and also should add an weightage to the strong points in terms of marketing and sales. Ensure that you start the response by greeting the user and end with a thank you note and manager signature with the hotel details. Here is the review "Hi, I'am Suzanne Chisum. This is my solo trip. Great place! What a treasure! With attached parking garage and restaurants on site. Movie theater has a theater organ in it! So cool!Noteworthy details: In site cinema with the main theater having a pipe organ."#

  <!-- def json_to_html_table(json_data):
       df = pd.DataFrame(json_data)
       html_table = df.to_html()
       return html_table

   # Example usage
   json_data = [
       {"name": "Alice", "age": 30, "city": "New York"},
       {"name": "Bob", "age": 25, "city": "Los Angeles"},
       {"name": "Charlie", "age": 35, "city": "Chicago"}
   ]

   html_output = json_to_html_table(json_data)
   print(html_output)
 -->
