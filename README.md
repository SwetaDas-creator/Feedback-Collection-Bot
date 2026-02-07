# Feedback-Collection-Bot
Conversational survey chatbot for collecting customer insights using NPS, CSAT, and CES. Uses ScaleDown logic to reduce survey length by 75%, boost completion rates by 50%, and analyze 10,000+ responses in real time with sentiment analysis, trend detection, and actionable recommendations.

A backend-driven feedback analytics system built using FastAPI and Python.
The system collects customer feedback, performs sentiment analysis, calculates NPS and CSAT, detects fraud or spam responses, identifies trends, and supports CSV export for reporting.

**Features**

Feedback Collection
- Accepts structured feedback (NPS, CSAT, CES, comments)
- Stores responses in an SQLite database

Sentiment Analysis
~~~~~~~~~~~~~~~~~~
- Uses TextBlob
- Classifies feedback as **Positive**, **Neutral**, or **Negative**

Analytics
~~~~~~~~~
- NPS score calculation
- Average CSAT calculation
- Promoter, Passive, and Detractor classification

Trend Detection
~~~~~~~~~~~~~~~
- Identifies whether NPS is improving or declining over time

Fraud / Spam Detection
~~~~~~~~~~~~~~~~~~
Detects:

Very short comments
Generic spam words (e.g., ok, test)
Extreme NPS scores with minimal text

Suspicious feedback is flagged without deleting stored data.

CSV Export
~~~~~~~~~~~~~~~~~~
- Exports the complete feedback dataset
- Useful for Excel-based reporting and offline analysis

Tech Stack
----------

+-----------+------------+
| Layer     | Technology |
+===========+============+
| Backend   | FastAPI    |
+-----------+------------+
| Language  | Python     |
+-----------+------------+
| Database  | SQLite     |
+-----------+------------+
| NLP       | TextBlob   |
+-----------+------------+
| API Docs  | Swagger    |
+-----------+------------+

Project Structure
-----------------

::

    feedback_bot/
    │
    ├── app.py              # Main FastAPI application
    ├── database.py         # SQLite connection and table creation
    ├── feedback.db         # SQLite database
    ├── README.rst          # Project documentation

Setup Instructions
------------------

1. Clone the repository::

       git clone https://github.com/your-username/feedback-collection-bot.git
       cd feedback-collection-bot

2. Install dependencies::

       pip install fastapi uvicorn textblob

3. Run the application::

       python -m uvicorn app:app --reload

4. Open API documentation::

       http://127.0.0.1:8000/docs

API Endpoints
-------------

Submit Feedback
~~~~~~~~~~~~~~~~~~
POST /submit

Request body:
~~~~~~~~~~~~~~~~~~
{
  "nps": 9,
  "csat": 5,
  "ces": 4,
  "comment": "Fast delivery and great support"
}
~~~~~~~~~~~~~~~~~~
Response:
~~~~~~~~~~~~~~~~~~
{
  "status": "saved",
  "sentiment": "Positive",
  "fraud": false
}
~~~~~~~~~~~~~~~~~~
View All Feedback:
~~~~~~~~~~~~~~~~~~
**GET** ``/results``  

Returns all stored feedback responses.

Analytics
~~~~~~~~~
**GET** ``/analytics``  

Returns:
- Total responses
- NPS score
- Average CSAT

Insights
~~~~~~~~
**GET** ``/insights``  

Returns:
- Sentiment distribution percentages
- High-level improvement insight

Trends
~~~~~~
**GET** ``/trends``

Response example::

    {
      "trend": "Improving",
      "first_nps": 7,
      "latest_nps": 9
    }

Fraud Detection
~~~~~~~~~~~~~~~
**GET** ``/fraud``  

Returns all flagged spam or suspicious feedback.

CSV Export
~~~~~~~~~~
**GET** ``/export``  

Downloads::

    feedback_export.csv

Sample Test Data
----------------

::

    {
      "nps": 3,
      "csat": 2,
      "ces": 2,
      "comment": "Very slow and confusing process"
    }

::

    {
      "nps": 10,
      "csat": 5,
      "ces": 5,
      "comment": "ok"
    }
~~~~~~~~~~~~~~~~~~
Design Decisions
----------------
~~~~~~~~~~~~~~~~~~
- SQLite chosen for simplicity and portability
- Fraud detection implemented using rule-based logic
- APIs designed to be UI-agnostic
- CSV export enables offline analysis and reporting
~~~~~~~~~~~~~~~~~~
Future Enhancements
-------------------
~~~~~~~~~~~~~~~~~~
- Machine learning–based spam detection
- Authentication and admin roles
- Date-based trend analytics
- Frontend dashboard integration
- Cloud deployment (Render, Railway)
