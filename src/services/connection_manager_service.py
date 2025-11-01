from __future__ import annotations
import os
from time import sleep
from paramiko import SSHClient, AutoAddPolicy
from src.config.settings import Settings
from src.utils.logging_signal import logger


class ConnectionManagerService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ssh_client = None
        self.sftp_client = None

    def connect(self) -> bool:
        if self.ssh_client and self.sftp_client:
            return True

        logger.search(f"Connection: Checking: {self.settings.pi_ip}...")
        retries = 0

        while retries < 3:
            try:
                if not os.path.exists(self.settings.ssh_key_path):
                    logger.error(
                        f"Connection: SSH Key: Not Found: {self.settings.ssh_key_path}"
                    )
                    return False

                self.ssh_client = SSHClient()
                self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
                self.ssh_client.connect(
                    hostname=self.settings.pi_ip,
                    username=self.settings.pi_user,
                    key_filename=self.settings.ssh_key_path,
                    timeout=10,
                )
                self.sftp_client = self.ssh_client.open_sftp()
                logger.start(f"Connection: Start: {self.settings.pi_ip}")
                return True
            except Exception as e:
                logger.error(f"Connection: Failed: {e}")
                self.ssh_client = None
                self.sftp_client = None
                retries += 1
                sleep(3)
        return False

    def is_connected(self) -> bool:
        return self.ssh_client is not None and self.sftp_client is not None

    def close(self):
        """Close SSH + SFTP connections."""
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

        logger.stop("Connection: Stop\n")

    def test_connection(self):
        """Temporary connection just for testing."""
        test_ssh = SSHClient()
        test_ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            test_ssh.connect(
                hostname=self.settings.pi_ip,
                username=self.settings.pi_user,
                key_filename=self.settings.ssh_key_path,
                timeout=10,
            )
            return True
        except Exception as e:
            logger.error(f"Test connection failed: {e}")
            return False
        finally:
            test_ssh.close()
