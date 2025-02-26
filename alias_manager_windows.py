import os
import shutil
import logging

class WindowsAliasManager:
    def __init__(self):
        # We'll use System32 to store our alias batch files.
        self.system_dir = r"C:\Windows\System32"
        if not os.path.isdir(self.system_dir):
            raise IOError(f"System directory {self.system_dir} not found. Ensure you have administrative privileges.")

    def create_alias(self, alias_name, command):
        bat_file = os.path.join(self.system_dir, f"{alias_name}.bat")
        # Backup existing file if present.
        if os.path.exists(bat_file):
            backup_file = bat_file + ".bak"
            try:
                shutil.copy2(bat_file, backup_file)
                logging.info("Backup created for %s at %s.", bat_file, backup_file)
            except Exception as e:
                logging.warning("Could not backup %s: %s", bat_file, e)
        try:
            with open(bat_file, "w") as f:
                f.write("@echo off\n")
                f.write("REM AliasManager\n")  # Marker to identify our alias files.
                f.write(f"{command}\n")
            logging.info("Created alias '%s' as %s.", alias_name, bat_file)
            print(f"Alias '{alias_name}' created at {bat_file}.")
        except Exception as e:
            logging.exception("Failed to create alias file %s", bat_file)
            raise IOError(f"Failed to create alias file {bat_file}: {e}")

    def list_aliases(self):
        aliases = {}
        try:
            for filename in os.listdir(self.system_dir):
                if filename.endswith(".bat"):
                    file_path = os.path.join(self.system_dir, filename)
                    with open(file_path, "r") as f:
                        content = f.read()
                    if "REM AliasManager" in content:
                        alias_name = os.path.splitext(filename)[0]
                        # Assume command is on the third line.
                        lines = content.splitlines()
                        command_line = lines[2] if len(lines) >= 3 else ""
                        aliases[alias_name] = command_line
        except Exception as e:
            logging.exception("Error listing aliases in %s", self.system_dir)
            raise IOError(f"Error listing aliases: {e}")
        return aliases

    def update_alias(self, alias_name, new_command):
        bat_file = os.path.join(self.system_dir, f"{alias_name}.bat")
        if not os.path.exists(bat_file):
            raise ValueError(f"Alias '{alias_name}' not found")
        try:
            with open(bat_file, "w") as f:
                f.write("@echo off\n")
                f.write("REM AliasManager\n")
                f.write(f"{new_command}\n")
        except Exception as e:
            logging.exception("Error updating alias file %s", bat_file)
            raise IOError(f"Error updating alias {alias_name}: {e}")
        logging.info("Updated alias '%s' in %s.", alias_name, bat_file)

    def delete_alias(self, alias_name):
        bat_file = os.path.join(self.system_dir, f"{alias_name}.bat")
        if not os.path.exists(bat_file):
            raise ValueError(f"Alias '{alias_name}' not found")
        try:
            os.remove(bat_file)
        except Exception as e:
            logging.exception("Error deleting alias file %s", bat_file)
            raise IOError(f"Error deleting alias {alias_name}: {e}")
        logging.info("Deleted alias '%s' from %s.", alias_name, bat_file)