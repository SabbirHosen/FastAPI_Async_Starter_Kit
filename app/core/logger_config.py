import logging
import shutil
from logging.handlers import TimedRotatingFileHandler, WatchedFileHandler
import smtplib
from email.message import EmailMessage
from datetime import datetime
from multiprocessing import Lock as ProcessLock
import threading
import os
import time
from collections import defaultdict
from typing import Dict

from app.core.config import settings

LOGGER_LEVEL = logging.DEBUG


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'ERROR': '\033[91m',
        'CRITICAL': '\033[91m',
        'WARNING': '\033[93m',
        'INFO': '\033[92m',
        'DEBUG': '\033[94m',
        'RESET': '\033[0m',
    }

    def format(self, record):
        log_msg = super().format(record)
        if record.levelname in self.COLORS:
            log_msg = f"{self.COLORS[record.levelname]}{log_msg}{self.COLORS['RESET']}"
        return log_msg


def send_email(content: str, subject: str) -> bool:
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = settings.EMAIL_RECEIVER

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=5) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        return False


class ProcessSafeCriticalHandler(logging.Handler):
    _process_lock = ProcessLock()

    def __init__(self, threshold: int = 5, window_hours: int = 1):
        super().__init__()
        self.threshold = threshold
        self.window_hours = window_hours
        self.function_logs = defaultdict(list)
        self.thread_lock = threading.RLock()

    def emit(self, record):
        if record.levelno != logging.CRITICAL:
            return

        try:
            with self._process_lock:
                with self.thread_lock:
                    self._handle_critical_log(record)
        except Exception as e:
            print(f"Error in critical handler: {e}")

    def _handle_critical_log(self, record):
        current_time = datetime.now()
        log_entry = {
            'time': current_time,
            'message': record.getMessage(),
            'process': record.processName,
            'thread': record.threadName
        }

        func_name = record.funcName
        self.function_logs[func_name].append(log_entry)

        # Clean old logs
        self.function_logs[func_name] = [
            log for log in self.function_logs[func_name]
            if (current_time - log['time']).total_seconds() <= self.window_hours * 3600
        ]

        if len(self.function_logs[func_name]) >= self.threshold:
            self._send_alert(func_name, self.function_logs[func_name])
            self.function_logs[func_name].clear()

    def _send_alert(self, function_name: str, logs: list):
        try:
            log_messages = "\n".join([
                f"{log['time'].strftime('%Y-%m-%d %H:%M:%S')} - Process:{log['process']} - Thread:{log['thread']}: {log['message']}"
                for log in logs
            ])

            content = f"""Alert: {len(logs)} critical logs from {function_name} in last {self.window_hours}h

Detailed Logs:
{log_messages}"""

            send_email(content, f'Critical Log Alert - {function_name} From FaceBookListingScrapper')
        except Exception as e:
            logging.error(f"Error sending alert: {e}")

    def close(self):
        """Properly close the handler"""
        try:
            self.function_logs.clear()
            super().close()
        except Exception as e:
            logging.error(f"Error closing critical handler: {e}")


