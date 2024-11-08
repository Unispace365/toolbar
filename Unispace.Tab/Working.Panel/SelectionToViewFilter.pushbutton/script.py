# -*- coding: utf-8 -*-
__title__ = 'Create Filter From Element'
__author__ = 'Matt Vogel'
__doc__ = 'Select an element to create view filters based on its parameters.'

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from System.Windows.Forms import (
    Form, CheckedListBox, Button, Label, DialogResult, 
    DockStyle, AnchorStyles, CheckState, ListBox,
    TextBox, Panel
)
from System.Drawing import Point, Size, Font, FontStyle, Color
from pyrevit import revit, DB

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

class ParameterSelectorForm(Form):
    def __init__(self, element, parameters):
        self.element = element
        self.parameters = parameters
        self.InitializeComponent()
        self.populate_element_info()
        self.populate_parameter_list()

    def InitializeComponent(self):
        self.Text = 'Select Parameters for Filter'
        self.Size = Size(600, 700)
        self.MinimumSize = Size(500, 500)

        # Element Info Panel
        self.infoPanel = Panel()
        self.infoPanel.Location = Point(10, 10)
        self.infoPanel.Size = Size(580, 120)
        self.infoPanel.BackColor = Color.White
        self.Controls.Add(self.infoPanel)

        # Element Info Title
        self.infoTitle = Label()
        self.infoTitle.Text = "Element Information"
        self.infoTitle.Font = Font(self.infoTitle.Font, FontStyle.Bold)
        self.infoTitle.Location = Point(10, 10)
        self.infoTitle.Size = Size(560, 20)
        self.infoPanel.Controls.Add(self.infoTitle)

        # Element Info Labels
        self.categoryLabel = Label()
        self.categoryLabel.Location = Point(10, 35)
        self.categoryLabel.Size = Size(560, 20)
        self.infoPanel.Controls.Add(self.categoryLabel)

        self.idLabel = Label()
        self.idLabel.Location = Point(10, 55)
        self.idLabel.Size = Size(560, 20)
        self.infoPanel.Controls.Add(self.idLabel)

        self.familyLabel = Label()
        self.familyLabel.Location = Point(10, 75)
        self.familyLabel.Size = Size(560, 20)
        self.infoPanel.Controls.Add(self.familyLabel)

        self.typeLabel = Label()
        self.typeLabel.Location = Point(10, 95)
        self.typeLabel.Size = Size(560, 20)
        self.infoPanel.Controls.Add(self.typeLabel)

        # Parameters Label
        self.paramLabel = Label()
        self.paramLabel.Text = 'Select parameters to use in filter:'
        self.paramLabel.Location = Point(10, 140)
        self.paramLabel.Size = Size(580, 20)
        self.Controls.Add(self.paramLabel)

        # Create CheckedListBox for parameters
        self.checkedListBox = CheckedListBox()
        self.checkedListBox.Location = Point(10, 170)
        self.checkedListBox.Size = Size(580, 430)
        self.checkedListBox.Anchor = (AnchorStyles.Top | AnchorStyles.Left | 
                                    AnchorStyles.Bottom | AnchorStyles.Right)
        self.Controls.Add(self.checkedListBox)

        # Create buttons
        self.btnOK = Button()
        self.btnOK.Text = 'Create Filter'
        self.btnOK.DialogResult = DialogResult.OK
        self.btnOK.Location = Point(410, 620)
        self.btnOK.Anchor = (AnchorStyles.Bottom | AnchorStyles.Right)
        self.Controls.Add(self.btnOK)

        self.btnCancel = Button()
        self.btnCancel.Text = 'Cancel'
        self.btnCancel.DialogResult = DialogResult.Cancel
        self.btnCancel.Location = Point(490, 620)
        self.btnCancel.Anchor = (AnchorStyles.Bottom | AnchorStyles.Right)
        self.Controls.Add(self.btnCancel)

    def populate_element_info(self):
        try:
            category = self.element.Category.Name if self.element.Category else "N/A"
            element_id = self.element.Id.IntegerValue
            family_name = self.element.Symbol.Family.Name if hasattr(self.element, 'Symbol') else "N/A"
            type_name = self.element.Name

            self.categoryLabel.Text = "Category: {}".format(category)
            self.idLabel.Text = "Element ID: {}".format(element_id)
            self.familyLabel.Text = "Family Name: {}".format(family_name)
            self.typeLabel.Text = "Type Name: {}".format(type_name)
        except Exception as e:
            print("Error populating element info: {}".format(str(e)))

    def populate_parameter_list(self):
        try:
            # Clear existing items
            self.checkedListBox.Items.Clear()
            
            # Add parameters to the checked list box
            for param in self.parameters:
                display_text = "{} ({}) - Current Value: {}".format(
                    param['name'],
                    param['parameter_type'],
                    param['value']
                )
                self.checkedListBox.Items.Add(display_text, CheckState.Unchecked)
        except Exception as e:
            print("Error populating parameter list: {}".format(str(e)))

    def get_selected_parameters(self):
        selected_indices = self.checkedListBox.CheckedIndices
        return [self.parameters[i] for i in selected_indices]

