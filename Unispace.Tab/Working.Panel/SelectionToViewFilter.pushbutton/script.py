# -*- coding: utf-8 -*-
__title__ = 'Get Element Info'
__author__ = 'Matt Vogel'
__doc__ = 'Gets information from selected element to help create rule-based filters.'

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
from pyrevit import revit, DB
from System.Collections.Generic import List

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

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

def get_built_in_param_name(param):
    """Try to get built-in parameter name if it exists"""
    try:
        if param.Definition.BuiltInParameter != BuiltInParameter.INVALID:
            return str(param.Definition.BuiltInParameter)
    except:
        pass
    return "Not built-in"

def get_parameter_info(param):
    """Get detailed information about a parameter"""
    try:
        param_info = dict(
            name = param.Definition.Name,
            built_in_name = get_built_in_param_name(param),
            category = str(param.Definition.ParameterGroup),
            parameter_type = str(param.Definition.ParameterType),
            storage_type = str(param.StorageType),
            is_shared = param.IsShared,
            guid = str(param.GUID) if param.IsShared else "Not a shared parameter",
            element_id = param.Id.IntegerValue,
            value = get_parameter_value(param)
        )
        return param_info
    except Exception as e:
        return "Error getting parameter info: {0}".format(str(e))

def get_all_parameters(element):
    """Get all parameters from both instance and type"""
    param_data = []
    
    # Get instance parameters
    for param in element.Parameters:
        param_info = get_parameter_info(param)
        if isinstance(param_info, dict):
            param_data.append(param_info)
    
    # Get type parameters
    element_type = doc.GetElement(element.GetTypeId())
    if element_type:
        for param in element_type.Parameters:
            param_info = get_parameter_info(param)
            if isinstance(param_info, dict):
                param_info['name'] = "Type: " + param_info['name']  # Prefix type parameters
                param_data.append(param_info)
    
    return param_data

def display_element_info(element):
    """Display comprehensive information about the element"""
    
    # Basic element information
    info_strings = [
        "Basic Element Information:",
        "Category: {0}".format(element.Category.Name),
        "Element ID: {0}".format(element.Id.IntegerValue),
        "UniqueId: {0}".format(element.UniqueId),
        "Family Name: {0}".format(element.Symbol.Family.Name if hasattr(element, 'Symbol') else "N/A"),
        "Type Name: {0}".format(element.Name),
        "\nAll Available Parameters:",
        "-" * 50
    ]
    
    # Get all parameters
    parameters = get_all_parameters(element)
    
    # Sort parameters by name for better readability
    parameters.sort(key=lambda x: x['name'])
    
    # Add parameter information to display strings
    for param_info in parameters:
        param_strings = [
            "\nParameter: {0}".format(param_info['name']),
            "Built-in Parameter: {0}".format(param_info['built_in_name']),
            "Category: {0}".format(param_info['category']),
            "Parameter Type: {0}".format(param_info['parameter_type']),
            "Storage Type: {0}".format(param_info['storage_type']),
            "Is Shared: {0}".format(param_info['is_shared']),
            "GUID: {0}".format(param_info['guid']),
            "Element ID: {0}".format(param_info['element_id']),
            "Value: {0}".format(param_info['value']),
            "-" * 50
        ]
        info_strings.extend(param_strings)
    
    # Display the information in a TaskDialog
    dialog = TaskDialog("Element Information")
    dialog.MainInstruction = "Information for {0}".format(element.Category.Name)
    dialog.MainContent = "\n".join(info_strings)
    dialog.Show()

def main():
    # Get selected elements
    selection = uidoc.Selection
    selected_ids = selection.GetElementIds()
    
    # Convert to list for checking length
    selected_elements = [doc.GetElement(element_id) for element_id in selected_ids]
    
    if not selected_elements:
        TaskDialog.Show("Selection Error", "Please select exactly one element.")
        return
    
    if len(selected_elements) > 1:
        TaskDialog.Show("Selection Error", 
                       "Please select exactly one element. Multiple elements are currently selected.")
        return
    
    # Get information for the single selected element
    element = selected_elements[0]
    display_element_info(element)

if __name__ == '__main__':
    main()