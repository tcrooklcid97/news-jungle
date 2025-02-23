# This file must be used with "source bin/activate.csh" *from csh*.
# You cannot run it directly.
# Created by Davide Di Blasi <davidedb@gmail.com>.
# Ported to Python 3.3 venv by Andrew Svetlov <andrew.svetlov@gmail.com>

# Brief description:
# This script activates the Python virtual environment by setting up the necessary environment variables
# and modifying the shell prompt. It also defines a `deactivate` alias to revert the changes.

alias deactivate 'test $?_OLD_VIRTUAL_PATH != 0 && setenv PATH "$_OLD_VIRTUAL_PATH" && unset _OLD_VIRTUAL_PATH; rehash; test $?_OLD_VIRTUAL_PROMPT != 0 && set prompt="$_OLD_VIRTUAL_PROMPT" && unset _OLD_VIRTUAL_PROMPT; unsetenv VIRTUAL_ENV; unsetenv VIRTUAL_ENV_PROMPT; test "\!:*" != "nondestructive" && unalias deactivate'

# Unset irrelevant variables.
deactivate nondestructive

# Set up the virtual environment
setenv VIRTUAL_ENV /Users/Lenovo/Downloads/news_jungle_export/environment

set _OLD_VIRTUAL_PATH="$PATH"
setenv PATH "$VIRTUAL_ENV/bin:$PATH"

# Unset PYTHONHOME if set
if ( $?PYTHONHOME ) then
    set _OLD_VIRTUAL_PYTHONHOME="$PYTHONHOME"
    unsetenv PYTHONHOME
endif

# Modify the shell prompt to indicate the virtual environment is active
if (! $?VIRTUAL_ENV_DISABLE_PROMPT) then
    set _OLD_VIRTUAL_PROMPT="$prompt"
    set prompt = '(environment) '"$prompt"
    setenv VIRTUAL_ENV_PROMPT '(environment) '
endif

alias pydoc 'python -m pydoc'

rehash