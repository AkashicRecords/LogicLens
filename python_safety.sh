#!/bin/bash
# Safety wrapper for Python commands
# This adds an extra step to Python commands to ensure environment awareness

echo "Setting up Python safety measures..."

# Create the safety wrapper function for python/python3
cat > ~/.python_safety_wrapper.sh << 'EOL'
#!/bin/bash

python_safety() {
    # Check if first argument is the safety keyword
    if [[ "$1" != "global" ]]; then
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "!! SAFETY CHECK: You must use 'global' keyword with Python !!"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo ""
        echo "ENVIRONMENT CHECK:"
        echo "- Current directory: $(pwd)"
        echo "- Virtual env active: ${VIRTUAL_ENV:-(none)}"
        echo "- Python executable: $(which python3 || which python)"
        echo ""
        echo "USE THE MANAGEMENT SCRIPT WHEN POSSIBLE:"
        echo "  python3 logiclens_manage.py start"
        echo ""
        echo "Or to bypass this check, use:"
        echo "  global python3 [your command]"
        return 1
    fi
    
    # Remove the 'global' keyword and execute the command
    shift
    command "$@"
}

# Create aliases for python and python3
alias python='python_safety global python'
alias python3='python_safety global python3'
EOL

# Add to bash/zsh profile if not already there
if ! grep -q "source ~/.python_safety_wrapper.sh" ~/.bashrc 2>/dev/null; then
    echo "# Python safety wrapper" >> ~/.bashrc
    echo "source ~/.python_safety_wrapper.sh" >> ~/.bashrc
    echo "Added to ~/.bashrc"
fi

if [ -f ~/.zshrc ] && ! grep -q "source ~/.python_safety_wrapper.sh" ~/.zshrc 2>/dev/null; then
    echo "# Python safety wrapper" >> ~/.zshrc
    echo "source ~/.python_safety_wrapper.sh" >> ~/.zshrc
    echo "Added to ~/.zshrc"
fi

# Make the wrapper executable
chmod +x ~/.python_safety_wrapper.sh

echo ""
echo "Python safety measures have been installed."
echo "Now you need to use 'global' keyword with Python commands:"
echo ""
echo "  global python3 logiclens_manage.py start   # This will work"
echo "  python3 logiclens_manage.py start          # This will show warning"
echo ""
echo "IMPORTANT: You need to restart your shell or run 'source ~/.python_safety_wrapper.sh'"
echo "           for these changes to take effect."
echo ""
echo "Note for LogicLens startup: Always use the management script:"
echo "  global python3 logiclens_manage.py start" 