def get_parameter_value(param):
    """Get parameter value based on storage type"""
    if not param:
        return "Parameter not found"
    
    try:
        if param.StorageType == StorageType.String:
            return param.AsString() or "No Value"
        elif param.StorageType == StorageType.Integer:
            return str(param.AsInteger())
        elif param.StorageType == StorageType.Double:
            return str(param.AsDouble())
        elif param.StorageType == StorageType.ElementId:
            return str(param.AsElementId().IntegerValue)
        else:
            return param.AsValueString() or "No Value"
    except:
        return "Error getting value"

def get_parameter_info(param):
    """Get detailed information about a parameter"""
    try:
        param_info = dict(
            name = param.Definition.Name,
            parameter = param,  # Store the actual parameter object
            category = str(param.Definition.ParameterGroup),
            parameter_type = str(param.Definition.ParameterType),
            storage_type = str(param.StorageType),
            is_shared = param.IsShared,
            element_id = param.Id.IntegerValue,
            value = get_parameter_value(param)
        )
        return param_info
    except Exception as e:
        print("Error getting parameter info: {}".format(str(e)))
        return None

def get_all_parameters(element):
    """Get all parameters from both instance and type"""
    param_data = []
    
    try:
        # Get instance parameters
        for param in element.Parameters:
            param_info = get_parameter_info(param)
            if param_info:
                param_data.append(param_info)
        
        # Get type parameters
        element_type = doc.GetElement(element.GetTypeId())
        if element_type:
            for param in element_type.Parameters:
                param_info = get_parameter_info(param)
                if param_info:
                    param_info['name'] = "Type: " + param_info['name']
                    param_data.append(param_info)
    except Exception as e:
        print("Error getting parameters: {}".format(str(e)))
    
    return sorted(param_data, key=lambda x: x['name'])

def main():
    # Get selected elements
    selection = uidoc.Selection
    selected_ids = selection.GetElementIds()
    
    if not selected_ids:
        TaskDialog.Show("Selection Error", "Please select exactly one element.")
        return
    
    if len(selected_ids) > 1:
        TaskDialog.Show("Selection Error", 
                       "Please select exactly one element. Multiple elements are currently selected.")
        return
    
    # Get element and its parameters
    element = doc.GetElement(selected_ids[0])
    parameters = get_all_parameters(element)
    
    if not parameters:
        TaskDialog.Show("Error", "No parameters found for the selected element.")
        return
    
    # Show parameter selector form
    param_form = ParameterSelectorForm(element, parameters)
    result = param_form.ShowDialog()
    
    if result == DialogResult.OK:
        selected_parameters = param_form.get_selected_parameters()
        if selected_parameters:
            TaskDialog.Show("Success", "Selected {} parameters. Filter creation coming in next version!".format(len(selected_parameters)))
        else:
            TaskDialog.Show("Warning", "No parameters were selected.")

if __name__ == '__main__':
    main()