class LogRotationManager:
    def __init__(self, log_dir: str, max_days: int = 7, rotation_interval: int = 24):
        """
        Initialize LogRotationManager.

        Args:
            log_dir: Base directory for logs
            max_days: Maximum days to keep logs
            rotation_interval: Hours between rotation checks
        """
        self.log_dir = log_dir
        self.max_days = max_days
        self.rotation_interval = rotation_interval * 3600  # Convert hours to seconds
        self.log_configs: Dict[str, dict] = {}
        self.running = True
        self._init_log_directory()
        self.start_rotation()

    def _init_log_directory(self):
        """Initialize the log directory structure."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Create archived directory
        self.archive_dir = os.path.join(self.log_dir, 'archived')
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def add_log_config(self, name: str, max_size_mb: int = 10, backup_count: int = 5):
        """
        Add configuration for a specific log file.

        Args:
            name: Name of the log file (without .log extension)
            max_size_mb: Maximum size of each log file in MB
            backup_count: Number of backup files to keep
        """
        self.log_configs[name] = {
            'filename': f"{name}.log",
            'max_size': max_size_mb * 1024 * 1024,  # Convert MB to bytes
            'backup_count': backup_count
        }

    def start_rotation(self):
        """Start the log rotation thread."""
        self.rotation_thread = threading.Thread(target=self._rotate_logs, daemon=True)
        self.rotation_thread.name = f"LogRotation-{threading.get_ident()}"
        self.rotation_thread.start()

    def stop_rotation(self):
        """Stop the log rotation thread."""
        self.running = False
        if self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=5)

    def _rotate_logs(self):
        """Main rotation loop."""
        while self.running:
            try:
                self._perform_rotation()
            except Exception as e:
                logging.error(f"Log rotation error: {e}")
            time.sleep(self.rotation_interval)

    def _perform_rotation(self):
        """Perform the actual log rotation."""
        current_time = time.time()

        # Handle configured log files
        for log_name, config in self.log_configs.items():
            self._rotate_single_log(log_name, config)

        # Clean up old archived logs
        self._cleanup_archived_logs(current_time)

    def _rotate_single_log(self, log_name: str, config: dict):
        """Rotate a single log file."""
        log_path = os.path.join(self.log_dir, config['filename'])
        if not os.path.exists(log_path):
            return

        try:
            # Check file size
            file_size = os.path.getsize(log_path)
            if file_size > config['max_size']:
                # Create timestamp for archive name
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"{log_name}_{timestamp}.log"
                archive_path = os.path.join(self.archive_dir, archive_name)

                # Move current log to archive
                shutil.move(log_path, archive_path)

                # Remove old archives if exceeding backup count
                self._cleanup_old_backups(log_name, config['backup_count'])

        except Exception as e:
            logging.error(f"Error rotating log {log_name}: {e}")

    def _cleanup_old_backups(self, log_name: str, backup_count: int):
        """Clean up old backup files exceeding the backup count."""
        try:
            # Get all backup files for this log
            backup_files = []
            for filename in os.listdir(self.archive_dir):
                if filename.startswith(log_name + '_') and filename.endswith('.log'):
                    filepath = os.path.join(self.archive_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))

            # Sort by creation time (oldest first)
            backup_files.sort(key=lambda x: x[1])

            # Remove excess backups
            while len(backup_files) > backup_count:
                filepath, _ = backup_files.pop(0)
                try:
                    os.remove(filepath)
                    logging.info(f"Removed old backup: {filepath}")
                except Exception as e:
                    logging.error(f"Failed to remove backup {filepath}: {e}")

        except Exception as e:
            logging.error(f"Error cleaning up backups for {log_name}: {e}")

    def _cleanup_archived_logs(self, current_time: float):
        """Remove archived logs older than max_days."""
        try:
            cutoff_time = current_time - (self.max_days * 86400)
            for filename in os.listdir(self.archive_dir):
                filepath = os.path.join(self.archive_dir, filename)
                if os.path.getctime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        logging.info(f"Removed old archived log: {filepath}")
                    except Exception as e:
                        logging.error(f"Failed to remove archived log {filepath}: {e}")

        except Exception as e:
            logging.error(f"Error cleaning up archived logs: {e}")


def get_logger(base_log_dir: str = settings.LOG_DIR) -> logging.Logger:
    try:
        logger = logging.getLogger(f'facebook.scrapper')
        logger.propagate = False
        if logger.handlers:
            return logger

        logger.setLevel(LOGGER_LEVEL)

        # Create log directory with proper permissions
        log_dir = os.path.join(base_log_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        os.chmod(log_dir, 0o777)

        # File handler
        # file_handler = WatchedFileHandler(
        #     )
        # )
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, f'app_{datetime.now().strftime("%Y_%m_%d")}.log'), when="midnight", interval=1, backupCount=7
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(processName)s - %(threadName)s - %(funcName)s - %(message)s'
        ))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(processName)s - %(threadName)s - %(funcName)s - %(message)s'
        ))

        # Critical handler
        critical_handler = ProcessSafeCriticalHandler(threshold=10, window_hours=1)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(critical_handler)

        def cleanup():
            """Cleanup function to properly close handlers"""
            for handler in logger.handlers[:]:
                try:
                    handler.close()
                    logger.removeHandler(handler)
                except Exception as e:
                    print(f"Error closing handler: {e}")

        # Register cleanup function
        import atexit
        atexit.register(cleanup)

        return logger

    except Exception as e:
        print(f"Logger initialization failed: {e}")
        return logging.getLogger()
