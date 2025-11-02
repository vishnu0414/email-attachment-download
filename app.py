#!/usr/bin/env python3
"""
Gmail Attachment Downloader - Main Flask Application
A modern Flask web application for downloading Gmail attachments with OAuth2 integration.
"""

import os
import base64
import zipfile as zf
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import tempfile

from config import Config
from models import db, User, Attachment
from gmail_oauth import GmailAPI
from gmail_utils import clean_filename, format_file_size

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Changed from 'auth.login' to match actual route
login_manager.login_message = 'Please log in to access this page.'

# Initialize Gmail API using configured credential/token file names
gmail_api = GmailAPI(
    credentials_file=app.config.get('GMAIL_CREDENTIALS_FILE', 'credentials.json'),
    token_file=app.config.get('GMAIL_TOKEN_FILE', 'token.pickle')
)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.before_request
def create_tables():
    """Create database tables on first request."""
    if not hasattr(app, 'tables_created'):
        os.makedirs(app.config['ATTACHMENT_FOLDER'], exist_ok=True)
        db.create_all()
        app.tables_created = True

# Routes
@app.route('/')
def index():
    """Homepage with feature overview."""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('signup.html')

        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'warning')
            return redirect(url_for('login'))

        # Create user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=password_hash)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'danger')
            app.logger.error(f"Signup error: {e}")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication."""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/disconnect_gmail')
@login_required
def disconnect_gmail():
    """Disconnect Gmail authentication."""
    try:
        # Revoke OAuth token
        if gmail_api.creds:
            revoke_success = gmail_api.revoke_token()
            if not revoke_success:
                app.logger.warning("Failed to revoke Gmail OAuth token")

        # Delete token file
        token_file = app.config.get('GMAIL_TOKEN_FILE', 'token.pickle')
        if os.path.exists(token_file):
            try:
                os.remove(token_file)
            except OSError as e:
                app.logger.error(f"Failed to delete token file: {e}")

        # Delete all user attachments
        attachments = Attachment.query.filter_by(user_id=current_user.id).all()
        deleted_files = 0
        for attachment in attachments:
            if os.path.exists(attachment.filepath):
                try:
                    os.remove(attachment.filepath)
                    deleted_files += 1
                except OSError:
                    pass  # Continue even if file deletion fails

        # Delete user directory if empty
        user_folder = os.path.join(app.config['ATTACHMENT_FOLDER'], str(current_user.id))
        try:
            if os.path.exists(user_folder):
                os.rmdir(user_folder)
        except OSError:
            pass  # Directory not empty or doesn't exist

        # Remove attachments from database
        for attachment in attachments:
            db.session.delete(attachment)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error during disconnect: {e}")

        # Clear session
        session.pop('gmail_authenticated', None)

        flash(f'Gmail account disconnected successfully. Removed {len(attachments)} attachments and {deleted_files} files.', 'success')

    except Exception as e:
        app.logger.error(f"Error during Gmail disconnect: {e}")
        flash('An error occurred while disconnecting Gmail. Please try again.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete user account."""
    if request.method == 'POST':
        # Delete all attachments and their files
        attachments = Attachment.query.filter_by(user_id=current_user.id).all()
        for attachment in attachments:
            if os.path.exists(attachment.filepath):
                try:
                    os.remove(attachment.filepath)
                except OSError:
                    pass  # Continue even if file deletion fails

        # Delete user directory if empty
        user_folder = os.path.join(app.config['ATTACHMENT_FOLDER'], str(current_user.id))
        try:
            if os.path.exists(user_folder):
                os.rmdir(user_folder)
        except OSError:
            pass  # Directory not empty or doesn't exist

        # Delete user from database
        db.session.delete(current_user)
        db.session.commit()

        # Clear session and logout
        logout_user()
        session.clear()

        flash('Your account has been deleted successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('delete_account.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics and recent attachments."""
    recent_attachments = Attachment.query.filter_by(
        user_id=current_user.id
    ).order_by(Attachment.created_at.desc()).limit(5).all()

    total_attachments = Attachment.query.filter_by(user_id=current_user.id).count()
    total_size = db.session.query(db.func.sum(Attachment.size)).filter_by(user_id=current_user.id).scalar() or 0

    stats = {
        'total_attachments': total_attachments,
        'total_size': format_file_size(total_size),
        'recent_count': len(recent_attachments),
        'gmail_connected': session.get('gmail_authenticated', False)
    }

    return render_template('dashboard.html', 
                         recent_attachments=recent_attachments, 
                         stats=stats)


@app.route('/analytics')
@login_required
def analytics():
    """Analytics view showing charts for attachment categories."""
    # The template will fetch `/api/chart_data` to render charts client-side
    return render_template('analytics.html')

@app.route('/gmail_auth')
@login_required
def gmail_auth():
    """Initiate Gmail OAuth2 authentication using web OAuth flow.

    It generates an authorization URL and redirects the user to Google. The
    callback will be handled at `/oauth2callback` where we exchange the code
    for tokens.
    """
    try:
        redirect_uri = url_for('oauth2callback', _external=True)
        auth_url, state = gmail_api.get_authorization_url(redirect_uri)
        # Persist state for verification during callback
        session['oauth_state'] = state
        return redirect(auth_url)
    except FileNotFoundError:
        flash('Gmail credentials not found. Please check your setup.', 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Gmail authentication failed: {str(e)}', 'danger')
        app.logger.error(f"Gmail auth error: {e}")
        return redirect(url_for('dashboard'))


@app.route('/oauth2callback')
@login_required
def oauth2callback():
    """OAuth2 callback endpoint - exchange code for tokens and save credentials."""
    state = session.get('oauth_state')
    redirect_uri = url_for('oauth2callback', _external=True)

    try:
        # request.url contains the full redirect URL including code and state
        gmail_api.fetch_token(request.url, state, redirect_uri)
        session['gmail_authenticated'] = True
        flash('Successfully connected to Gmail API!', 'success')
        return redirect(url_for('gmail_connect'))
    except Exception as e:
        flash(f'Gmail authentication failed: {str(e)}', 'danger')
        app.logger.error(f"Gmail callback error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/gmail_connect', methods=['GET', 'POST'])
@login_required
def gmail_connect():
    """Gmail connection and attachment download."""
    if request.method == 'POST':
        query = request.form.get('query', 'has:attachment').strip()
        max_results = int(request.form.get('max_results', 50))
        date_filter = request.form.get('date_filter', '').strip()

        # Build search query
        search_query = query
        if date_filter:
            # Convert YYYY-MM-DD to YYYY/MM/DD for Gmail API
            date_formatted = date_filter.replace('-', '/')
            search_query += f' after:{date_formatted}'

        try:
            # Search for messages with attachments
            messages = gmail_api.search_messages_with_attachments(
                query=search_query, 
                max_results=max_results
            )

            if not messages:
                flash('No emails found matching your search criteria.', 'info')
                return render_template('gmail_connect.html')

            downloaded_count = 0
            errors = []

            for message in messages:
                try:
                    message_id = message['id']

                    # Get message details
                    message_details = gmail_api.get_message_details(message_id)
                    if not message_details:
                        continue

                    # Extract headers
                    headers = gmail_api.get_message_headers(message_details)
                    subject = headers.get('subject', 'No Subject')
                    sender = headers.get('from', 'Unknown Sender')
                    date_str = headers.get('date', '')

                    # Parse date
                    date_received = None
                    if date_str:
                        try:
                            import email.utils
                            date_tuple = email.utils.parsedate_tz(date_str)
                            if date_tuple:
                                ts = email.utils.mktime_tz(date_tuple)
                                date_received = datetime.utcfromtimestamp(ts)
                        except Exception:
                            pass

                    # Get attachments
                    attachments = gmail_api.get_attachments(message_id)

                    for attachment_data in attachments:
                        filename = clean_filename(attachment_data['filename'])
                        file_size = attachment_data.get('size', 0)

                        # Create user-specific folder
                        user_folder = os.path.join(
                            app.config['ATTACHMENT_FOLDER'], 
                            str(current_user.id)
                        )
                        os.makedirs(user_folder, exist_ok=True)

                        # Generate unique filename
                        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                        safe_filename = f"{timestamp}_{filename}"
                        file_path = os.path.join(user_folder, safe_filename)

                        # Download attachment
                        if gmail_api.download_attachment(attachment_data, file_path):
                            # Save to database
                            attachment = Attachment(
                                user_id=current_user.id,
                                email_from=sender,
                                subject=subject,
                                filename=filename,
                                filepath=file_path,
                                filetype=os.path.splitext(filename)[1].lower().lstrip('.') or 'unknown',
                                size=file_size,
                                date_received=date_received
                            )
                            db.session.add(attachment)
                            downloaded_count += 1
                        else:
                            errors.append(f"Failed to download: {filename}")

                except Exception as e:
                    errors.append(f"Error processing message: {str(e)}")
                    continue

            try:
                db.session.commit()
                if downloaded_count > 0:
                    flash(f'Successfully downloaded {downloaded_count} attachments!', 'success')
                else:
                    flash('No attachments were downloaded.', 'warning')

                if errors:
                    flash(f'{len(errors)} errors occurred during download.', 'warning')

                return redirect(url_for('history'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error saving attachments: {str(e)}', 'danger')
                app.logger.error(f"Database error: {e}")

        except Exception as e:
            flash(f'Error downloading attachments: {str(e)}', 'danger')
            app.logger.error(f"Gmail download error: {e}")

    return render_template('gmail_connect.html')

@app.route('/history')
@login_required
def history():
    """Download history with search and filtering."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    file_type = request.args.get('type', '').strip()

    query = Attachment.query.filter_by(user_id=current_user.id)

    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Attachment.filename.contains(search),
                Attachment.subject.contains(search),
                Attachment.email_from.contains(search)
            )
        )

    if file_type:
        query = query.filter(Attachment.filetype == file_type)

    attachments = query.order_by(Attachment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # Get file types for filter dropdown
    file_types = db.session.query(Attachment.filetype).filter_by(
        user_id=current_user.id
    ).distinct().all()
    file_types = [ft[0] for ft in file_types if ft[0]]

    return render_template('history.html', 
                         attachments=attachments, 
                         file_types=file_types,
                         search=search,
                         current_type=file_type)

@app.route('/download/<int:attach_id>')
@login_required
def download(attach_id):
    """Download specific attachment."""
    attachment = Attachment.query.get_or_404(attach_id)

    if attachment.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('history'))

    if not os.path.exists(attachment.filepath):
        flash('File not found on server.', 'danger')
        return redirect(url_for('history'))

    try:
        return send_file(attachment.filepath,
                        as_attachment=True,
                        download_name=attachment.filename)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        app.logger.error(f"Download error: {e}")
        return redirect(url_for('history'))

