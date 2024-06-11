import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import revit, DB, script

# Get the output object
output = script.get_output()

# Get the current Revit document and UI document
doc = revit.doc
uidoc = revit.uidoc

# Prompt user to select elements
selection = uidoc.Selection
selected_refs = selection.PickObjects(ObjectType.Element, "Select elements")

# Start a transaction
t = DB.Transaction(doc, "Remove Mullions Above Doors")
t.Start()

try:
    for elem_ref in selected_refs:
        element = doc.GetElement(elem_ref.ElementId)

        # Debugging output to understand the selected element
        output.print_md("**Selected Element:** {} of type {} with category ID {}".format(
            element.Id, element.GetType().Name, element.Category.Id.IntegerValue))

        # Check if the element has a valid location
        location = element.Location
        if location:
            output.print_md("**Location Type:** {}".format(type(location)))
            if hasattr(location, 'Point'):
                door_location = location.Point
                output.print_md("**Location Point:** {}".format(door_location))
            elif hasattr(location, 'Curve'):
                door_location = location.Curve.GetEndPoint(0)  # Use the start point of the curve as the location
                output.print_md("**Location Curve Start Point:** {}".format(door_location))
            else:
                output.print_md("**Warning:** Selected element does not have a valid location point or curve.")
                continue

            # Get the curtain wall that contains the element
            host_element = element.Host
            if host_element and isinstance(host_element, Wall):
                output.print_md("**Host Curtain Wall:** {} of type {}".format(host_element.Id, host_element.GetType().Name))

                # Get the curtain grid
                curtain_grid = host_element.CurtainGrid

                # Debugging output for curtain grid
                output.print_md("**Curtain Grid:** Found {} mullions".format(len(curtain_grid.GetMullions())))

                # Find the mullion directly above the element
                for mullion in curtain_grid.GetMullions():
                    if mullion.LocationCurve is not None:
                        mullion_location_curve = mullion.LocationCurve
                        mullion_start = mullion_location_curve.GetEndPoint(0)
                        mullion_end = mullion_location_curve.GetEndPoint(1)

                        # Debugging output for mullion location
                        output.print_md("**Mullion Location:** Start {} End {}".format(mullion_start, mullion_end))

                        # Check if the mullion is directly above the element
                        if (mullion_start.X == door_location.X and mullion_start.Y == door_location.Y and
                                mullion_start.Z > door_location.Z and mullion_end.Z > door_location.Z):
                            output.print_md("**Mullion to Remove:** {}".format(mullion.Id))

                            # Unpin the mullion if it is pinned
                            if mullion.Pinned:
                                mullion.Pinned = False
                                output.print_md("**Mullion Unpinned:** {}".format(mullion.Id))

                            # Remove the mullion
                            doc.Delete(mullion.Id)
                            output.print_md("**Mullion Removed:** {}".format(mullion.Id))
                            break
            else:
                output.print_md("**Warning:** Host element is not a curtain wall or does not exist.")
        else:
            output.print_md("**Warning:** Selected element does not have a valid location.")
finally:
    # Commit the transaction
    t.Commit()

# Notify user of completion
output.print_md("**Operation Complete:** Mullions above selected elements have been removed.")