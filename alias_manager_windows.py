import os
import shutil
import logging

class WindowsAliasManager:
    def __init__(self):
        profile_dir = os.path.join(os.environ["USERPROFILE"], "Documents", "WindowsPowerShell")
        try:
            os.makedirs(profile_dir, exist_ok=True)
        except Exception as e:
            logging.exception("Could not create profile directory: %s", profile_dir)
            raise IOError(f"Could not create profile directory: {profile_dir}. Error: {e}")
        self.profile_path = os.path.join(profile_dir, "Microsoft.PowerShell_profile.ps1")
        if not os.path.exists(self.profile_path):
            try:
                open(self.profile_path, "a").close()
            except Exception as e:
                logging.exception("Could not create profile file: %s", self.profile_path)
                raise IOError(f"Could not create profile file: {self.profile_path}. Error: {e}")
        try:
            backup_path = self.profile_path + ".bak"
            shutil.copy2(self.profile_path, backup_path)
            logging.info("Backup of profile created at %s.", backup_path)
        except Exception as e:
            logging.warning("Could not backup profile file: %s. Error: %s", self.profile_path, e)
    def create_alias(self, alias_name, command):
        alias_line = f"Set-Alias {alias_name} {command}\n"
        try:
            with open(self.profile_path, "a") as f:
                f.write(alias_line)
        except Exception as e:
            logging.exception("Failed to write alias to %s", self.profile_path)
            raise IOError(f"Failed to write alias to {self.profile_path}: {e}")
        logging.info("Added alias '%s' to %s.", alias_name, self.profile_path)
        print(f"Added alias '{alias_name}' to {self.profile_path}.")
