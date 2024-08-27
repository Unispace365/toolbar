# emea_setup_dialog.py

import clr
clr.AddReference('PresentationCore')
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')

from System.Windows import Window, WindowStartupLocation, SizeToContent, Thickness
from System.Windows.Controls import StackPanel, ComboBox, Button, TextBlock
from System.Windows.Media import Brushes

class EmeaSetupDialog(Window):
    def __init__(self):
        self.Title = 'EMEA Project Setup'
        self.Width = 400
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.SizeToContent = SizeToContent.Height
        self.Background = Brushes.WhiteSmoke

        self.main_stack = StackPanel()
        self.main_stack.Margin = Thickness(20)

        # Country selection
        self.country_label = TextBlock()
        self.country_label.Text = "Select EMEA Country:"
        self.country_label.Margin = Thickness(0, 0, 0, 5)
        self.main_stack.Children.Add(self.country_label)

        self.country_combo = ComboBox()
        countries = ["UK", "ES", "IT", "FR", "DE"]  # Based on the screenshots
        for country in countries:
            self.country_combo.Items.Add(country)
        self.country_combo.Margin = Thickness(0, 0, 0, 20)
        self.country_combo.MinWidth = 200
        self.main_stack.Children.Add(self.country_combo)

        # Language selection
        self.language_label = TextBlock()
        self.language_label.Text = "Select Project Language:"
        self.language_label.Margin = Thickness(0, 0, 0, 5)
        self.main_stack.Children.Add(self.language_label)

        self.language_combo = ComboBox()
        languages = ["English", "French", "German", "Italian", "Spanish"]
        for language in languages:
            self.language_combo.Items.Add(language)
        self.language_combo.Margin = Thickness(0, 0, 0, 30)
        self.language_combo.MinWidth = 200
        self.main_stack.Children.Add(self.language_combo)

        # Submit button
        self.submit_button = Button()
        self.submit_button.Content = "Submit"
        self.submit_button.Click += self.on_submit
        self.submit_button.Padding = Thickness(20, 10, 20, 10)
        self.submit_button.Background = Brushes.DodgerBlue
        self.submit_button.Foreground = Brushes.White
        self.submit_button.BorderThickness = Thickness(0)
        self.main_stack.Children.Add(self.submit_button)

        self.Content = self.main_stack

    def on_submit(self, sender, e):
        if self.country_combo.SelectedItem and self.language_combo.SelectedItem:
            self.DialogResult = True
        else:
            # TODO: Show error message if selections are not made
            pass
        self.Close()

def show_dialog():
    dialog = EmeaSetupDialog()
    result = dialog.ShowDialog()
    if result:
        return {
            "country": dialog.country_combo.SelectedItem,
            "language": dialog.language_combo.SelectedItem
        }
    else:
        return None