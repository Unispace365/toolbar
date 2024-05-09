# -*- coding: utf-8 -*-
__title__ = 'Workset Setup'
__author__ = 'Matt Vogel'
__doc__ = 'Creates worksets for worksharing files.'
from pyrevit import revit, DB

# Initialize Document
doc = revit.doc

# Define your list of new workset names here
new_workset_names = ["00_BASEBUILD", "01_FLOOR", "02_WALL", "03_JOINERY", "04_FFE", "05_ENTOURAGE", "Z_Linked_ARCH", "Z_Linked_MEP", "Z_Linked_STRUC", "Z_Linked_CAD"]

# Names of default worksets to rename
default_worksets_to_rename = {
    "Shared Levels and Grids": "06_MASSING",
    "Workset1": "99_LEVELS & GRIDS"
}


def create_workset(name):
    """Create a new workset if it does not already exist."""
    if DB.WorksetTable.IsWorksetNameUnique(doc, name):
        with revit.Transaction("Create Workset"):
            new_workset = DB.Workset.Create(doc, name)
        print("Created workset: {}".format(name))
        return new_workset
    else:
        print("Workset '{}' already exists.".format(name))
        return None

def rename_workset(old_name, new_name):
    """Rename an existing workset using the correct API method."""
    worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)
    for ws in worksets:
        if ws.Name == old_name:
            with revit.Transaction("Rename Workset"):
                try:
                    DB.WorksetTable.RenameWorkset(doc, ws.Id, new_name)
                    print("Renamed '{}' to '{}'".format(old_name, new_name))
                except Exception as e:
                    print("Failed to rename '{}': {}".format(old_name, str(e)))
            return
    print("Workset '{}' not found.".format(old_name))

# Execute workset creation and renaming
for name in new_workset_names:
    create_workset(name)

for old_name, new_name in default_worksets_to_rename.items():
    rename_workset(old_name, new_name)