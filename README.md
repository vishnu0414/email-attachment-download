# Gmail Attachment Downloader

A modern Flask web application for downloading Gmail attachments with OAuth2 integration, featuring multiple database support, analytics charts, and comprehensive user management.

## Features

- **Multi-Database Support**: SQLite (default), MySQL, PostgreSQL, and SQL Server
- **Gmail OAuth2 Integration**: Secure authentication with Google APIs
- **Advanced Search**: Find emails with attachments using Gmail search operators
- **Bulk Downloads**: Download multiple attachments as ZIP files
- **Analytics Dashboard**: Interactive charts showing file types, download trends, and size distribution
- **User Management**: Account creation, login, delete account, and Gmail disconnect options
- **Light Theme**: Clean, consistent light theme design
- **Database Status**: Real-time database connection monitoring

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd gmail-attachment-downloader-complete
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your configuration:
     ```env
     # Database Configuration
     DB_TYPE=sqlite  # Options: sqlite, mysql, postgresql, mssql
     DB_HOST=localhost
     DB_NAME=gmail_downloader
     DB_USER=your_username
     DB_PASSWORD=your_password

     # Flask Configuration
     SECRET_KEY=your-secret-key-here
     FLASK_ENV=development

     # Gmail API (get from Google Cloud Console)
     GMAIL_CREDENTIALS_FILE=credentials.json
     ```

4. **Set up Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` and place in project root

5. **Run the application:**
   ```bash
   python app.py
   ```

   Access at: http://localhost:5000

## Database Configuration

### SQLite (Default)
No additional setup required. Database file created automatically.

### MySQL
1. Install MySQL server
2. Create database: `CREATE DATABASE gmail_downloader;`
3. Set environment variables:
   ```env
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   ```

### PostgreSQL
1. Install PostgreSQL server
2. Create database and user
3. Set environment variables:
   ```env
   DB_TYPE=postgresql
   DB_HOST=localhost
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

### SQL Server
1. Install SQL Server
2. Install ODBC Driver 17 for SQL Server
3. Create database
4. Set environment variables:
   ```env
   DB_TYPE=mssql
   DB_HOST=localhost
   DB_USER=sa
   DB_PASSWORD=your_password
   ```

## Usage

1. **Register/Login**: Create an account or login
2. **Connect Gmail**: Authenticate with Google OAuth2
3. **Search & Download**: Use advanced search to find attachments
4. **View Analytics**: Check dashboard for charts and statistics
5. **Manage Account**: Disconnect Gmail or delete account as needed

## API Endpoints

- `GET /health` - Health check with database status
- `GET /api/stats` - User statistics
- `GET /api/chart_data` - Chart data for analytics
- `GET /api/gmail/status` - Gmail authentication status

## Development

### Project Structure
```
gmail-attachment-downloader-complete/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── gmail_oauth.py        # Gmail OAuth2 handling
├── gmail_utils.py        # Gmail utility functions
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── instance/            # Database files (SQLite)
├── static/              # Static assets (CSS, JS, images)
├── templates/           # Jinja2 templates
└── README.md            # This file
```

### Running Tests
```bash
# Set test environment
export FLASK_ENV=testing

# Run tests (if implemented)
python -m pytest
```

## Deployment

### Heroku
1. Set buildpacks for Python
2. Configure environment variables in Heroku dashboard
3. Deploy using git push

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [Issues](https://github.com/your-repo/issues) page
- Review the documentation
- Ensure all dependencies are properly installed

## OAuth troubleshooting: unverified app / access_denied

If you see an error like "Access blocked: <app> has not completed the Google verification process" (Error 403: access_denied) when trying to connect Gmail, this means the OAuth consent screen is in testing or unverified and your Google account is not listed as a test user. To fix this quickly for development, either add your Google account as a test user or publish the app after verification.

Quick steps to add a test user (recommended for local development):

1. Open the Google Cloud Console: https://console.cloud.google.com/
2. Select the project that contains your OAuth 2.0 Client ID.
3. Navigate to APIs & Services -> OAuth consent screen.
4. Under "Test users", add the Google account(s) you will use to test the app.
5. Save changes and retry the OAuth flow in your app.

If you intend to provide the app to other users publicly, you'll need to submit the app for verification in the OAuth consent screen (this can take time and requires justification for sensitive scopes like Gmail). See Google documentation for the verification process.

Also checklist items to verify locally:

- Use exactly the same host and port as registered in `credentials.json` (e.g., use `http://localhost:5000` in your browser if `credentials.json` has `http://localhost:5000/oauth2callback`).
- If you use `127.0.0.1` or a tunneled URL (ngrok), add those exact redirect URIs to the OAuth client in the Cloud Console.
- For local development, you can set the environment variable to allow insecure transport (HTTP) for oauthlib:

```powershell
$env:OAUTHLIB_INSECURE_TRANSPORT = '1'
python .\app.py
```

If you'd like, I can add a small README note or automatically add `127.0.0.1` to your local `credentials.json` file (the file contains your client secret, so only modify it if you're comfortable storing it locally). Tell me which you'd prefer and I will proceed.
