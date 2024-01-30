@echo off

REM This is a Windows Batch script to install a private pyRevit extension
REM Docs found here https://pyrevitlabs.notion.site/Manage-pyRevit-extensions-fa853768e94240b5b59803e5d7171be3

REM Define variables
set command_name=extend
set extension_type=ui
set extension_name=Unispace
set repository_url=https://github.com/Unispace365/revit-unispace-toolbar.git
set username=SET_GITHUB_USERNAME_HERE
set token=SET_GITHUB_TOKEN_HERE
set branch=main

REM Build the command
set pyrevit_command=pyrevit %command_name% %extension_type% %extension_name% "%repository_url%" --username="%username%" --token="%token%" --branch="%branch%"

REM Print the command to the console
echo Running command: %pyrevit_command%

REM Run the command
%pyrevit_command%

REM End of the script
