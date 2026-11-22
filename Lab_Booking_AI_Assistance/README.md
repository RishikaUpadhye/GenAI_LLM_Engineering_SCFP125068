# 🧪 Lab Test Booking AI Assistant

An AI-powered laboratory test booking system that allows patients to explore diagnostic tests, check appointment availability, book laboratory tests, view their bookings and cancel appointments through natural language conversations.

Built using **Python, SQLite, LangChain, LangGraph, Groq LLM and Streamlit**, this project demonstrates how AI agents can interact with databases and perform real-world operations with user approval.

---

## 📌 Project Overview

The Lab Test Booking AI Assistant is designed to simplify the process of booking diagnostic laboratory tests.

Instead of manually searching for tests or navigating through multiple booking pages, patients can communicate directly with an AI assistant.

The assistant understands user requests, retrieves real-time information from the SQLite database, and performs booking-related operations after obtaining patient approval.

### 🎯 Project Objectives

- Develop an AI-powered conversational laboratory booking assistant.
- Retrieve laboratory test information and prices from SQLite.
- Check available appointment slots.
- Allow patients to book and cancel appointments through AI conversations.
- Implement approval before database modifications.
- Maintain user-specific booking information.
- Provide general laboratory test information through web search.
- Maintain conversation context across multiple interactions.

---

## ✨ Features

### 🤖 AI-Powered Conversational Assistant
- Natural language interaction with patients.
- Understands laboratory test-related queries.
- Uses AI tools to retrieve information from the database.
- Provides general information about laboratory tests.

### 🔐 Patient Authentication
- Patient registration and login.
- Signup using Name, Email and Password.
- Unique patient ID generation.
- Password hashing before database storage.
- Patient-specific session management.

### 🧪 Laboratory Test Management
- View available laboratory tests.
- Display test categories and descriptions.
- Retrieve test prices directly from SQLite.
- Support multiple laboratory test categories.

### 📅 Appointment Management
- Check available appointment slots.
- Book appointments directly through AI conversations.
- Cancel existing bookings through AI conversations.
- Automatically update slot availability after booking or cancellation.

### ✅ Human Approval Mechanism
- AI requests patient approval before booking.
- AI requests patient approval before cancellation.
- Rejected operations do not modify the database.
- Booking receipts are retrieved from database records.

### 🔒 Privacy and Security
- Patient-specific booking access.
- Booking ownership validation.
- User identity supplied through runtime context.
- Email redaction before sending messages to the AI model.
- Parameterized SQL queries to reduce SQL injection risks.

### 🌐 General Information Search
- Uses Tavily Search for general laboratory information.
- Provides information about test purposes and fasting requirements.
- Uses SQLite as the source of truth for prices and availability.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| SQLite | Relational database |
| LangChain | LLM and tool integration |
| LangGraph | AI agent workflow and state management |
| Groq | LLM inference provider |
| GPT-OSS-20B | Language model |
| Tavily Search | General web information retrieval |
| Pandas | Tabular data handling |
| Python-dotenv | Environment variable management |

---

## 🏗️ Project Architecture

The application follows an AI-agent-based architecture.

```text
                  PATIENT
                     |
                     v
              STREAMLIT UI
                     |
              LOGIN / SIGNUP
                     |
                     v
                AI ASSISTANT
                     |
                     v
               GROQ LLM
                     |
                     v
              LANGCHAIN AGENT
                     |
                     v
               LANGGRAPH
                     |
          +----------+----------+
          |          |          |
          v          v          v
      READ TOOLS  WRITE TOOLS  WEB SEARCH
          |          |          |
          v          v          v
        SQLITE    APPROVAL    TAVILY
                     |
              +------+------+
              |             |
              v             v
           APPROVE        REJECT
              |             |
              v             v
        DATABASE UPDATE  NO CHANGE
```

### Booking Workflow

1. Patient requests a laboratory test.
2. AI retrieves test information and available slots.
3. Patient selects an appointment slot.
4. AI presents the booking details.
5. Patient approves or rejects the booking.
6. If approved, the booking is saved in SQLite.
7. The assistant displays the booking confirmation.

### Cancellation Workflow

1. Patient requests cancellation.
2. AI retrieves the patient's bookings.
3. Patient identifies the booking to cancel.
4. AI requests cancellation approval.
5. If approved, the booking status changes to `Cancelled`.
6. The associated appointment slot becomes `Available`.

---

## 🗄️ Database Structure

The project uses SQLite for data storage.

Database file:

```text
lab_book.db
```

The database contains the following tables:

### 1. Users

Stores patient registration information.

| Column | Description |
|---|---|
| user_id | Unique patient identifier |
| name | Patient name |
| email | Patient email |
| password_hash | Hashed password |
| created_at | Account creation date |

### 2. Tests

