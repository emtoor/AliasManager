import json
import os
from getpass import getpass

CONFIG_PATH = os.path.expanduser("~/.alias_manager_config.json")

def setup_config():
    print("Remote configuration not found. Please enter remote SSH details.")
    remote_host = input("Remote host (IP or hostname): ").strip()
    remote_username = input("Remote username: ").strip()
    remote_password = getpass("Remote password: ")
    config = {
        "remote_host": remote_host,
        "remote_username": remote_username,
        "remote_password": remote_password
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_PATH}")
    except Exception as e:
        print("Error saving configuration file:", e)
    return config

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print("Error reading configuration file:", e)
            # If there's an error reading, force re-setup
            return setup_config()
    else:
        return setup_config()