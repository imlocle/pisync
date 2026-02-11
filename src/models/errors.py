"""
Custom exception hierarchy for PiSync application.

This module defines all custom exceptions used throughout the application,
providing clear error types for different failure scenarios.
"""

from typing import Optional


# ============================================================================
# Base Exceptions
# ============================================================================


class PiSyncError(Exception):
    """Base exception for all PiSync errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


# ============================================================================
# Connection Errors
# ============================================================================


class ConnectionError(PiSyncError):
    """Base exception for connection-related errors."""
    pass


class SSHConnectionError(ConnectionError):
    """Failed to establish SSH connection."""
    pass


class SFTPConnectionError(ConnectionError):
    """Failed to establish SFTP connection."""
    pass


class ConnectionTimeoutError(ConnectionError):
    """Connection attempt timed out."""
    pass


class ConnectionLostError(ConnectionError):
    """Active connection was lost unexpectedly."""
    pass


class AuthenticationError(ConnectionError):
    """SSH authentication failed."""
    pass


class HostKeyError(ConnectionError):
    """SSH host key verification failed."""
    pass


# ============================================================================
# Transfer Errors
# ============================================================================


class TransferError(PiSyncError):
    """Base exception for transfer operations."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        details: Optional[str] = None,
    ):
        self.file_path = file_path
        super().__init__(message, details)

    def __str__(self) -> str:
        base = super().__str__()
        if self.file_path:
            return f"{base}\nFile: {self.file_path}"
        return base


class RemoteDirectoryError(TransferError):
    """Failed to create or access remote directory."""
    pass


class FileUploadError(TransferError):
    """Failed to upload file to remote server."""
    pass


class FileDownloadError(TransferError):
    """Failed to download file from remote server."""
    pass


class TransferVerificationError(TransferError):
    """File transfer completed but verification failed."""
    pass


class InsufficientSpaceError(TransferError):
    """Insufficient disk space on target."""

    def __init__(
        self,
        message: str,
        required_bytes: Optional[int] = None,
        available_bytes: Optional[int] = None,
        details: Optional[str] = None,
    ):
        self.required_bytes = required_bytes
        self.available_bytes = available_bytes
        super().__init__(message, details=details)


class TransferCancelledError(TransferError):
    """Transfer was cancelled by user."""
    pass


# ============================================================================
# Configuration Errors
# ============================================================================


class ConfigurationError(PiSyncError):
    """Base exception for configuration-related errors."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Configuration validation failed."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[str] = None):
        self.field = field
        super().__init__(message, details)

    def __str__(self) -> str:
        base = super().__str__()
        if self.field:
            return f"{base}\nField: {self.field}"
        return base


class ConfigurationLoadError(ConfigurationError):
    """Failed to load configuration file."""
    pass


class ConfigurationSaveError(ConfigurationError):
    """Failed to save configuration file."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing."""
    pass


# ============================================================================
# File System Errors
# ============================================================================


class FileSystemError(PiSyncError):
    """Base exception for file system operations."""

    def __init__(self, message: str, path: Optional[str] = None, details: Optional[str] = None):
        self.path = path
        super().__init__(message, details)

    def __str__(self) -> str:
        base = super().__str__()
        if self.path:
            return f"{base}\nPath: {self.path}"
        return base


class FileNotFoundError(FileSystemError):
    """File or directory not found."""
    pass


class FileAccessError(FileSystemError):
    """Permission denied or file access error."""
    pass


class FileDeletionError(FileSystemError):
    """Failed to delete file or directory."""
    pass


class FileMonitorError(FileSystemError):
    """File monitoring/watchdog error."""
    pass


class FileStabilityError(FileSystemError):
    """File is still being written or modified."""
    pass


# ============================================================================
# Classification Errors
# ============================================================================


class ClassificationError(PiSyncError):
    """Base exception for file classification errors."""
    pass


class UnknownFileTypeError(ClassificationError):
    """Unable to determine file type (movie/TV)."""
    pass


class InvalidFileExtensionError(ClassificationError):
    """File extension not in allowed list."""
    pass


# ============================================================================
# Validation Errors
# ============================================================================


class ValidationError(PiSyncError):
    """Base exception for validation errors."""
    pass


class IPAddressValidationError(ValidationError):
    """Invalid IP address format."""
    pass


class PathValidationError(ValidationError):
    """Invalid path format or structure."""
    pass


class SSHKeyValidationError(ValidationError):
    """SSH key file invalid or inaccessible."""
    pass


# ============================================================================
# Operation Errors
# ============================================================================


class OperationError(PiSyncError):
    """Base exception for general operation errors."""
    pass


class OperationInProgressError(OperationError):
    """Cannot start operation while another is in progress."""
    pass


class OperationCancelledError(OperationError):
    """Operation was cancelled by user."""
    pass


class OperationTimeoutError(OperationError):
    """Operation exceeded timeout limit."""
    pass