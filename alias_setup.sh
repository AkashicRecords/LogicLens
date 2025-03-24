#!/bin/bash
# Sets up aliases to prevent manual server startup errors

cat << 'EOT'
========================================================================
      SETTING UP SAFETY ALIASES FOR LOGICLENS SERVER MANAGEMENT
========================================================================
EOT

# Get the project root directory
PROJECT_ROOT=$(pwd)
echo "Project root: $PROJECT_ROOT"

# Create aliases file
ALIASES_FILE="$PROJECT_ROOT/logiclens_aliases.sh"

cat > "$ALIASES_FILE" << EOT
# LogicLens Server Management Aliases
# These aliases help prevent common server startup errors

# Override dangerous manual commands with warnings
alias 'flask run'='echo "⛔ MANUAL STARTUP IS THE WRONG WAY! ⛔" && echo "Please use: logiclens-start" && false'
alias 'python -m flask run'='echo "⛔ MANUAL STARTUP IS THE WRONG WAY! ⛔" && echo "Please use: logiclens-start" && false'
alias 'python3 -m flask run'='echo "⛔ MANUAL STARTUP IS THE WRONG WAY! ⛔" && echo "Please use: logiclens-start" && false'

# Create safe commands
alias logiclens-start='cd $PROJECT_ROOT && python3 logiclens_manage.py start'
alias logiclens-stop='cd $PROJECT_ROOT && python3 logiclens_manage.py stop'
alias logiclens-status='cd $PROJECT_ROOT && python3 logiclens_manage.py status'
alias logiclens-setup='cd $PROJECT_ROOT && python3 logiclens_manage.py setup'
alias logiclens-ollama='cd $PROJECT_ROOT && python3 logiclens_manage.py ollama'

# Add reminder function
logiclens-help() {
  echo "========== LogicLens Safe Commands =========="
  echo "logiclens-start   - Start the server safely"
  echo "logiclens-stop    - Stop the server"
  echo "logiclens-status  - Check server status"
  echo "logiclens-setup   - Setup environment only"
  echo "logiclens-ollama  - Manage Ollama integration"
  echo "logiclens-help    - Show this help message"
  echo "==========================================="
}

# Add safeguard for the backend directory
cd() {
  builtin cd "\$@"
  if [[ "\$PWD" == *"/backend" ]]; then
    echo "⚠️  You are now in the backend directory ⚠️"
    echo "Remember to use logiclens-start instead of manual flask commands"
  fi
}
EOT

# Inform user how to use these aliases
echo
echo "Aliases created in: $ALIASES_FILE"
echo
echo "To use these aliases, run:"
echo "    source $ALIASES_FILE"
echo
echo "To make them permanent, add this line to your ~/.bashrc or ~/.zshrc:"
echo "    source $ALIASES_FILE"
echo
echo "=========================================================================="
echo "Available commands after sourcing aliases:"
echo "  logiclens-start   - Start the server safely"
echo "  logiclens-stop    - Stop the server"
echo "  logiclens-status  - Check server status"
echo "  logiclens-setup   - Setup environment only"
echo "  logiclens-ollama  - Manage Ollama integration"
echo "  logiclens-help    - Show this help message"
echo "=========================================================================="

# Ask if user wants to source the file now
read -p "Would you like to source the aliases file now? (y/n): " response
if [[ "$response" =~ ^[Yy] ]]; then
  source "$ALIASES_FILE"
  echo "Aliases loaded successfully!"
  echo "Try 'logiclens-help' to see available commands"
else
  echo "You can source the file later with: source $ALIASES_FILE"
fi 