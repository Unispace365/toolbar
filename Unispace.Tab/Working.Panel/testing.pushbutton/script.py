import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

from pyrevit import revit, DB, UI
from pyrevit import script
import math

output = script.get_output()

doc = revit.doc

class ElevationMarkerFilter(ISelectionFilter):
    def AllowElement(self, elem):
        return isinstance(elem, ElevationMarker)
    
    def AllowReference(self, reference, position):
        return False

def get_direction_in_degrees(direction):
    # Flip the Y-axis to account for Revit's coordinate system
    angle = math.atan2(-direction.Y, direction.X)
    degrees = math.degrees(angle)
    if degrees < 0:
        degrees += 360
    return degrees

def get_cardinal_direction(angle):
    if 0 <= angle < 22.5 or 337.5 <= angle < 360:
        return "East"
    elif 22.5 <= angle < 67.5:
        return "Northeast"
    elif 67.5 <= angle < 112.5:
        return "North"
    elif 112.5 <= angle < 157.5:
        return "Northwest"
    elif 157.5 <= angle < 202.5:
        return "West"
    elif 202.5 <= angle < 247.5:
        return "Southwest"
    elif 247.5 <= angle < 292.5:
        return "South"
    elif 292.5 <= angle < 337.5:
        return "Southeast"

def get_room_from_point(point):
    return doc.GetRoomAtPoint(point)

# Main script
try:
    output.print_md("### Elevation ViewSection Information")
    
    # Prompt user to select an ElevationMarker
    selection = revit.uidoc.Selection
    elevation_marker_ref = selection.PickObject(ObjectType.Element, ElevationMarkerFilter(), "Select an Elevation Marker")
    elevation_marker = doc.GetElement(elevation_marker_ref.ElementId)
    
    output.print_md("Selected Elevation Marker ID: {}".format(elevation_marker.Id))
    
    # Check if the marker has elevations
    has_elevations = elevation_marker.HasElevations()
    output.print_md("Elevation Marker HasElevations(): {}".format(has_elevations))
    
    # Get the number of elevations
    num_elevations = sum(1 for i in range(4) if not elevation_marker.IsAvailableIndex(i))
    output.print_md("Number of elevations: {}".format(num_elevations))
    
    if has_elevations:
        output.print_md("Elevation Marker reports having elevations.")
        views_found = False
        
        for index in range(4):  # ElevationMarkers typically have up to 4 elevations
            output.print_md("Checking index: {}".format(index))
            
            is_available = elevation_marker.IsAvailableIndex(index)
            output.print_md("  Is index {} available: {}".format(index, is_available))
            
            if not is_available:  # If not available, it means there's an elevation view
                view_id = elevation_marker.GetViewId(index)
                output.print_md("  View ID at index {}: {}".format(index, view_id))
                
                if view_id != ElementId.InvalidElementId:
                    view_element = doc.GetElement(view_id)
                    output.print_md("  Element type at index {}: {}".format(index, type(view_element).__name__))
                    
                    if isinstance(view_element, ViewSection):
                        views_found = True
                        output.print_md("#### Elevation View {}".format(index + 1))
                        output.print_md("**View Name:** {}".format(view_element.Name))
                        output.print_md("**View Id:** {}".format(view_element.Id))
                        
                        # Get and display the orientation with cardinal direction
                        direction = view_element.ViewDirection
                        orientation = get_direction_in_degrees(direction)
                        cardinal_direction = get_cardinal_direction(orientation)
                        output.print_md("**Orientation:** {:.2f} degrees ({})".format(orientation, cardinal_direction))
                        
                        # Get information about the room where the ElevationMarker is placed
                        bbox = elevation_marker.BoundingBox
                        print(bbox)
                        if bbox:
                            center = bbox.Min + 0.5 * (bbox.Max - bbox.Min)
                            room = get_room_from_point(center)
                            if room and hasattr(room, 'Name') and hasattr(room, 'Number'):
                                output.print_md("**Room Name:** {}".format(room.Name))
                                output.print_md("**Room Number:** {}".format(room.Number))
                            else:
                                output.print_md("**Room Information:** Elevation Marker is not associated with a room or room details are missing")
                        else:
                            output.print_md("**Room Information:** Unable to determine bounding box of Elevation Marker")
                        
                        # Display some additional useful information
                        output.print_md("**View Scale:** 1:{}".format(view_element.Scale))
                        output.print_md("**Detail Level:** {}".format(view_element.DetailLevel))
                        output.print_md("**Display Style:** {}".format(view_element.DisplayStyle))
                        
                        output.print_md("---")  # Separator between views
                        
                    else:
                        output.print_md("  View at index {} is not a ViewSection".format(index))
                else:
                    output.print_md("  Invalid View ID at index {}".format(index))
            else:
                output.print_md("  No elevation view at index {}".format(index))
            
            output.print_md("---")  # Separator between indices
        
        if not views_found:
            output.print_md("No valid ViewSections found for this Elevation Marker.")
    else:
        output.print_md("The selected Elevation Marker reports having no elevations.")

except Exception as e:
    output.print_md("An error occurred: {}".format(str(e)))
    import traceback
    output.print_md("Detailed error information:")
    output.print_md(traceback.format_exc())