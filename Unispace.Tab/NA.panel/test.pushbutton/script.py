# Import necessary PyRevit and Revit API components.
from pyrevit import script
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ViewSheet, ViewType, Transaction, LinePatternElement, Line, XYZ, DetailLine, ElementId, Viewport, BuiltInParameter, Color
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI import TaskDialogCommonButtons, TaskDialogResult
from collections import defaultdict

# Function to convert inches to feet
def inches_to_feet(inches):
    return inches / 12.0

# Function to show an alert dialog in Revit
def show_alert(title, message):
    dialog = TaskDialog(title)
    dialog.MainInstruction = message
    dialog.Show()

# Function to prompt the user with a yes/no question
def ask_user_first_column_notes():
    dialog = TaskDialog("First Column for Notes")
    dialog.MainInstruction = "Is the first column being used for sheet notes?"
    dialog.CommonButtons = TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No
    result = dialog.Show()
    if result == TaskDialogResult.Yes:
        return True
    else:
        return False

# Calculate the grid shift correction
def calculate_grid_shift_correction(left_gutter_width):
    # Convert the shift from inches to internal units (Revit uses feet; 1 inch = 1/12 feet)
    grid_shift_correction = (8 + (39/256.0)) / 12  # Correction value in feet
    
    # Correct the left gutter width by subtracting the grid shift to move the grid to the left
    corrected_left_gutter_width = left_gutter_width - grid_shift_correction
   
    return corrected_left_gutter_width

# Function to draw grid lines on the sheet

def draw_grid_lines(doc, view, grid_width, grid_height, cell_width, cell_height, left_gutter_width, right_gutter_width, bottom_gutter_height, top_gutter_height, line_style_name):
    # Start a new transaction
    t = Transaction(doc, 'Draw Grid Lines')
    t.Start()
    
    # Debugging: Print initial parameters
    # output.print_md("**Grid Width:** {}".format(grid_width))
    # output.print_md("**Grid Height:** {}".format(grid_height))
    # output.print_md("**Line Style Name:** {}".format(line_style_name))

    # Find the line style by name
    categories = doc.Settings.Categories
    line_styles_category = categories.get_Item(BuiltInCategory.OST_Lines)
    line_style_id = None  # Initialize line_style_id to None
    for gs in line_styles_category.SubCategories:
        if gs.Name == line_style_name:
            line_style_id = gs.Id  # Assign the ElementId of the line style to line_style_id
            break
    
    # Debugging: Check if line style was found
    # if line_style_id:
    #     output.print_md("**Line Style Found:** Yes, ID = {}".format(line_style_id))
    # else:
    #     output.print_md("**Line Style Found:** No")
    #     show_alert('Error', "Line style '{}' not found.".format(line_style_name))
    #     return
    
    # Draw vertical lines
    for i in range(grid_width + 1):
        start_point = XYZ(left_gutter_width + i * cell_width, bottom_gutter_height, 0)
        end_point = XYZ(left_gutter_width + i * cell_width, bottom_gutter_height + grid_height * cell_height, 0)
        line = Line.CreateBound(start_point, end_point)
        detail_line = doc.Create.NewDetailCurve(view, line)
        detail_line.LineStyle = doc.GetElement(line_style_id)
        # output.print_md("**LineStyle Applied to Detail Line:** {}".format(detail_line.LineStyle.Name))
    
    # Debugging: Print after drawing vertical lines
    # output.print_md("**Vertical Lines Drawn:** {}".format(grid_width + 1))
    
    # Draw horizontal lines
    for j in range(grid_height + 1):
        start_point = XYZ(left_gutter_width, bottom_gutter_height + j * cell_height, 0)
        end_point = XYZ(left_gutter_width + grid_width * cell_width, bottom_gutter_height + j * cell_height, 0)
        line = Line.CreateBound(start_point, end_point)
        detail_line = doc.Create.NewDetailCurve(view, line)
        detail_line.LineStyle = doc.GetElement(line_style_id)
        # output.print_md("**LineStyle Applied to Detail Line:** {}".format(detail_line.LineStyle.Name))
    
    # Debugging: Print after drawing horizontal lines
    # output.print_md("**Horizontal Lines Drawn:** {}".format(grid_height + 1))

    # Commit the transaction
    t.Commit()


