# Import the required Revit API modules
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance, Transaction
from Autodesk.Revit.UI import TaskDialog
import Autodesk.Revit.UI.Selection
import clr
from System.Collections.Generic import List
from Autodesk.Revit.DB import ElementId

# Import the script utilities from pyRevit
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from pyrevit import script, revit

# Get the current Revit document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Function to filter elements by family name starting with "Enscape"
def get_elements_with_enscape_family_name(doc):
    enscape_elements = []
    
    # Use a filtered element collector to get all family instances in the model
    collector = FilteredElementCollector(doc).OfClass(FamilyInstance)
    
    # Iterate through the elements
    for element in collector:
        family = element.Symbol.Family
        if family and family.Name.startswith('Enscape'):
            enscape_elements.append(element.Id)
    
    return enscape_elements

# Function to select the elements in the Revit UI
def select_elements_in_ui(uidoc, element_ids):
    # Make sure we have elements to select
    if element_ids:
        # Convert Python list to .NET List[ElementId]
        element_id_list = List[ElementId](element_ids)

        # Start a transaction to modify the document
        t = Transaction(doc, 'Select Enscape Elements')
        t.Start()
        
        # Set the current selection to the enscape elements
        uidoc.Selection.SetElementIds(element_id_list)
        
        # Commit the transaction
        t.Commit()
        
        # Inform the user
        TaskDialog.Show('Selection', 'Selected {} Enscape elements.'.format(len(element_ids)))
    else:
        # Inform the user if no elements were found
        TaskDialog.Show('Selection', 'No Enscape elements found.')

# Main script execution
if __name__ == '__main__':
    # Get all elements with family names starting with "Enscape"
    enscape_element_ids = get_elements_with_enscape_family_name(doc)
    
    # Select the elements in the Revit UI
    select_elements_in_ui(uidoc, enscape_element_ids)