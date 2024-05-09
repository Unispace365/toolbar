from pyrevit import revit, DB, forms
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult

# Initialize Document
doc = revit.doc

def append_letter(existing_numbers, base_number):
    """
    Appends letters to the base number to ensure uniqueness.
    Handles more than 26 occurrences by moving to AA, AB, etc.
    """
    if not existing_numbers:
        return base_number
    index = 0
    while True:
        if index < 26:
            suffix = chr(65 + index)
        else:
            first_letter = chr(65 + (index // 26) - 1)
            second_letter = chr(65 + (index % 26))
            suffix = first_letter + second_letter
        
        new_number = base_number + suffix
        if new_number not in existing_numbers:
            return new_number
        index += 1

def append_number(existing_numbers, base_number):
    """
    Appends numbers (.01, .02, ...) to the base number to ensure uniqueness, starting with the base number for the first item.
    """
    if base_number not in existing_numbers:
        return base_number  # Return the base number if it's not already used

    index = 1
    while True:
        new_number = "{}.{:02}".format(base_number, index)
        if new_number not in existing_numbers:
            return new_number
        index += 1

def renumber_doors(prefix_existing, use_letters):
    with DB.Transaction(doc, "Renumber Doors") as t:
        t.Start()
        
        # Collect all doors in the project
        doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
        
        # Get the last phase of the project (most recent phase)
        phase = doc.Phases[doc.Phases.Size - 1]
        
        # Dictionary to hold room number and list of doors in that room
        room_doors = {}
        
        # Iterate through all doors
        for door in doors:
            try:
                room = door.ToRoom[phase]
            except:
                room = None
            
            if room:
                room_number_param = room.LookupParameter("Number")
                room_number = room_number_param.AsString() if room_number_param else "Undefined"
                
                # Check if the door was created in the "Existing" phase
                phase_created_param = door.get_Parameter(DB.BuiltInParameter.PHASE_CREATED)
                door_phase = doc.GetElement(phase_created_param.AsElementId())
                if door_phase and door_phase.Name == "Existing" and prefix_existing:
                    room_number = "EX" + room_number
                
                if room_number not in room_doors:
                    room_doors[room_number] = []
                room_doors[room_number].append(door)
        
        # Assign new numbers to doors
        for room_number, doors in room_doors.items():
            used_numbers = set()
            for door in doors:
                new_number = append_letter(used_numbers, room_number) if use_letters else append_number(used_numbers, room_number)
                mark_param = door.LookupParameter("Mark")
                if mark_param:
                    mark_param.Set(new_number)
                used_numbers.add(new_number)
        
        t.Commit()

# Ask user if they want to prefix door numbers with 'EX'
prefix_existing = forms.alert("Do you want to prefix door numbers with 'EX' for doors created in the 'Existing' phase?",
                              yes=True, no=True, title="Door Number Prefix")

# Ask user to choose the numbering method
numbering_method = forms.CommandSwitchWindow.show(
    ['Append letters (A, B, C, ...)', 'Append numbers (.01, .02, ...)'],
    message='Choose the numbering method for doors in the same room:')

# Check what the user chose for the numbering method
use_letters = numbering_method == 'Append letters (A, B, C, ...)'

# Execute the function based on user choices
try:
    renumber_doors(prefix_existing, use_letters)

    # Informative message after operation
    # forms.alert("Doors have been successfully renumbered.\nPlease review all doors to make sure the numbering is as expected.",
    #             title="Review Door Numbers")
    info_dialog = TaskDialog("Review Door Numbers")
    info_dialog.MainInstruction = "This tool is a good first pass at renumbering doors. After running, please review all doors to make sure the numbering is as expected."
    info_dialog.Show()

except Exception as e:
    forms.alert("Error renumbering doors: {0}".format(str(e)), title="Error")