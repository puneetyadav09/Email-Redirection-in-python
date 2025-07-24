# 📧 Email Redirection System with AI-based Department Classification

## 🔍 Overview

This is an AI-enhanced Python-based email redirection system that automatically reads incoming emails, classifies their content using a local LLM (via [Ollama](https://ollama.com/)), and forwards them to the appropriate department email address. It also includes fallback handling for unclassified emails and a `.env`-powered configuration system.

## ⚙️ Key Features

- ✅ Automatically connects to a configured email inbox
- 🧠 Uses a local LLM (via Ollama) to classify emails into departments
- 📤 Forwards emails to department-specific addresses based on classification
- 🛑 Fallback handling for unclassified/misrouted emails
- 🔒 Uses `.env` for secure configuration of credentials and model settings
- 📊 Designed to be extended with dashboards, logging, and analytics

---

## 🧰 Tech Stack

| Component           | Description                      |
|---------------------|----------------------------------|
| Python 3.x          | Core language                    |
| IMAP + SMTP         | Email fetching and forwarding    |
| `email`, `smtplib`  | Built-in email handling          |
| `python-dotenv`     | Environment variable loading     |
| `asyncio`, `aioimaplib` | Async event loop for fetching |
| `ollama`            | Local LLM for classification     |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/puneetyadav09/Email-Redirection-in-python.git
```

### 2. Set Up Environment

Install Dependencies
```bash
pip install -r requirements.txt
```
Create a .env file (you can copy from .env.example):
```bash
cp .env.example .env
```
Fill in your email credentials, SMTP server, and Ollama config.


### 3. Run Ollama (LLM Engine)

Make sure [Ollama](https://ollama.com/download) is installed and running:
```bash
ollama run llama3
```
You can use any other supported model (e.g., mistral, phi3, etc.)

### 4. Start the Application

Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

---

## 🔐 .env Configuration

```env
EMAIL_ACCOUNT=your_email@example.com
EMAIL_PASSWORD=your_password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

OLLAMA_MODEL=llama3

DEFAULT_DEPARTMENT_EMAIL=fallback@example.com
```

---

## 🧪 How It Works

1. Connects to your email inbox using IMAP.
2. Checks for new unread emails.
3. Sends the email body to the LLM for classification.
4. Based on department match, forwards to the mapped department email.
5. If no department is matched, sends to fallback department address.

---

## 📁 Project Structure

```bash
backend/
├── main.py             
├── .env                
├── .env.example       
└── requirements.txt    
```

---


## 👨‍💻 Created By
Puneet Yadav

[Github](https://github.com/puneetyadav09/) . [LinkedIn](https://www.linkedin.com/in/puneetyadav09)