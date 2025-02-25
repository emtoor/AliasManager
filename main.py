import platform
import argparse
import logging
from getpass import getpass

# Set up logging
logging.basicConfig(
    filename='alias_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_args():
    parser = argparse.ArgumentParser(description="CLI Alias Manager for local and remote machines")
    parser.add_argument("--mode", choices=["local", "remote"], help="Operation mode: local or remote")
    parser.add_argument("--alias", help="Alias name to create")
    parser.add_argument("--command", help="Command that the alias should execute")
    # Remote-specific arguments
    parser.add_argument("--remote_os", choices=["osx", "windows"], help="Remote OS type (if mode is remote)")
    parser.add_argument("--host", help="Remote host IP or hostname")
    parser.add_argument("--username", help="Remote username")
    parser.add_argument("--password", help="Remote password (will prompt if omitted)")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.mode:
        args.mode = input("Do you want to create a local alias or remote alias? (local/remote): ").strip().lower()
    if not args.alias:
        args.alias = input("Enter the alias name: ").strip()
    if not args.command:
        args.command = input("Enter the command for the alias: ").strip()

    if args.mode == "local":
        current_os = platform.system()
        if current_os == "Darwin":
            from alias_manager_osx import OSXAliasManager
            manager = OSXAliasManager()
        elif current_os == "Windows":
            from alias_manager_windows import WindowsAliasManager
            manager = WindowsAliasManager()
        else:
            logging.error("Unsupported OS for local alias creation.")
            print("Unsupported OS for local alias creation.")
            return
    elif args.mode == "remote":
        if not args.remote_os:
            args.remote_os = input("Enter remote OS (osx/windows): ").strip().lower()
        if not args.host:
            args.host = input("Enter remote host IP: ").strip()
        if not args.username:
            args.username = input("Enter remote username: ").strip()
        if not args.password:
            args.password = getpass("Enter remote password: ")
        from alias_manager_remote import RemoteAliasManager
        manager = RemoteAliasManager(args.remote_os, args.host, args.username, args.password)
    else:
        logging.error("Invalid mode selected. Must be 'local' or 'remote'.")
        print("Invalid mode selected. Please choose 'local' or 'remote'.")
        return

    try:
        manager.create_alias(args.alias, args.command)
        logging.info("Alias '%s' created successfully.", args.alias)
        print("Alias created successfully. Please restart or reload your shell for changes to take effect.")
    except Exception as e:
        logging.exception("An error occurred while creating the alias:")
        print("An error occurred:", e)

if __name__ == '__main__':
    main()
