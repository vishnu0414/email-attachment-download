"""Gmail API utility functions."""

import os
import re
import math
from datetime import datetime, timedelta

def clean_filename(filename):
    """Clean filename for safe filesystem storage."""
    if not filename:
        return 'untitled'

    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\|?*]', '_', filename)
    filename = re.sub(r'\s+', ' ', filename)  # Replace multiple spaces with single space
    filename = filename.strip()

    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'

    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_icon(filetype):
    """Get Bootstrap icon class for file type."""
    icon_map = {
        'pdf': 'bi-file-earmark-pdf',
        'doc': 'bi-file-earmark-word',
        'docx': 'bi-file-earmark-word',
        'xls': 'bi-file-earmark-excel',
        'xlsx': 'bi-file-earmark-excel',
        'ppt': 'bi-file-earmark-ppt',
        'pptx': 'bi-file-earmark-ppt',
        'txt': 'bi-file-earmark-text',
        'jpg': 'bi-file-earmark-image',
        'jpeg': 'bi-file-earmark-image',
        'png': 'bi-file-earmark-image',
        'gif': 'bi-file-earmark-image',
        'zip': 'bi-file-earmark-zip',
        'rar': 'bi-file-earmark-zip',
        '7z': 'bi-file-earmark-zip',
        'mp3': 'bi-file-earmark-music',
        'mp4': 'bi-file-earmark-play',
        'avi': 'bi-file-earmark-play',
    }
    return icon_map.get(filetype.lower(), 'bi-file-earmark')

def build_search_query(sender=None, subject=None, date_after=None, 
                       date_before=None, has_attachment=True, filename_contains=None):
    """Build Gmail search query with multiple criteria."""
    query_parts = []

    if has_attachment:
        query_parts.append('has:attachment')

    if sender:
        query_parts.append(f'from:{sender}')

    if subject:
        query_parts.append(f'subject:"{subject}"')

    if date_after:
        if isinstance(date_after, datetime):
            date_after = date_after.strftime('%Y/%m/%d')
        query_parts.append(f'after:{date_after}')

    if date_before:
        if isinstance(date_before, datetime):
            date_before = date_before.strftime('%Y/%m/%d')
        query_parts.append(f'before:{date_before}')

    if filename_contains:
        query_parts.append(f'filename:{filename_contains}')

    return ' '.join(query_parts)

def parse_email_date(date_string):
    """Parse email date string to datetime object."""
    import email.utils
    try:
        date_tuple = email.utils.parsedate_tz(date_string)
        if date_tuple:
            timestamp = email.utils.mktime_tz(date_tuple)
            return datetime.utcfromtimestamp(timestamp)
    except:
        pass
    return None

def extract_email_address(email_string):
    """Extract email address from 'Name <email@domain.com>' format."""
    match = re.search(r'<([^>]+)>', email_string)
    if match:
        return match.group(1)
    return email_string

def get_search_filters():
    """Get predefined search filters."""
    return {
        'all': 'has:attachment',
        'today': f'has:attachment newer_than:{datetime.now().strftime("%Y/%m/%d")}',
        'week': 'has:attachment newer_than:7d',
        'month': 'has:attachment newer_than:30d',
        'pdf': 'has:attachment filename:pdf',
        'images': 'has:attachment filename:(jpg OR png OR gif)',
        'documents': 'has:attachment filename:(doc OR docx OR xls OR xlsx OR ppt OR pptx)',
        'large': 'has:attachment larger:5M'
    }
