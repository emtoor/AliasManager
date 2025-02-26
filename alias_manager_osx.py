import os
import shutil
import logging

class OSXAliasManager:
    def __init__(self):
        shell = os.environ.get("SHELL", "")
        # Choose appropriate profile file based on shell (defaulting to bash)
        if "zsh" in shell:
            self.profile_path = os.path.expanduser("~/.zshrc")
        else:
            self.profile_path = os.path.expanduser("~/.bash_profile")
        # Ensure the profile exists
        if not os.path.exists(self.profile_path):
            try:
                open(self.profile_path, "a").close()
            except Exception as e:
                logging.exception("Could not create profile file: %s", self.profile_path)
                raise IOError(f"Could not create profile file: {self.profile_path}. Error: {e}")
        # Backup the profile
        try:
            backup_path = self.profile_path + ".bak"
            shutil.copy2(self.profile_path, backup_path)
            logging.info("Backup of profile created at %s.", backup_path)
        except Exception as e:
            logging.warning("Could not backup profile file: %s. Error: %s", self.profile_path, e)

    def create_alias(self, alias_name, command):
        alias_line = f"alias {alias_name}='{command}'\n"
        try:
            with open(self.profile_path, "a") as f:
                f.write(alias_line)
        except Exception as e:
            logging.exception("Failed to write alias to %s", self.profile_path)
            raise IOError(f"Failed to write alias to {self.profile_path}: {e}")
        logging.info("Added alias '%s' to %s.", alias_name, self.profile_path)
        print(f"Added alias '{alias_name}' to {self.profile_path}.")

    def list_aliases(self):
        aliases = {}
        try:
            with open(self.profile_path, "r") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("alias "):
                    # Expected format: alias name='command'
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        alias_def = parts[0].strip()  # e.g., "alias ll"
                        command_def = parts[1].strip().strip("'")
                        alias_key = alias_def[6:]  # Remove 'alias ' prefix
                        aliases[alias_key] = command_def
        except Exception as e:
            logging.exception("Error listing aliases from %s", self.profile_path)
            raise IOError(f"Error listing aliases: {e}")
        return aliases

    def update_alias(self, alias_name, new_command):
        updated = False
        try:
            with open(self.profile_path, "r") as f:
                lines = f.readlines()
            with open(self.profile_path, "w") as f:
                for line in lines:
                    if line.startswith(f"alias {alias_name}="):
                        f.write(f"alias {alias_name}='{new_command}'\n")
                        updated = True
                    else:
                        f.write(line)
            if not updated:
                raise ValueError(f"Alias '{alias_name}' not found")
        except Exception as e:
            logging.exception("Error updating alias %s", alias_name)
            raise IOError(f"Error updating alias {alias_name}: {e}")
        logging.info("Updated alias '%s' in %s.", alias_name, self.profile_path)

    def delete_alias(self, alias_name):
        found = False
        try:
            with open(self.profile_path, "r") as f:
                lines = f.readlines()
            with open(self.profile_path, "w") as f:
                for line in lines:
                    if line.startswith(f"alias {alias_name}="):
                        found = True
                        continue  # Skip the alias line
                    f.write(line)
            if not found:
                raise ValueError(f"Alias '{alias_name}' not found")
        except Exception as e:
            logging.exception("Error deleting alias %s", alias_name)
            raise IOError(f"Error deleting alias {alias_name}: {e}")
        logging.info("Deleted alias '%s' from %s.", alias_name, self.profile_path)