@app.route('/preview/<int:attach_id>')
@login_required
def preview(attach_id):
    """Preview attachment inline in browser."""
    attachment = Attachment.query.get_or_404(attach_id)

    if attachment.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('history'))

    if not os.path.exists(attachment.filepath):
        flash('File not found on server.', 'danger')
        return redirect(url_for('history'))

    # Optional: Restrict preview to safe file types for security
    safe_types = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'pdf', 'txt'}
    if attachment.filetype.lower() not in safe_types:
        flash('Preview not available for this file type.', 'warning')
        return redirect(url_for('history'))

    try:
        return send_file(attachment.filepath,
                        as_attachment=False)
    except Exception as e:
        flash(f'Error previewing file: {str(e)}', 'danger')
        app.logger.error(f"Preview error: {e}")
        return redirect(url_for('history'))

@app.route('/download_zip')
@login_required
def download_zip():
    """Download all attachments as ZIP file."""
    attachments = Attachment.query.filter_by(user_id=current_user.id).all()

    if not attachments:
        flash('No attachments to download.', 'warning')
        return redirect(url_for('history'))

    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

    try:
        with zf.ZipFile(temp_zip.name, 'w', zf.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                if os.path.exists(attachment.filepath):
                    # Use original filename in ZIP
                    zip_file.write(attachment.filepath, attachment.filename)

        # Generate download filename
        download_name = f"gmail_attachments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        return send_file(temp_zip.name, 
                        as_attachment=True, 
                        download_name=download_name,
                        mimetype='application/zip')

    except Exception as e:
        flash(f'Error creating ZIP file: {str(e)}', 'danger')
        app.logger.error(f"ZIP creation error: {e}")
        return redirect(url_for('history'))
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_zip.name)
        except:
            pass

