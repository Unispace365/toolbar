@echo off
setlocal

set "JSON_FILE=%appdata%\pyRevit-Master\extensions\extensions.json"

:: Execute the PowerShell commands directly
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$json = Get-Content -Path '%JSON_FILE%' -Raw | ConvertFrom-Json; " ^
    "$newObject = [PSCustomObject]@{ " ^
        "builtin='False'; " ^
        "default_enabled='True'; " ^
        "type='extension'; " ^
        "rocket_mode_compatible='True'; " ^
        "name='Unispace Toolbar'; " ^
        "description='Set of custom tools for Unispace.'; " ^
        "author='Matt Vogel'; " ^
        "author_profile='https://www.linkedin.com/in/matthewtvogel'; " ^
        "url='https://github.com/Unispace365/revit-unispace-toolbar.git'; " ^
        "website='https://github.com/Unispace365/revit-unispace-toolbar'; " ^
        "image=''; " ^
        "templates=@{author=''; docpath=''}; " ^
        "dependencies=@(); " ^
    "}; " ^
    "$json.extensions += $newObject; " ^
    "$json | ConvertTo-Json -Depth 10 | Set-Content -Path '%JSON_FILE%'"

endlocal