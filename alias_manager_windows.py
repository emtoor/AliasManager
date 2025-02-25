import os
import shutil
import logging

class WindowsAliasManager:
    def __init__(self):
        # Set the system32 directory where alias .bat files will be placed.
        self.system_dir = r"C:\Windows\System32"
        if not os.path.isdir(self.system_dir):
            raise IOError(f"System directory {self.system_dir} not found. Make sure you have administrative privileges.")

    def create_alias(self, alias_name, command):
        # Build the path for the .bat file
        bat_file = os.path.join(self.system_dir, f"{alias_name}.bat")
        
        # Backup existing file if it already exists
        if os.path.exists(bat_file):
            backup_file = bat_file + ".bak"
            try:
                shutil.copy2(bat_file, backup_file)
                logging.info("Backup of existing alias created at %s.", backup_file)
            except Exception as e:
                logging.warning("Could not backup existing alias file %s: %s", bat_file, e)
        
        # Write the command into the .bat file. The '@echo off' suppresses command echo.
        try:
            with open(bat_file, "w") as f:
                f.write(f"@echo off\n{command}\n")
            logging.info("Created alias '%s' as %s.", alias_name, bat_file)
            print(f"Alias '{alias_name}' created successfully at {bat_file}.")
        except Exception as e:
            logging.exception("Failed to create alias file %s", bat_file)
            raise IOError(f"Failed to create alias file {bat_file}: {e}")