# script.py

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
from pyrevit import revit, forms
import emea_setup_dialog

def get_families_to_remove(selected_country):
    # Define families to remove for each country
    families_by_country = {
        "UK": [
            # "UNI_WALL_UK_PT01_122MM(2X12.5PB/72/2X12.5PB)",
            # "UNI_WALL_UK_PT02_100MM(2X12.5PB/50/2X12.5PB)",
            # "UNI_WALL_UK_PT03_97MM(2X12.5PB/72)",
            # "UNI_WALL_UK_PT04_75MM(2X12.5PB/50)",
            # "UNI_WALL_UK_PT05_97MM(12.5PB/72/12.5PB)",
            # "UNI_WALL_UK_PT06_75MM(12.5PB/50/12.5PB)",
            # "UNI_WALL_UK_PT07_84.5MM(12.5PB/72)",
            # "UNI_WALL_UK_PT08_62.5MM(12.5PB/50)",
            # "UNI_WALL_UK_PT10_122MM(2X12.5PB/72/2X12.5PB)FR60",
            # "UNI_WALL_UK_PT11_100MM(2X12.5PB/50/2X12.5PB)FR60",
            # "UNI_WALL_UK_PT12_97MM(2X12.5PB/72) FR60",
            # "UNI_WALL_UK_PT13_75MM(2X12.5PB/50) FR60",
            # "UNI_WALL_UK_PT14_122MM(2X12.5PB/72/2X12.5PB)FR60",
            # "UNI_WALL_UK_PT15_100MM(2X12.5PB/50/2X12.5PB)FR60",
            # "UNI_WALL_UK_PT20_122MM(2X12.5MR/72/2X12.5MR)",
            # "UNI_WALL_UK_PT21_100MM(2X12.5MR/50/2X12.5MR)",
            # "UNI_WALL_UK_PT22_97MM(2X12.5MR/72)",
            # "UNI_WALL_UK_PT23_75MM(2X12.5MR/50)",
            # "UNI_WALL_UK_PT24_122MM(2X12.5MR/72/2X12.5PB)",
            # "UNI_WALL_UK_PT25_100MM(2X12.5MR/50/2X12.5PB)",
            # "UNI_WALL_UK_PT30_122MM(2X12.5MR/72/2X12.5PB)",
            # "UNI_WALL_UK_PT31_100MM(2X12.5MR/50/2X12.5PB)",
            # "UNI_WALL_UK_PT40 120MM 4X 6MM  GRG_72_4X 6MM  GRG 2"
        ],
        "ES": [
            # "UNI_WALL_ES_PT01_120MM(2X12.5PB/70/2X12.5PB)",
            # "UNI_WALL_ES_PT03_95MM(2X12.5PB/70)",
            # "UNI_WALL_ES_PT10_120MM(2X12.5PB/70/2X12.5PB)FR60",
            # "UNI_WALL_ES_PT20_120MM(2X12.5MR/70/2X12.5MR)"
        ],
        "IT": [
            # "UNI_WALL_IT_2A2_100MM_STUDPARTITION",
            # "UNI_WALL_IT_2A2_125MM_STUDPARTITION",
            # "UNI_WALL_IT_2A2_150MM_STUDPARTITION",
            # "UNI_WALL_IT_A1A2/2A2_125MM_STUDPARTITION",
            # "UNI_WALL_IT_A1A2/2A2_150MM_STUDPARTITION",
            # "UNI_WALL_IT_A1A2/2A1_125MM_STUDPARTITION",
            # "UNI_WALL_IT_A1A2/2A1_150MM_STUDPARTITION",
            # "UNI_WALL_IT_A1A2_100MM_STUDPARTITION"
        ],
        "FR": [],  # Add French-specific families if any
        "DE": []   # Add German-specific families if any
    }
    
    # Create a list of all families to remove except those for the selected country
    families_to_remove = []
    for country, families in families_by_country.items():
        if country != selected_country:
            families_to_remove.extend(families)
    
    return families_to_remove

def get_legends_to_remove(selected_country):
    # Define legend prefixes to remove for each country
    legend_prefixes_by_country = {
        "ES": "ES_SHEET_IA",
        "IT": "IT_SHEET_IA",
        "UK": "UK_SHEET_IA",  # Add this if UK has a specific prefix
        "FR": "FR_SHEET_IA",  # Add this if FR has a specific prefix
        "DE": "DE_SHEET_IA",  # Add this if DE has a specific prefix
    }
    
    # Create a list of all legend prefixes to remove except those for the selected country
    prefixes_to_remove = [prefix for country, prefix in legend_prefixes_by_country.items() if country != selected_country]
    
    return prefixes_to_remove

def delete_country_specific_content(doc, selected_country):
    families_to_remove = get_families_to_remove(selected_country)
    legend_prefixes_to_remove = get_legends_to_remove(selected_country)
    countries_to_remove = ["UK", "ES", "IT", "FR", "DE"]
    countries_to_remove.remove(selected_country)

    elements_to_delete = []

    # Collect families to delete
    family_collector = DB.FilteredElementCollector(doc).OfClass(DB.Family)
    for family in family_collector:
        if family.Name in families_to_remove:
            elements_to_delete.append(family.Id)
            print("Family marked for deletion: {}".format(family.Name))

    # Collect view templates and legends to delete
    view_collector = DB.FilteredElementCollector(doc).OfClass(DB.View)
    for view in view_collector:
        if view.IsTemplate and any("COUNTRY_{}".format(country) in view.Name for country in countries_to_remove):
            elements_to_delete.append(view.Id)
            print("View template marked for deletion: {}".format(view.Name))
        elif view.ViewType == DB.ViewType.Legend:
            if any(view.Name.startswith(prefix) for prefix in legend_prefixes_to_remove):
                elements_to_delete.append(view.Id)
                print("Legend marked for deletion: {}".format(view.Name))

    # Delete collected elements
    with revit.Transaction("Remove Country-Specific Content"):
        for element_id in elements_to_delete:
            try:
                element = doc.GetElement(element_id)
                if element:
                    doc.Delete(element_id)
                    print("Successfully deleted: {}".format(element.Name))
                else:
                    print("Element not found: {}".format(element_id))
            except Exception as e:
                print("Failed to delete element {}: {}".format(element_id, str(e)))

    print("Country-specific content removal completed.")
    print("Total elements deleted: {}".format(len(elements_to_delete)))
    
def main():
    try:
        # Show the custom dialog
        result = emea_setup_dialog.show_dialog()
        if result:
            country = result["country"]
            language = result["language"]

            # Confirm with the user
            confirmation = forms.alert(
                "This will remove content for other EMEA countries. Continue?",
                yes=True, no=True
            )
            if not confirmation:
                script.exit()

            # Delete country-specific content
            delete_country_specific_content(revit.doc, country)

            # TODO: Implement logic to select type for "Uni_Annotation_Legend_General-Notes" based on language

            forms.alert("EMEA Project Setup completed successfully!", title="Success")
    except Exception as e:
        import traceback
        error_msg = "An error occurred:\n{}\n\nTraceback:\n{}".format(str(e), traceback.format_exc())
        forms.alert(error_msg, title="Error")

if __name__ == "__main__":
    main()