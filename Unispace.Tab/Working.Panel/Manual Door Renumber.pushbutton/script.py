from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import revit, DB

doc = revit.doc
from Autodesk.Revit.UI.Selection import ISelectionFilter

class DoorSelectionFilter(ISelectionFilter):
    """ Allows selection of only door elements """
    def AllowElement(self, element):
        return element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors)

class RoomSelectionFilter(ISelectionFilter):
    """ Allows selection of only room elements """
    def AllowElement(self, element):
        return element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Rooms)

class RoomTagSelectionFilter(ISelectionFilter):
    """ Allows selection of only room tag elements """
    def AllowElement(self, element):
        return element.Category.Id.IntegerValue == int(BuiltInCategory.OST_RoomTags)
    
def select_element(message, selection_filter):
    """ Helper function to select an element """
    TaskDialog.Show('Selection', message)
    reference = revit.uidoc.Selection.PickObject(ObjectType.Element, selection_filter)
    return doc.GetElement(reference.ElementId)

def main():
    # Start transaction
    t = Transaction(doc, 'Renumber Door')
    t.Start()
    
    try:
        # Select door or use current selection
        if not revit.uidoc.Selection.GetElementIds():
            door = select_element('Please select a door.', DoorSelectionFilter())
        else:
            door_id = list(revit.uidoc.Selection.GetElementIds())[0]
            door = doc.GetElement(door_id)
        
        # Select room or room tag
        room = select_element('Please select a room or room tag.', RoomSelectionFilter())
        
        # Renumber door
        door.Parameter[DB.BuiltInParameter.DOOR_NUMBER].Set(room.Number)
        
        # Commit transaction
        t.Commit()
    except Exception as e:
        t.RollBack()
        TaskDialog.Show('Error', str(e))

# Run the main function
main()