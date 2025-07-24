"""
Gestion de configuration pour le Clonage de Chaînes Telegram
Gère les variables d'environnement et les paramètres de l'application.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for managing application settings."""
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize configuration from environment variables.
        
        Args:
            env_file: Path to the environment file
        """
        # Load environment variables from .env file
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Telegram API Configuration
        self.api_id: Optional[int] = self._get_int_env('TELEGRAM_API_ID')
        self.api_hash: Optional[str] = os.getenv('TELEGRAM_API_HASH')
        self.session_name: str = os.getenv('TELEGRAM_SESSION_NAME', 'telegram_cloner')
        
        # Bot Configuration (optionnel)
        self.bot_token: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
        self.use_bot_for_sending: bool = self._get_bool_env('USE_BOT_FOR_SENDING', False)
        
        # Rate Limiting Configuration
        self.rate_limit_delay: float = self._get_float_env('RATE_LIMIT_DELAY', 1.0)
        self.batch_size: int = self._get_int_env('BATCH_SIZE', 10) or 10
        self.max_retries: int = self._get_int_env('MAX_RETRIES', 3) or 3
        self.retry_delay: float = self._get_float_env('RETRY_DELAY', 5.0)
        
        # Logging Configuration
        self.log_file: str = os.getenv('LOG_FILE', 'telegram_cloner.log')
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        
        # Progress Tracking Configuration
        self.progress_file: str = os.getenv('PROGRESS_FILE', 'clone_progress.json')
        self.save_progress_interval: int = self._get_int_env('SAVE_PROGRESS_INTERVAL', 50) or 50
        
        # Media Configuration
        self.download_media: bool = self._get_bool_env('DOWNLOAD_MEDIA', True)
        self.media_timeout: int = self._get_int_env('MEDIA_TIMEOUT', 300) or 300
        
    def _get_int_env(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def _get_float_env(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, '').lower()
        return value in ('true', '1', 'yes', 'on')
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        if self.api_id is None:
            errors.append("TELEGRAM_API_ID is required")
        
        if not self.api_hash:
            errors.append("TELEGRAM_API_HASH is required")
        
        if self.use_bot_for_sending and not self.bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required when USE_BOT_FOR_SENDING is enabled")
        
        if self.rate_limit_delay < 0:
            errors.append("RATE_LIMIT_DELAY must be non-negative")
        
        if self.batch_size <= 0:
            errors.append("BATCH_SIZE must be positive")
        
        if self.max_retries < 0:
            errors.append("MAX_RETRIES must be non-negative")
        
        if self.retry_delay < 0:
            errors.append("RETRY_DELAY must be non-negative")
        
        if errors:
            print("Erreurs de configuration:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of configuration (without sensitive data)."""
        return f"""Configuration:
  Session Name: {self.session_name}
  Rate Limit Delay: {self.rate_limit_delay}s
  Batch Size: {self.batch_size}
  Max Retries: {self.max_retries}
  Retry Delay: {self.retry_delay}s
  Log File: {self.log_file}
  Log Level: {self.log_level}
  Progress File: {self.progress_file}
  Save Progress Interval: {self.save_progress_interval}
  Download Media: {self.download_media}
  Media Timeout: {self.media_timeout}s"""