# Function to renumber viewports based on cell position
def renumber_viewports(doc, viewports, grid_width, grid_height, cell_width, cell_height, left_gutter_width, bottom_gutter_height, use_first_column):

    # Start a new transaction
    t = Transaction(doc, 'Renumber Viewports')
    t.Start()

    # Calculate effective grid width considering the use of the first column for notes
    effective_grid_width = grid_width - 1 if use_first_column else grid_width
    
    # Dictionary to hold the new numbers and their corresponding viewports
    new_numbers = defaultdict(list)
    
    # Assign dummy numbers to all viewports to avoid clashes during renumbering
    for i, vp in enumerate(viewports):
        detail_number_param = vp.LookupParameter("Detail Number")
        if detail_number_param and not detail_number_param.IsReadOnly:
            detail_number_param.Set("Dummy{}".format(i))
        else:
            print("Detail Number parameter is read-only or not found for viewport ID: {}".format(vp.Id))
            t.RollBack()
            return

    for vp in viewports:
        vp_outline = vp.GetBoxOutline()
        min_point = vp_outline.MinimumPoint
        max_point = vp_outline.MaximumPoint

        vp_top_right = XYZ(max_point.X, max_point.Y, 0)

        # Calculate the viewport's column based on its X position, using the corrected left gutter width
        column = int((vp_top_right.X - left_gutter_width) // cell_width)
        # Calculate the viewport's row based on its Y position
        row = int((vp_top_right.Y - bottom_gutter_height) // cell_height)

        # Adjust the column index if the first column is used for notes
        if use_first_column:
            column -= 1  # Shift column index to the left

        # Skip the viewport if it's in the notes column or outside the grid bounds
        if column < 0 or column >= effective_grid_width or row < 0 or row >= grid_height:
            continue  # Skip this viewport

        # Calculate the new number considering the adjusted grid width
        new_number = (effective_grid_width - 1 - column) * grid_height + (grid_height - 1 - row) +1
        new_numbers[new_number].append(vp)

        # Apply new numbers, marking duplicates with "DUP "
        for new_number, vps in new_numbers.items():
            for i, vp in enumerate(vps):
                detail_number_param = vp.LookupParameter("Detail Number")
                if detail_number_param and not detail_number_param.IsReadOnly:
                    if i == 0:  # First viewport gets the new number
                        detail_number_param.Set(str(new_number))
                    else:  # Subsequent duplicates get "DUP " prefix, if not already present
                        current_number = detail_number_param.AsString()
                        # Check if "DUP " is already present at the beginning of the current number
                        if not current_number.startswith("DUP "):
                            detail_number_param.Set("DUP " + current_number)
                        else:
                            # If "DUP " is already present, we don't add another prefix
                            # Optionally, you could update the logic here if you need to handle these cases differently
                            pass

    t.Commit()

# Get the current Revit document.
doc = __revit__.ActiveUIDocument.Document

# Get the active view.
active_view = doc.ActiveView

# Check if the active view is a sheet.
if isinstance(active_view, ViewSheet):
    output = script.get_output()

    # Define the sheet size in feet (30"x42" sheet with left and right gutters).
    sheet_width_in_inches = 42
    left_gutter_width_in_inches = 2.75
    
    right_gutter_width_in_inches = 4.61328125 #4 + 157/256.0
    sheet_height_in_inches = 30
    bottom_gutter_height_in_inches = 127/256.0  # Added bottom gutter height in inches.
    top_gutter_height_in_inches = 1/2.0  # Added top gutter height in inches.
    left_gutter_width = inches_to_feet(left_gutter_width_in_inches)
    

    right_gutter_width = inches_to_feet(right_gutter_width_in_inches)
    bottom_gutter_height = inches_to_feet(bottom_gutter_height_in_inches)  # Convert bottom gutter to feet.
    top_gutter_height = inches_to_feet(top_gutter_height_in_inches)  # Convert top gutter to feet.
    line_type_name = "01 - Ultra Light Red"

    # Define the grid size (6 cells wide by 5 cells high).
    grid_width = 6
    grid_height = 5

    # Calculate the cell size in feet, subtracting gutter widths from the total sheet width.
    cell_width = inches_to_feet(.02734375) + (inches_to_feet(sheet_width_in_inches) - (left_gutter_width + right_gutter_width)) / grid_width
    # Calculate the cell height in feet, subtracting gutter heights from the total sheet height.
    cell_height = (inches_to_feet(sheet_height_in_inches) - (bottom_gutter_height + top_gutter_height)) / grid_height

    # Ensure that the cell size is being calculated correctly.
    assert cell_width > 0, "Cell width must be positive"
    assert cell_height > 0, "Cell height must be positive"

    # fix it for some reason...
    left_gutter_width = calculate_grid_shift_correction(left_gutter_width)

    # Get all viewports on the sheet.
    # viewports = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Viewports).WhereElementIsNotElementType().ToElements()

    def printViewportInfo():
        # draw_grid_lines(doc, active_view, grid_width, grid_height, cell_width, cell_height, left_gutter_width, right_gutter_width, bottom_gutter_height, top_gutter_height, line_type_name)

        viewports = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Viewports).WhereElementIsNotElementType().ToElements()

        # Print information about each viewport.
        output.print_md("**Grid width:** {}".format(grid_width))
        output.print_md("**grid_height:** {}".format(grid_height))
        output.print_md("**cell_width:** {}".format(cell_width))
        output.print_md("**cell_height:** {}".format(cell_height))
        for vp in viewports:
            # Get the view associated with the viewport.
            view = doc.GetElement(vp.ViewId)

            # Filter out Legends.
            if view.ViewType == ViewType.Legend:
                continue

            # Get the viewport's outline.
            vp_outline = vp.GetBoxOutline()
            vp_outline_max = vp_outline.MaximumPoint

            # Calculate the top-right coordinates relative to the sheet's origin, including gutters.
            top_right_x = vp_outline_max.X - left_gutter_width
            # Adjust top_right_y to account for bottom gutter.
            top_right_y = vp_outline_max.Y - bottom_gutter_height

            # Calculate the viewport's position in the grid.
            grid_x = grid_width - int(top_right_x // cell_width) - 1
            # Adjust calculation for grid_y to account for bottom gutter.
            grid_y = grid_height - int(top_right_y // cell_height) - 1

            # Adjust the grid position if the viewport is in the gutter space.
            if top_right_x < 0:
                grid_x = grid_width  # This indicates the viewport is in the left gutter.
            elif top_right_x > cell_width * grid_width:
                grid_x = -1  # This indicates the viewport is in the right gutter.
            if top_right_y < 0:
                grid_y = grid_height  # This indicates the viewport is in the bottom gutter.
            elif top_right_y > cell_height * grid_height:
                grid_y = -1  # This indicates the viewport is in the top gutter.
            

            output.print_md("**Viewport:** {} (Id: {})".format(view.Name, vp.Id))
            output.print_md("**Top-Right Coordinates:** X: {:.2f}', Y: {:.2f}'".format(top_right_x + left_gutter_width, top_right_y))
            output.print_md("**Grid Position:** Column {}, Row {}".format(grid_x , grid_y + 1))

    # Ask the user if the first column is used for sheet notes
    use_first_column = ask_user_first_column_notes()
    
    draw_grid_lines(doc, active_view, grid_width, grid_height, cell_width, cell_height, left_gutter_width, right_gutter_width, bottom_gutter_height, top_gutter_height, line_type_name)

    # Get all viewports on the active sheet
    viewports = [vp for vp in FilteredElementCollector(doc, active_view.Id).OfClass(Viewport)]

    # Renumber viewports
    renumber_viewports(doc, viewports, grid_width, grid_height, cell_width, cell_height, left_gutter_width, bottom_gutter_height, use_first_column)


else:
    show_alert("ERROR","The active view is not a sheet.")