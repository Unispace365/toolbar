# -*- coding: utf-8 -*-
__title__ = 'Set Opacity 80%'
__author__ = 'Matt Vogel'
__doc__ = 'Sets the opacity of selected elements to 80% in the current view.'

from pyrevit import revit, DB
from Autodesk.Revit.DB import Transaction, OverrideGraphicSettings, Color

# Get the current Revit document and active view
doc = revit.doc
active_view = doc.ActiveView

def set_opacity_for_elements(elements, opacity=20):
    with Transaction(doc, 'Set Opacity for Selected Elements') as t:
        t.Start()
        
        for element in elements:
            # Create new override settings
            override = OverrideGraphicSettings()
            
            # Set the transparency (opposite of opacity)
            transparency = 100 - opacity
            override.SetSurfaceTransparency(transparency)
            
            # Apply the override to the element in the current view
            active_view.SetElementOverrides(element.Id, override)
        
        t.Commit()

# Get the currently selected elements
selection = revit.get_selection()

if selection:
    # Set opacity for selected elements
    set_opacity_for_elements(selection)
    # print("{0} elements have been set to 80% opacity in the current view.".format(len(selection)))
else:
    print("No elements selected. Please select elements and run the script again.")