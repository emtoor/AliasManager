import json
import os

CONFIG_PATH = os.path.expanduser("~/.alias_manager_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print("Error reading configuration file:", e)
    return {}

def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Error saving configuration file:", e)
