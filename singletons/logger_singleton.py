"""
Logger Singleton for Connectly API.
Provides centralized logging functionality across the application.
"""

import logging
import os
import re
from datetime import datetime
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from log records."""

    REDACTION_PATTERNS = [
        (re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(Authorization[:\s]+Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(access_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(refresh_token["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(api[_-]?key["\s:=]+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(password["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(secret["\s:=]+)[^\s,}"\']+', re.IGNORECASE), r'\1[REDACTED]'),
    ]

    def filter(self, record):
        if hasattr(record, 'msg'):
            message = str(record.msg)
            for pattern, replacement in self.REDACTION_PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message

        if hasattr(record, 'args') and record.args:
            args = list(record.args) if isinstance(record.args, tuple) else [record.args]
            redacted_args = []
            for arg in args:
                arg_str = str(arg)
                for pattern, replacement in self.REDACTION_PATTERNS:
                    arg_str = pattern.sub(replacement, arg_str)
                redacted_args.append(arg_str)
            record.args = tuple(redacted_args)

        return True


class LoggerSingleton:
    _instance = None
    _initialized = False

    def __new__(cls) -> 'LoggerSingleton':
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._initialize()
            LoggerSingleton._initialized = True

    def _initialize(self) -> None:
        """Initialize the logger with proper configuration."""
        self.logger = logging.getLogger("connectly_logger")
        self.logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Create sensitive data filter
        sensitive_filter = SensitiveDataFilter()

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(sensitive_filter)

        # Create file handler
        file_handler = logging.FileHandler(
            f'logs/connectly_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(sensitive_filter)

        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            The configured logger instance
        """
        return self.logger

    @classmethod
    def get_instance(cls) -> 'LoggerSingleton':
        """
        Get the singleton instance.
        
        Returns:
            The singleton logger instance
        """
        if not cls._instance:
            cls._instance = LoggerSingleton()
        return cls._instance 