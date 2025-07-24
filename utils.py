"""
Utility functions for Telegram Channel Cloner
Contains helper functions for file operations, text processing, and calculations.
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = filename.strip('._')  # Remove leading/trailing dots and underscores
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename or 'unnamed_file'


def format_duration(duration: timedelta) -> str:
    """
    Format duration as human-readable string.
    
    Args:
        duration: Duration to format
        
    Returns:
        Formatted duration string
    """
    total_seconds = int(duration.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def calculate_eta(current: int, total: int, elapsed: timedelta) -> str:
    """
    Calculate estimated time of arrival.
    
    Args:
        current: Current progress
        total: Total items
        elapsed: Time elapsed so far
        
    Returns:
        ETA as formatted string
    """
    if current <= 0 or elapsed.total_seconds() <= 0:
        return "Unknown"
    
    rate = current / elapsed.total_seconds()
    remaining = total - current
    
    if rate <= 0:
        return "Unknown"
    
    eta_seconds = remaining / rate
    eta_duration = timedelta(seconds=int(eta_seconds))
    
    return format_duration(eta_duration)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size as human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    Clean text by removing excessive whitespace and control characters.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r'[ \t]+', ' ', text)     # Multiple spaces/tabs to single space
    
    return text.strip()


def save_json(data: Dict[Any, Any], filepath: str, indent: int = 2) -> bool:
    """
    Save data to JSON file safely.
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        # Write to temporary file first
        temp_filepath = f"{filepath}.tmp"
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        # Move temporary file to final location
        os.replace(temp_filepath, filepath)
        return True
    except Exception:
        # Clean up temporary file if it exists
        if os.path.exists(f"{filepath}.tmp"):
            try:
                os.remove(f"{filepath}.tmp")
            except:
                pass
        return False


def load_json(filepath: str) -> Optional[Dict[Any, Any]]:
    """
    Load data from JSON file safely.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data or None if failed
    """
    try:
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def get_message_type(message) -> str:
    """
    Determine the type of a Telegram message.
    
    Args:
        message: Telegram message object
        
    Returns:
        Message type as string
    """
    if message.text and not message.media:
        return "text"
    elif message.media:
        if hasattr(message.media, 'photo'):
            return "photo"
        elif hasattr(message.media, 'document'):
            if message.media.document.mime_type:
                if message.media.document.mime_type.startswith('video/'):
                    return "video"
                elif message.media.document.mime_type.startswith('audio/'):
                    return "audio"
                elif message.media.document.mime_type.startswith('image/'):
                    return "image"
                else:
                    return "document"
            return "document"
        else:
            return "media"
    else:
        return "empty"


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename with timestamp.
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup filename
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{path.stem}_{timestamp}{path.suffix}"


def validate_channel_username(username: str) -> bool:
    """
    Validate Telegram channel username format.
    
    Args:
        username: Channel username to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not username:
        return False
    
    # Remove @ if present
    clean_username = username.lstrip('@')
    
    # Check basic format: 5-32 characters, alphanumeric + underscores
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', clean_username):
        return False
    
    # Cannot end with underscore
    if clean_username.endswith('_'):
        return False
    
    # Cannot have consecutive underscores
    if '__' in clean_username:
        return False
    
    return True


def parse_channel_identifier(identifier: str) -> Optional[str]:
    """
    Parse and normalize channel identifier.
    
    Args:
        identifier: Channel identifier (username, invite link, ID, etc.)
        
    Returns:
        Normalized identifier or None if invalid
    """
    if not identifier:
        return None
    
    identifier = identifier.strip()
    
    # Handle numeric IDs (negative for channels/supergroups)
    if identifier.lstrip('-').isdigit():
        return int(identifier)
    
    # Handle t.me links
    if 't.me/' in identifier:
        parts = identifier.split('t.me/')
        if len(parts) > 1:
            identifier = parts[-1].split('?')[0]  # Remove query parameters
    
    # Handle +invite links
    if identifier.startswith('+'):
        return identifier
    
    # Add @ if not present and not an invite link
    if not identifier.startswith('@') and not identifier.startswith('+'):
        identifier = f"@{identifier}"
    
    return identifier if validate_channel_username(identifier) or identifier.startswith('+') else None


def is_channel_id(identifier) -> bool:
    """
    Check if identifier is a numeric channel ID.
    
    Args:
        identifier: Channel identifier to check
        
    Returns:
        True if it's a numeric ID, False otherwise
    """
    if isinstance(identifier, int):
        return True
    if isinstance(identifier, str):
        return identifier.lstrip('-').isdigit()
    return False
