<div align="center">

# 📧 Gmail Attachment Downloader

### Securely Search & Download Gmail Attachments with OAuth2 Authentication

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=3500&pause=1200&color=00BFFF&center=true&vCenter=true&width=900&lines=Gmail+OAuth2+Authentication;Search+Emails+with+Attachments;Bulk+Download+Attachments+as+ZIP;Analytics+Dashboard;Built+with+Flask+%26+Gmail+API" />

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask)
![Gmail API](https://img.shields.io/badge/Gmail_API-EA4335?style=for-the-badge&logo=gmail&logoColor=white)
![OAuth2](https://img.shields.io/badge/OAuth2-4285F4?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql)

</div>

---

# 📖 Table of Contents

- 📌 Overview
- ✨ Features
- 🛠️ Tech Stack
- ⚙️ System Architecture
- 🔄 Application Workflow
- 📂 Project Structure
- 🚀 Installation
- ⚙️ Configuration
- ▶️ Running the Application
- 📊 Dashboard Features
- 🔒 Security
- 📈 Future Enhancements
- 🤝 Contributing
- 📜 License

---

# 📌 Overview

The **Gmail Attachment Downloader** is a secure Flask web application that allows authenticated users to connect their Gmail account using **Google OAuth2**, search emails containing attachments, and download multiple attachments as a single ZIP archive.

The application also provides an analytics dashboard for tracking downloaded attachments and supports multiple database backends.

---

# ✨ Features

✅ Secure Gmail OAuth2 Authentication

✅ Search Gmail Messages

✅ Filter Emails with Attachments

✅ Bulk Download as ZIP

✅ Analytics Dashboard

✅ User Authentication

✅ SQLite / MySQL / PostgreSQL Support

✅ Responsive Web Interface

---

# 🛠️ Tech Stack

### Backend

<p align="center">

<img src="https://skillicons.dev/icons?i=python,flask"/>

</p>

### Database

<p align="center">

<img src="https://skillicons.dev/icons?i=sqlite,mysql,postgres"/>

</p>

### APIs & Services

<p align="center">

<img src="https://img.shields.io/badge/Gmail_API-EA4335?style=for-the-badge&logo=gmail&logoColor=white"/>

<img src="https://img.shields.io/badge/Google_OAuth2-4285F4?style=for-the-badge&logo=google"/>

</p>

### Tools

<p align="center">

<img src="https://skillicons.dev/icons?i=git,github,vscode"/>

</p>

---

# ⚙️ System Architecture

```text
                 Gmail Account
                      │
                      ▼
            Google OAuth2 Login
                      │
                      ▼
             Gmail API Authentication
                      │
                      ▼
              Search Gmail Messages
                      │
                      ▼
         Filter Emails with Attachments
                      │
                      ▼
          Download Selected Attachments
                      │
                      ▼
               Create ZIP Archive
                      │
                      ▼
             Download to Local System
```

---

# 🔄 Application Workflow

```text
User Login
      │
      ▼
Authenticate with Google
      │
      ▼
Grant Gmail Permission
      │
      ▼
Search Emails
      │
      ▼
Select Attachments
      │
      ▼
Download ZIP
      │
      ▼
View Analytics Dashboard
```

---

# 📂 Project Structure

```text
email-attachment-download
│
├── app.py
├── requirements.txt
├── config.py
├── models.py
├── templates/
├── static/
├── credentials.json
├── instance/
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/vishnu0414/email-attachment-download.git
```

Navigate into the project

```bash
cd email-attachment-download
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ⚙️ Configuration

## 1️⃣ Environment Variables

Create a `.env` file or configure the following variables:

```env
SECRET_KEY=your_secret_key

DB_TYPE=sqlite

GMAIL_CREDENTIALS_FILE=credentials.json
```

---

## 2️⃣ Google Cloud Setup

- Create a project in **Google Cloud Console**
- Enable the **Gmail API**
- Configure the **OAuth Consent Screen**
- Create **OAuth2 Credentials**
- Download the credentials file
- Save it as:

```text
credentials.json
```

inside the project directory.

---

# ▶️ Running the Application

Start the Flask server:

```bash
python app.py
```

Open your browser:

```
http://localhost:5000
```

---

# 📊 Dashboard Features

<details>

<summary>📧 Gmail Search</summary>

- Search inbox emails
- Filter emails containing attachments
- View sender, subject, and date

</details>

<details>

<summary>📂 Attachment Downloads</summary>

- Select multiple attachments
- Download as ZIP
- Fast bulk download

</details>

<details>

<summary>📈 Analytics Dashboard</summary>

- Download statistics
- Attachment counts
- Recent activity
- User insights

</details>

---

# 🔒 Security Features

- 🔐 Google OAuth2 Authentication
- 🔑 Secure User Login
- 📧 Gmail API Authorization
- 🛡️ Protected Routes
- 🔒 Environment Variable Configuration

---

# 📈 Future Enhancements

- ☁️ Cloud Storage Integration
- 📄 PDF Preview
- 📧 Advanced Gmail Filters
- 📊 Download Reports
- 🌙 Dark Mode
- 🔍 Attachment Search
- 📱 Mobile Responsive Dashboard

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

---

# 📜 License

This project is intended for educational purposes.

---

<div align="center">

## ⭐ If you found this project useful, consider giving it a Star!

Made with ❤️ using Flask, Gmail API & OAuth2

</div>
MIT
