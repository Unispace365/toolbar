# -*- coding: utf-8 -*-
__title__ = 'Set DOB Page Numbers'
__author__ = 'Matt Vogel'
__doc__ = 'Sets sheet titleblock page number parameters for a New York DOB issuance.'
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, ViewSchedule, BuiltInParameter, Transaction, BuiltInCategory, StorageType
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
from pyrevit import revit, DB

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def is_sheet_list_schedule(view):
    if not isinstance(view, ViewSchedule):
        return False  # Not a schedule view
    
    # Attempt to get the schedule's category
    try:
        # For a Sheet List, the schedule definition's category id should match that of Sheets (OST_Sheets)
        schedule_def = view.Definition
        category_id = schedule_def.CategoryId
        if category_id == doc.Settings.Categories.get_Item(BuiltInCategory.OST_Sheets).Id:
            return True
    except:
        pass  # In case of any errors, assume it's not a Sheet List
    
    return False

# Function to get parameter value safely
def get_parameter_value(element, param_name):
    param = element.LookupParameter(param_name)
    if param:
        return param.AsString() or param.AsValueString() or ""
    return ""

# Function to set the value of a parameter in the Project Information
def set_project_info_parameter(param_name, value):
    # Start a transaction to modify the document
    t = Transaction(doc, 'Set Project Info Parameter')
    t.Start()
    
    try:
        # Get the Project Information element. Use ToElements() and then access the first element if the collection is not empty.
        project_info_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectInformation).ToElements()
        project_info = project_info_collector[0] if project_info_collector else None
        
        if project_info:
            param = project_info.LookupParameter(param_name)
            if param:
                # Determine the parameter's storage type and set its value accordingly
                if param.StorageType == StorageType.String:
                    param.Set(str(value))  # Convert value to string, as Set expects a string for String parameters
                elif param.StorageType == StorageType.Integer:
                    param.Set(int(value))  # Ensure value is an integer for Integer parameters
                elif param.StorageType == StorageType.Double:
                    param.Set(float(value))  # Ensure value is a float for Double parameters
                # Add more cases here if necessary for other storage types
                
                t.Commit()  # Commit the transaction if the parameter value was set successfully
                return True
    except Exception as e:
        print(e)
        t.RollBack()  # Roll back the transaction in case of any errors
    
    return False

# Function to print elements from the current schedule view, sorted by a given parameter
def set_dob_sheet_number(schedule, sort_param):
    # Collect all elements in the schedule
    collector = FilteredElementCollector(doc, schedule.Id)
    elements = collector.ToElements()
    

    # Start a transaction to modify the document
    t = Transaction(doc, 'Set Page No of Sheets')
    t.Start()

    # Sort elements by Discipline and then Sheet Number
    sorted_sheets = sorted(elements, key=lambda x: (get_parameter_value(x, "Discipline"), x.SheetNumber))
    try:
        for index, sheet in enumerate(sorted_sheets):
            sheet_id = sheet.Id.IntegerValue
            sheet_name = sheet.Name
            sheet_discipline = get_parameter_value(sheet, sort_param)
            # print("{} - {}".format(sheet.SheetNumber, sheet.Name))
            # print(sheet.LookupParameter("Total_Pages"))
            sheet.LookupParameter("Page_No_of").Set(str(index+1))
        t.Commit()
    except Exception as e:
        # Something went wrong, print the error message
        print(str(e))
        t.RollBack()

    set_project_info_parameter("Total_Pages", str(len(sorted_sheets)))

def ask_user_to_proceed():
    dialog = TaskDialog("New York DOB Sheet Renumber")
    dialog.MainInstruction = "This script sets sheet titleblock page number parameter for a New York DOB issuance."
    dialog.MainContent = "Make sure the current open view is the DRAWING INDEX schedule.\nSheet page numbers will be numbered in the order they appear in a sheet schedule (Sorted by Discipline and then Sheet Number).\n\nPress OK to continue or Cancel to stop."
    dialog.CommonButtons = TaskDialogCommonButtons.Ok | TaskDialogCommonButtons.Cancel
    dialog.DefaultButton = TaskDialogResult.Cancel
    result = dialog.Show()
    
    if result == TaskDialogResult.Ok:
        return True
    else:
        return False

def main():
    # Get the current view
    current_view = uidoc.ActiveView

    # Ask user if they want to proceed
    if not ask_user_to_proceed():
        # print("Script cancelled by the user.")
        return

    if is_sheet_list_schedule(current_view):
        set_dob_sheet_number(current_view, "Discipline")
    else:
        TaskDialog.Show("View Check", "The current view is not a Sheet List schedule. Please open up the DRAWING INDEX schedule and rerun.")

main()