Stores laboratory test information.

| Column | Description |
|---|---|
| test_id | Unique test identifier |
| test_name | Laboratory test name |
| category | Test category |
| description | Test description |
| price | Test price |

### 3. Slots

Stores appointment availability.

| Column | Description |
|---|---|
| slot_id | Unique appointment slot ID |
| test_id | Associated test ID |
| slot_date | Appointment date |
| slot_time | Appointment time |
| status | Available / Booked |

### 4. Bookings

Stores patient appointment records.

| Column | Description |
|---|---|
| booking_id | Unique booking identifier |
| user_id | Patient identifier |
| test_id | Booked test |
| slot_id | Selected appointment slot |
| status | Confirmed / Cancelled |
| booking_date | Booking creation date |

---

## 📂 Project Structure

```text
Lab_Booking_AI_Assistance/
│
├── app.py
│
├── backend/
│   ├── agent.py
│   ├── database.py
│   └── __init__.py
│
├── lab_book.db
│
├── lab_booking_ai.ipynb
│
├── README.md
│
└── requirements.txt
```

### File Description

| File | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `backend/agent.py` | AI agent, tools, model integration and approval workflow |
| `backend/database.py` | Database creation, authentication and booking operations |
| `backend/__init__.py` | Backend package initialization |
| `lab_book.db` | SQLite database |
| `lab_booking_ai.ipynb` | Original project development and experimentation notebook |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

---

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### Prerequisites

Make sure you have installed:

- Python 3.10 or above
- pip
- Git
- Groq API Key
- Tavily API Key (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate into the project directory:

```bash
cd Lab_Booking_AI_Assistance
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

For Ubuntu / Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
touch .env
```

Add your API keys:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

**Important:** Never upload your `.env` file or expose your API keys on GitHub.

### 6. Run the Application

Execute:

```bash
streamlit run app.py
```

The application will start locally.

Open the URL displayed in your terminal. Usually:

```text
http://localhost:8501
```

---

## 🔑 API Configuration

### Groq API

Groq provides access to the language model used by the AI assistant.

Obtain an API key from:

https://console.groq.com/

### Tavily API

Tavily provides web search capabilities for general laboratory test information.

Obtain an API key from:

https://app.tavily.com/

Tavily is optional. Without its API key, the database-based functionality remains available, but general web search will not be enabled.

---

## 🧠 AI Agent Tools

The AI assistant uses tools to interact with external resources.

| Tool | Operation | Description |
|---|---|---|
| `list_tests` | Read | Retrieves laboratory tests |
| `check_slots` | Read | Checks appointment availability |
| `my_bookings` | Read | Retrieves the logged-in patient's bookings |
| `book_test` | Write | Creates an appointment after approval |
| `cancel_booking` | Write | Cancels an appointment after approval |
| Tavily Search | Search | Retrieves general laboratory information |

The AI model does not receive unrestricted SQL access.

Database operations are handled by predefined Python functions.

---

## 🔐 Security and Privacy

The project implements several security-related mechanisms:

- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes.
- Parameterized SQL queries are used for database operations.
- Patient identity is passed through agent runtime context.
- Booking ownership is validated before cancellation.
- Email addresses are redacted before messages reach the AI model.
- Booking and cancellation operations require explicit patient approval.

**Note:** This project is an academic prototype. Production deployment would require additional authentication hardening, HTTPS, secure session management, rate limiting and appropriate data protection controls.

---

## 🧪 Testing and Evaluation

The project was designed around the following test scenarios:

1. Check available appointment slots.
2. Successfully book a laboratory test.
3. Book a test for another user.
4. Reject a booking approval.
5. Handle an appointment slot conflict.
6. Successfully cancel a booking.
7. Retrieve general information using web search.
8. Handle a symptom-related question without diagnosing the patient.

These scenarios help verify the correctness of the agent's tool usage and database operations.

---

## 🚀 Future Enhancements

Potential improvements include:

- Email-based booking confirmations.
- Password reset functionality.
- Patient profile management.
- Admin dashboard for laboratory staff.
- Dynamic appointment slot management.
- Booking history and downloadable receipts.
- Deployment to a cloud hosting platform.
- Integration with real diagnostic laboratory services.

---

## ⚠️ Disclaimer

This is an academic project developed for educational and demonstration purposes.

The laboratory, test catalogue, prices and appointment data are fictional.

The assistant is not a medical diagnostic system and does not replace professional medical advice.

---

## 👨‍💻 Author

**Rishika Upadhye**

MCA Student | Data Science

GitHub: [@RishikaUpadhye](https://github.com/RishikaUpadhye)

---

## ⭐ Support

If you find this project interesting, consider giving the repository a star on GitHub!

**Built with Python, AI and a passion for learning.** 🧪🤖
