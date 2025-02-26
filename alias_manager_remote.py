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
        # Try key-based authentication first; if that fails, use password.
        try:
            self.client.connect(hostname=host, username=username,
                                allow_agent=True, look_for_keys=True, timeout=10)
            logging.info("SSH connection established with %s using key-based authentication.", host)
        except Exception as key_exc:
            logging.warning("Key-based authentication failed for %s: %s", host, key_exc)
            try:
                self.client.connect(hostname=host, username=username, password=password,
                                    allow_agent=False, look_for_keys=False, timeout=10)
                logging.info("SSH connection established with %s using password authentication.", host)
            except Exception as pass_exc:
                logging.exception("SSH connection failed for %s", host)
                raise ConnectionError(f"Failed to connect to {host}: {pass_exc}")

    def create_alias(self, alias_name, command):
        if self.remote_os == "osx":
            profile_path = "~/.bash_profile"
            alias_line = f"alias {alias_name}='{command}'"
            cmd = f'echo "{alias_line}" >> {profile_path}'
        elif self.remote_os == "windows":
            bat_file = f"C:\\Windows\\System32\\{alias_name}.bat"
            alias_content = f"@echo off`nREM AliasManager`n{command}"
            cmd = f"powershell -Command \"Set-Content -Path '{bat_file}' -Value '{alias_content}'\""
        else:
            raise ValueError("Unsupported remote OS type. Use 'osx' or 'windows'.")
        stdin, stdout, stderr = self.client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.error("Failed to create remote alias: %s", error)
            raise IOError(f"Failed to create remote alias: {error}")
        logging.info("Created remote alias '%s' on host %s.", alias_name, self.host)

    def list_aliases(self):
        aliases = {}
        if self.remote_os == "osx":
            profile_path = "~/.bash_profile"
            cmd = f"cat {profile_path}"
            stdin, stdout, stderr = self.client.exec_command(cmd)
            output = stdout.read().decode()
            err = stderr.read().decode().strip()
            if err:
                logging.error("Error listing remote aliases: %s", err)
                raise IOError(f"Error listing remote aliases: {err}")
            lines = output.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("alias "):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        alias_def = parts[0].strip()  # "alias name"
                        command_def = parts[1].strip().strip("'")
                        alias_key = alias_def[6:]
                        aliases[alias_key] = command_def
        elif self.remote_os == "windows":
            # List .bat files in System32 containing our marker.
            cmd = r"powershell -Command \"Get-ChildItem -Path 'C:\Windows\System32' -Filter '*.bat' | ForEach-Object { if (Get-Content $_.FullName | Select-String 'REM AliasManager') { Write-Output ($_.Name) } }\""
            stdin, stdout, stderr = self.client.exec_command(cmd)
            output = stdout.read().decode()
            err = stderr.read().decode().strip()
            if err:
                logging.error("Error listing remote aliases on Windows: %s", err)
                raise IOError(f"Error listing remote aliases: {err}")
            files = output.splitlines()
            for filename in files:
                if filename.endswith(".bat"):
                    alias_name = filename[:-4]
                    # Read the file content to get the command (assumed on line 3)
                    cmd_read = f"powershell -Command \"Get-Content -Path 'C:\\Windows\\System32\\{filename}'\""
                    stdin, stdout, stderr = self.client.exec_command(cmd_read)
                    content = stdout.read().decode().splitlines()
                    command_line = content[2] if len(content) >= 3 else ""
                    aliases[alias_name] = command_line
        else:
            raise ValueError("Unsupported remote OS type for listing aliases.")
        return aliases

    def update_alias(self, alias_name, new_command):
        if self.remote_os == "osx":
            profile_path = "~/.bash_profile"
            # Using sed to update the alias. For macOS, sed -i '' is required.
            cmd = f"sed -i '' 's/^alias {alias_name}=.*/alias {alias_name}=\\'{new_command}\\'/g' {profile_path}"
        elif self.remote_os == "windows":
            bat_file = f"C:\\Windows\\System32\\{alias_name}.bat"
            cmd = f"powershell -Command \"Set-Content -Path '{bat_file}' -Value '@echo off`nREM AliasManager`n{new_command}'\""
        else:
            raise ValueError("Unsupported remote OS type for updating alias.")
        stdin, stdout, stderr = self.client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.error("Error updating remote alias: %s", error)
            raise IOError(f"Error updating remote alias: {error}")
        logging.info("Updated remote alias '%s' on host %s.", alias_name, self.host)

    def delete_alias(self, alias_name):
        if self.remote_os == "osx":
            profile_path = "~/.bash_profile"
            cmd = f"sed -i '' '/^alias {alias_name}=/d' {profile_path}"
        elif self.remote_os == "windows":
            bat_file = f"C:\\Windows\\System32\\{alias_name}.bat"
            cmd = f"del /F /Q \"{bat_file}\""
        else:
            raise ValueError("Unsupported remote OS type for deleting alias.")
        stdin, stdout, stderr = self.client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            logging.error("Error deleting remote alias: %s", error)
            raise IOError(f"Error deleting remote alias: {error}")
        logging.info("Deleted remote alias '%s' on host %s.", alias_name, self.host)

    def __del__(self):
        if self.client:
            self.client.close()
            logging.info("SSH connection to %s closed.", self.host)