import paramiko
import logging

class RemoteAliasManager:
    def __init__(self, remote_os, host, username, password):
        self.remote_os = remote_os.lower()
        self.host = host
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try key-based authentication first
        try:
            self.client.connect(
                hostname=host,
                username=username,
                allow_agent=True,
                look_for_keys=True,
                timeout=10
            )
            logging.info("SSH connection established with %s using key-based authentication.", host)
        except Exception as key_exc:
            logging.warning("Key-based authentication failed for %s: %s", host, key_exc)
            # Fallback to password authentication if key-based fails
            try:
                self.client.connect(
                    hostname=host,
                    username=username,
                    password=password,
                    allow_agent=False,
                    look_for_keys=False,
                    timeout=10
                )
                logging.info("SSH connection established with %s using password authentication.", host)
            except Exception as pass_exc:
                logging.exception("Password authentication failed for %s", host)
                raise ConnectionError(
                    f"Failed to connect to {host} using both key-based and password authentication: {pass_exc}"
                )

    def create_alias(self, alias_name, command):
        if self.remote_os == "osx":
            # For OSX, append alias to ~/.bash_profile (adjust if using zsh)
            profile_path = "~/.bash_profile"
            alias_line = f"alias {alias_name}='{command}'"
            cmd = f'echo "{alias_line}" >> {profile_path}'
        elif self.remote_os == "windows":
            # For Windows, create a .bat file in C:\Windows\System32
            bat_file = f"C:\\Windows\\System32\\{alias_name}.bat"
            # Use PowerShell command to set the file content; note the newline represented by `n in PowerShell
            alias_content = f"@echo off`n{command}"
            cmd = f"powershell -Command \"Set-Content -Path '{bat_file}' -Value '{alias_content}'\""
        else:
            raise ValueError("Unsupported remote OS type. Use 'osx' or 'windows'.")

        stdin, stdout, stderr = self.client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.error("Failed to create alias on remote machine: %s", error)
            raise IOError(f"Failed to create alias on remote machine: {error}")
        logging.info("Added alias '%s' to remote machine on host %s.", alias_name, self.host)
        print(f"Added alias '{alias_name}' on remote machine ({self.remote_os}) at host {self.host}.")

    def __del__(self):
        if self.client:
            self.client.close()
            logging.info("SSH connection to %s closed.", self.host)