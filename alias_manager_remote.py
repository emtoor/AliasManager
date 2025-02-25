import time
import paramiko
import logging

class RemoteAliasManager:
    def __init__(self, remote_os, host, username, password):
        self.remote_os = remote_os
        self.host = host
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname=host, username=username, password=password)
            logging.info("SSH connection established with %s.", host)
        except Exception as e:
            logging.exception("Failed to connect to %s", host)
            raise ConnectionError(f"Failed to connect to {host}: {e}")
        if remote_os == "osx":
            self.profile_path = "~/.bash_profile"  # Adjust if using zsh (e.g. "~/.zshrc")
            backup_cmd = f"if [ -f {self.profile_path} ]; then cp {self.profile_path} {self.profile_path}.bak.$(date +%Y%m%d%H%M%S); fi"
        elif remote_os == "windows":
            self.profile_path = r"$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
            backup_cmd = f"if (Test-Path {self.profile_path}) {{ Copy-Item {self.profile_path} {self.profile_path}.bak.$((Get-Date).ToString('yyyyMMddHHmmss')) }}"
        else:
            logging.error("Unsupported remote OS type: %s", remote_os)
            raise ValueError("Unsupported remote OS type. Use 'osx' or 'windows'.")
        stdin, stdout, stderr = self.client.exec_command(backup_cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.warning("Could not backup remote profile: %s", error)
            print(f"Warning: Could not backup remote profile: {error}")
    def create_alias(self, alias_name, command):
        if self.remote_os == "osx":
            alias_line = f"alias {alias_name}='{command}'"
            cmd = f'echo "{alias_line}" >> {self.profile_path}'
        else:
            alias_line = f"Set-Alias {alias_name} {command}"
            cmd = f'echo {alias_line} | Out-File -Append -FilePath {self.profile_path}'
        stdin, stdout, stderr = self.client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.error("Failed to create alias on remote machine: %s", error)
            raise IOError(f"Failed to create alias on remote machine: {error}")
        logging.info("Added alias '%s' to remote profile %s on host %s.", alias_name, self.profile_path, self.host)
        print(f"Added alias '{alias_name}' to remote profile {self.profile_path} on host {self.host}.")
    def __del__(self):
        if self.client:
            self.client.close()
            logging.info("SSH connection to %s closed.", self.host)
