# This file must be used with "source <venv>/bin/Activate.ps1" *from PowerShell*
# you cannot run it directly.

# Brief description:
# This script activates the Python virtual environment by setting up the necessary environment variables
# and modifying the shell prompt. It also defines a `deactivate` function to revert the changes.

function Deactivate {
    # Reset old environment variables
    if (Test-Path -Path variable:_OLD_VIRTUAL_PATH) {
        $env:PATH = $_OLD_VIRTUAL_PATH
        Remove-Variable -Name _OLD_VIRTUAL_PATH -Scope Global
    }
    if (Test-Path -Path variable:_OLD_VIRTUAL_PYTHONHOME) {
        $env:PYTHONHOME = $_OLD_VIRTUAL_PYTHONHOME
        Remove-Variable -Name _OLD_VIRTUAL_PYTHONHOME -Scope Global
    }

    if (Test-Path -Path variable:_OLD_VIRTUAL_PROMPT) {
        $function:prompt = $_OLD_VIRTUAL_PROMPT
        Remove-Variable -Name _OLD_VIRTUAL_PROMPT -Scope Global
    }

    Remove-Variable -Name VIRTUAL_ENV -Scope Global
    Remove-Variable -Name VIRTUAL_ENV_PROMPT -Scope Global
    if ($args[0] -ne "nondestructive") {
        # Self-destruct!
        Remove-Item -Path function:Deactivate
    }
}

# Unset irrelevant variables.
Deactivate nondestructive

# Set up the virtual environment
$env:VIRTUAL_ENV = "/Users/Lenovo/Downloads/news_jungle_export/environment"

$_OLD_VIRTUAL_PATH = $env:PATH
$env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

# Unset PYTHONHOME if set
if (Test-Path -Path variable:PYTHONHOME) {
    $_OLD_VIRTUAL_PYTHONHOME = $env:PYTHONHOME
    Remove-Variable -Name PYTHONHOME -Scope Global
}

# Modify the shell prompt to indicate the virtual environment is active
if (-not (Test-Path -Path variable:VIRTUAL_ENV_DISABLE_PROMPT)) {
    $_OLD_VIRTUAL_PROMPT = $function:prompt
    function prompt {
        Write-Host -NoNewline "(environment) "
        & $function:prompt
    }
    $env:VIRTUAL_ENV_PROMPT = "(environment) "
}