@app.route('/delete/<int:attach_id>', methods=['POST'])
@login_required
def delete(attach_id):
    """Delete attachment."""
    attachment = Attachment.query.get_or_404(attach_id)

    if attachment.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('history'))

    try:
        # Remove file from disk
        if os.path.exists(attachment.filepath):
            os.remove(attachment.filepath)

        # Remove from database
        db.session.delete(attachment)
        db.session.commit()

        flash('Attachment deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting attachment: {str(e)}', 'danger')
        app.logger.error(f"Delete error: {e}")

    return redirect(url_for('history'))

# API Routes
@app.route('/api/gmail/status')
@login_required
def api_gmail_status():
    """Check Gmail API authentication status."""
    authenticated = session.get('gmail_authenticated', False)
    return jsonify({'authenticated': authenticated})

@app.route('/api/stats')
@login_required
def api_stats():
    """Get user statistics."""
    total_attachments = Attachment.query.filter_by(user_id=current_user.id).count()
    recent_count = Attachment.query.filter_by(user_id=current_user.id).filter(
        Attachment.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()

    return jsonify({
        'total': total_attachments,
        'recent': recent_count,
        'gmail_connected': session.get('gmail_authenticated', False)
    })

@app.route('/api/chart_data')
@login_required
def api_chart_data():
    """Get chart data for dashboard."""
    try:
        # File type distribution
        file_types = db.session.query(
            Attachment.filetype,
            db.func.count(Attachment.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(Attachment.filetype).all()

        file_type_labels = []
        file_type_data = []
        for ft, count in file_types:
            file_type_labels.append(ft.upper() if ft else 'UNKNOWN')
            file_type_data.append(count)

        # Download trends (last 7 days)
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        daily_downloads = db.session.query(
            db.func.date(Attachment.created_at).label('date'),
            db.func.count(Attachment.id).label('count')
        ).filter(
            Attachment.user_id == current_user.id,
            Attachment.created_at >= start_date,
            Attachment.created_at <= end_date
        ).group_by(db.func.date(Attachment.created_at)).order_by(db.func.date(Attachment.created_at)).all()

        trend_labels = []
        trend_data = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            trend_labels.append(current_date.strftime('%b %d'))
            count = next((item[1] for item in daily_downloads if item[0] == current_date), 0)
            trend_data.append(count)
            current_date += timedelta(days=1)

        # Size distribution
        size_ranges = [
            ('0-1MB', 0, 1024*1024),
            ('1-10MB', 1024*1024, 10*1024*1024),
            ('10-50MB', 10*1024*1024, 50*1024*1024),
            ('50MB+', 50*1024*1024, float('inf'))
        ]

        size_labels = []
        size_data = []
        for label, min_size, max_size in size_ranges:
            if max_size == float('inf'):
                count = Attachment.query.filter(
                    Attachment.user_id == current_user.id,
                    Attachment.size >= min_size
                ).count()
            else:
                count = Attachment.query.filter(
                    Attachment.user_id == current_user.id,
                    Attachment.size >= min_size,
                    Attachment.size < max_size
                ).count()
            size_labels.append(label)
            size_data.append(count)

        return jsonify({
            'file_types': {
                'labels': file_type_labels,
                'data': file_type_data
            },
            'download_trends': {
                'labels': trend_labels,
                'data': trend_data
            },
            'size_distribution': {
                'labels': size_labels,
                'data': size_data
            }
        })
    except Exception as e:
        app.logger.error(f"Chart data error: {e}")
        return jsonify({'error': 'Failed to load chart data'}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'database': db_status,
        'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0] if '://' in app.config['SQLALCHEMY_DATABASE_URI'] else 'unknown'
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=port, debug=debug)
