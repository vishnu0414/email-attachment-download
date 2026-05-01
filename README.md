# Gmail Attachment Downloader

A Flask web application for downloading Gmail attachments with OAuth2 integration.

## Features

- Gmail OAuth2 Authentication
- Search emails with attachments
- Bulk downloads as ZIP
- Analytics dashboard
- Multi-database support (SQLite, MySQL, PostgreSQL)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Set environment variables:
   - `SECRET_KEY` - Flask secret key
   - `DB_TYPE` - Database type (sqlite, mysql, postgresql)
   - `GMAIL_CREDENTIALS_FILE` - Path to Google OAuth credentials.json

2. Get Gmail API credentials from Google Cloud Console and save as `credentials.json`

## Usage

```bash
python app.py
```

Access at: http://localhost:5000

1. Register/Login
2. Connect Gmail via OAuth
3. Search and download attachments
4. View analytics on dashboard

## License

MIT
