import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import platform
import logging
from config import load_config

# Set up logging
logging.basicConfig(
    filename='alias_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Determine local OS and import the appropriate module.
local_os = platform.system()
if local_os == "Darwin":
    from alias_manager_osx import OSXAliasManager
elif local_os == "Windows":
    from alias_manager_windows import WindowsAliasManager
else:
    messagebox.showerror("OS Error", f"Unsupported local OS: {local_os}")
    exit(1)

# Import remote alias manager.
from alias_manager_remote import RemoteAliasManager

def create_alias():
    alias_name = alias_entry.get().strip()
    command = command_entry.get().strip()
    if not alias_name or not command:
        messagebox.showerror("Input Error", "Please provide both alias and command.")
        return
    try:
        # Create local alias.
        if local_os == "Darwin":
            local_manager = OSXAliasManager()
        elif local_os == "Windows":
            local_manager = WindowsAliasManager()
        local_manager.create_alias(alias_name, command)
        logging.info("Local alias created: %s", alias_name)
    except Exception as e:
        logging.exception("Error creating local alias")
        messagebox.showerror("Error", f"Error creating local alias: {e}")
        return

    # Determine remote OS (assume remote is the opposite OS).
    if local_os == "Darwin":
        remote_os = "windows"
        remote_os_msg = "Windows"
    elif local_os == "Windows":
        remote_os = "osx"
        remote_os_msg = "OSX"
    else:
        messagebox.showerror("OS Error", f"Unsupported local OS: {local_os}")
        return

    # Load remote configuration.
    config = load_config()
    remote_host = config.get("remote_host")
    remote_username = config.get("remote_username")
    remote_password = config.get("remote_password")
    if not (remote_host and remote_username and remote_password):
        messagebox.showerror("Configuration Error", "Remote configuration not found. Please set up the config file.")
        return

    try:
        remote_manager = RemoteAliasManager(remote_os, remote_host, remote_username, remote_password)
        remote_manager.create_alias(alias_name, command)
        logging.info("Remote alias created on %s: %s", remote_os_msg, alias_name)
        messagebox.showinfo("Success", "Alias created locally and remotely successfully!")
    except Exception as e:
        logging.exception("Error creating remote alias")
        messagebox.showerror("Error", f"Error creating remote alias: {e}")

def list_aliases():
    # List local aliases.
    try:
        if local_os == "Darwin":
            local_manager = OSXAliasManager()
        elif local_os == "Windows":
            local_manager = WindowsAliasManager()
        local_aliases = local_manager.list_aliases()
    except Exception as e:
        logging.exception("Error listing local aliases")
        messagebox.showerror("Error", f"Error listing local aliases: {e}")
        local_aliases = {}

    # List remote aliases.
    try:
        if local_os == "Darwin":
            remote_os = "windows"
        elif local_os == "Windows":
            remote_os = "osx"
        config = load_config()
        remote_host = config.get("remote_host")
        remote_username = config.get("remote_username")
        remote_password = config.get("remote_password")
        remote_manager = RemoteAliasManager(remote_os, remote_host, remote_username, remote_password)
        remote_aliases = remote_manager.list_aliases()
    except Exception as e:
        logging.exception("Error listing remote aliases")
        messagebox.showerror("Error", f"Error listing remote aliases: {e}")
        remote_aliases = {}

    result = "Local Aliases:\n"
    for k, v in local_aliases.items():
        result += f"{k}: {v}\n"
    result += "\nRemote Aliases:\n"
    for k, v in remote_aliases.items():
        result += f"{k}: {v}\n"

    list_window = tk.Toplevel(root)
    list_window.title("List of Aliases")
    text_area = scrolledtext.ScrolledText(list_window, width=60, height=20)
    text_area.pack(padx=10, pady=10)
    text_area.insert(tk.END, result)
    text_area.config(state=tk.DISABLED)

def update_alias():
    alias_name = simpledialog.askstring("Update Alias", "Enter the alias name to update:")
    if not alias_name:
        return
    new_command = simpledialog.askstring("Update Alias", "Enter the new command:")
    if not new_command:
        return
    try:
        if local_os == "Darwin":
            local_manager = OSXAliasManager()
        elif local_os == "Windows":
            local_manager = WindowsAliasManager()
        local_manager.update_alias(alias_name, new_command)
        logging.info("Local alias updated: %s", alias_name)
    except Exception as e:
        logging.exception("Error updating local alias")
        messagebox.showerror("Error", f"Error updating local alias: {e}")
        return

    try:
        if local_os == "Darwin":
            remote_os = "windows"
        elif local_os == "Windows":
            remote_os = "osx"
        config = load_config()
        remote_host = config.get("remote_host")
        remote_username = config.get("remote_username")
        remote_password = config.get("remote_password")
        remote_manager = RemoteAliasManager(remote_os, remote_host, remote_username, remote_password)
        remote_manager.update_alias(alias_name, new_command)
        logging.info("Remote alias updated: %s", alias_name)
        messagebox.showinfo("Success", "Alias updated locally and remotely successfully!")
    except Exception as e:
        logging.exception("Error updating remote alias")
        messagebox.showerror("Error", f"Error updating remote alias: {e}")

def delete_alias():
    alias_name = simpledialog.askstring("Delete Alias", "Enter the alias name to delete:")
    if not alias_name:
        return
    try:
        if local_os == "Darwin":
            local_manager = OSXAliasManager()
        elif local_os == "Windows":
            local_manager = WindowsAliasManager()
        local_manager.delete_alias(alias_name)
        logging.info("Local alias deleted: %s", alias_name)
    except Exception as e:
        logging.exception("Error deleting local alias")
        messagebox.showerror("Error", f"Error deleting local alias: {e}")
        return

    try:
        if local_os == "Darwin":
            remote_os = "windows"
        elif local_os == "Windows":
            remote_os = "osx"
        config = load_config()
        remote_host = config.get("remote_host")
        remote_username = config.get("remote_username")
        remote_password = config.get("remote_password")
        remote_manager = RemoteAliasManager(remote_os, remote_host, remote_username, remote_password)
        remote_manager.delete_alias(alias_name)
        logging.info("Remote alias deleted: %s", alias_name)
        messagebox.showinfo("Success", "Alias deleted locally and remotely successfully!")
    except Exception as e:
        logging.exception("Error deleting remote alias")
        messagebox.showerror("Error", f"Error deleting remote alias: {e}")

# Set up the main GUI window.
root = tk.Tk()
root.title("Alias Manager GUI")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

# Alias label and entry.
alias_label = tk.Label(frame, text="Alias:")
alias_label.grid(row=0, column=0, sticky="e")
alias_entry = tk.Entry(frame, width=40)
alias_entry.grid(row=0, column=1, pady=5)

# Command label and entry.
command_label = tk.Label(frame, text="Command:")
command_label.grid(row=1, column=0, sticky="e")
command_entry = tk.Entry(frame, width=40)
command_entry.grid(row=1, column=1, pady=5)

# Create Alias button.
create_button = tk.Button(frame, text="Create Alias", command=create_alias)
create_button.grid(row=2, column=0, columnspan=2, pady=10)

# Buttons for listing, updating, and deleting aliases.
list_button = tk.Button(frame, text="List Aliases", command=list_aliases)
list_button.grid(row=3, column=0, pady=5)
update_button = tk.Button(frame, text="Update Alias", command=update_alias)
update_button.grid(row=3, column=1, pady=5)
delete_button = tk.Button(frame, text="Delete Alias", command=delete_alias)
delete_button.grid(row=4, column=0, columnspan=2, pady=5)

root.mainloop()
