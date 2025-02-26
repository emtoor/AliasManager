import platform
import argparse
import logging
import os
from config import load_config

# Set up logging
logging.basicConfig(
    filename='alias_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI Alias Manager for local and remote machines (dual creation)"
    )
    parser.add_argument("--alias", help="Alias name to create")
    parser.add_argument("--command", help="Command that the alias should execute")
    return parser.parse_args()

def reload_shell():
    """Reload the current shell if on macOS; on Windows, instruct the user."""
    local_os = platform.system()
    if local_os == "Darwin":
        shell = os.environ.get("SHELL")
        if shell:
            print(f"Reloading your shell ({shell}) to apply changes...")
            input("Press Enter to reload your shell now...")
            # Replace current process with a new shell process.
            os.execvp(shell, [shell])
        else:
            print("Could not determine your shell. Please reload manually.")
    elif local_os == "Windows":
        print("Please restart your terminal (CMD/PowerShell) to apply the new alias.")
    else:
        print("Shell reload is not supported on this OS.")

def main():
    args = parse_args()
    
    # Ask only for alias and command if not provided as arguments.
    if not args.alias:
        args.alias = input("Enter the alias name: ").strip()
    if not args.command:
        args.command = input("Enter the command for the alias: ").strip()
    
    local_os = platform.system()
    logging.info("Local OS detected: %s", local_os)
    
    # Create local alias using the appropriate module.
    if local_os == "Darwin":
        from alias_manager_osx import OSXAliasManager
        local_manager = OSXAliasManager()
    elif local_os == "Windows":
        from alias_manager_windows import WindowsAliasManager
        local_manager = WindowsAliasManager()
    else:
        logging.error("Unsupported local OS: %s", local_os)
        print("Unsupported local OS for alias creation.")
        return

    try:
        local_manager.create_alias(args.alias, args.command)
        print("Local alias created successfully.")
    except Exception as e:
        logging.exception("Local alias creation failed:")
        print("Local alias creation failed:", e)
        return

    # Determine remote target OS (assumes remote is the "other" OS).
    if local_os == "Darwin":
        remote_os = "windows"
        os_msg = "Windows"
    elif local_os == "Windows":
        remote_os = "osx"
        os_msg = "OSX"
    else:
        print("Remote creation not supported for local OS:", local_os)
        return

    # Load remote configuration from the config file.
    config = load_config()
    remote_host = config.get("remote_host")
    remote_username = config.get("remote_username")
    remote_password = config.get("remote_password")
    
    if not (remote_host and remote_username and remote_password):
        print("Remote configuration not found in config file. Please set it up.")
        return

    from alias_manager_remote import RemoteAliasManager
    try:
        remote_manager = RemoteAliasManager(remote_os, remote_host, remote_username, remote_password)
        remote_manager.create_alias(args.alias, args.command)
        print(f"Remote alias created successfully on {os_msg} machine.")
    except Exception as e:
        logging.exception("Remote alias creation failed:")
        print("Remote alias creation failed:", e)
        return

    # After aliases are added, reload the shell to pick up new aliases.
    reload_shell()

if __name__ == '__main__':
    main()