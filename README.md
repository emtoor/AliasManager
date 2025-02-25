# Alias Manager

This tool allows you to create CLI aliases on your local machine (OSX or Windows) or on remote machines via SSH.

## Features

- **Modular Design:** Separate modules for OSX, Windows, and remote alias creation.
- **Command-Line Support:** Use interactive prompts or pass arguments via the command line.
- **Logging:** All operations and errors are logged in \`alias_manager.log\`.
- **Configuration:** Optional configuration module (\`config.py\`) to store remote credentials securely.

## Installation

1. Install Python 3.
2. Install dependencies:
   \`\`\`
   pip install paramiko
   \`\`\`

## Usage

### Interactive Mode
Simply run:
\`\`\`
python main.py
\`\`\`

### Command-Line Mode
For example, to create a local alias:
\`\`\`
python main.py --mode local --alias ll --command "ls -la"
\`\`\`
For a remote alias:
\`\`\`
python main.py --mode remote --remote_os osx --host 192.168.1.3 --username emtoor --password YOUR_PASSWORD --alias ll --command "ls -la"
\`\`\`

## Security Note
Avoid hard-coding credentials. Consider using the configuration file (\`~/.alias_manager_config.json\`) or environment variables to manage sensitive data.
