# main_script.py

import clr
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')

from pyrevit import script
import custom_dialog  # Import the custom dialog module

# Get the output object
output = script.get_output()

# Show the custom dialog
result = custom_dialog.show_dialog()

# Handle the result
if result:
    output.print_md("**Option 1:** %s" % result["option1"])
    output.print_md("**Option 2:** %s" % result["option2"])
    output.print_md("**Option 3:** %s" % result["option3"])
    output.print_md("**Numbering Strategy:** %s" % result["numbering_strategy"])
else:
    output.print_md("**Dialog was cancelled or closed.**")