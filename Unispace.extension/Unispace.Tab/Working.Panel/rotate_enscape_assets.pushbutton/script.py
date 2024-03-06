# Import the required Revit API modules
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, FamilyInstance,
                               Transaction, ElementId, ElementTransformUtils, Line, XYZ)
import Autodesk.Revit.UI.Selection
import clr
import random
import math

# Import the script utilities from pyRevit
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from pyrevit import script, revit

# Get the current Revit document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Function to filter elements by family name starting with "Enscape" and including "Standing" or "Walking"
def get_elements_with_enscape_family_name(doc):
    enscape_elements = []
    
    # Use a filtered element collector to get all family instances in the model
    collector = FilteredElementCollector(doc).OfClass(FamilyInstance)
    
    # Iterate through the elements
    for element in collector:
        family = element.Symbol.Family
        if family:
            family_name = family.Name
            if family_name.startswith('Enscape') and ("Standing" in family_name or "Walking" in family_name or "Waitress" in family_name):
                enscape_elements.append(element)
    
    return enscape_elements

# Function to rotate elements a random degree
def rotate_elements_randomly(doc, elements):
    # Start a transaction to modify the document
    with Transaction(doc, 'Rotate Enscape Elements') as t:
        t.Start()
        
        for element in elements:
            # Define the rotation axis (vertical in this case)
            location = element.Location.Point
            axis = Line.CreateBound(location, location + XYZ(0, 0, 1))
            
            # Generate a random angle between 0 and 360 degrees (in radians)
            random_angle = random.uniform(0, 2 * math.pi)
            
            # Rotate the element
            ElementTransformUtils.RotateElement(doc, element.Id, axis, random_angle)
        
        # Commit the transaction
        t.Commit()

# Main script execution
if __name__ == '__main__':
    # Get all elements with family names starting with "Enscape" and including "Standing" or "Walking"
    enscape_elements = get_elements_with_enscape_family_name(doc)
    
    # Rotate the elements a random degree
    rotate_elements_randomly(doc, enscape_elements)