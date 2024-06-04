import clr
clr.AddReference('PresentationCore')
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')

from System import Uri
from System.Windows import Application, Window, Thickness, WindowStartupLocation, SizeToContent, TextWrapping
from System.Windows.Controls import StackPanel, Image, Button, CheckBox, TextBlock, DockPanel, Dock
from System.Windows.Media.Imaging import BitmapImage
from pyrevit import forms, script
import os

# Get the output object
output = script.get_output()

class CustomDialog(Window):
    def __init__(self):
        self.Title = 'Custom Popup'
        self.Width = 400
        self.MaxWidth = 400
        self.Height = 600
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.SizeToContent = SizeToContent.Height  # Adjust the height to fit content
        
        # Main Stack Panel
        self.main_stack = StackPanel()
        
        # Text Block 1
        self.textblock1 = TextBlock()
        self.textblock1.Text = ("This will renumber all rooms in the model based on the NY 10' grid system. "
                                "Room codes are determined based on alphanumeric coordinate system within the 10' grid interval. "
                                "Columns are alphabetical and rows are numeric")
        self.textblock1.Margin = Thickness(10)
        self.textblock1.MaxWidth = 380  # Set max width to ensure wrapping within window width
        self.textblock1.TextWrapping = TextWrapping.Wrap  # Enable text wrapping
        self.main_stack.Children.Add(self.textblock1)
        
        # Image 1
        self.image1 = Image()
        self.image1.Source = BitmapImage(Uri(os.path.join(os.path.dirname(__file__), 'grid.png')))
        self.image1.Height = 200
        self.image1.Margin = Thickness(10)
        self.main_stack.Children.Add(self.image1)
        
        # Text Block 2
        self.textblock2 = TextBlock()
        self.textblock2.Text = "This is the second image:"
        self.textblock2.Margin = Thickness(10)
        self.textblock2.MaxWidth = 380  # Set max width to ensure wrapping within window width
        self.textblock2.TextWrapping = TextWrapping.Wrap  # Enable text wrapping
        self.main_stack.Children.Add(self.textblock2)
        
        # Image 2
        self.image2 = Image()
        self.image2.Source = BitmapImage(Uri(os.path.join(os.path.dirname(__file__), 'name_template.png')))
        self.image2.Height = 200
        self.image2.Margin = Thickness(10)
        self.main_stack.Children.Add(self.image2)
        
        # Checkboxes with TextBlock for wrapping
        self.checkBox1 = CheckBox()
        self.checkBox1.Margin = Thickness(10)
        self.checkBox1.MaxWidth = 380  # Set max width to ensure wrapping within window width
        self.checkBox1.Content = TextBlock(Text="Does this project have work on multiple floors? If yes the level number will be added to each room name.",
                                           TextWrapping=TextWrapping.Wrap)
        self.main_stack.Children.Add(self.checkBox1)
        
        self.checkBox2 = CheckBox()
        self.checkBox2.Margin = Thickness(10)
        self.checkBox2.MaxWidth = 380  # Set max width to ensure wrapping within window width
        self.checkBox2.Content = TextBlock(Text="Create the red 10' grid",
                                           TextWrapping=TextWrapping.Wrap)
        self.main_stack.Children.Add(self.checkBox2)
        
        # Button Panel
        self.button_panel = DockPanel()
        self.button_panel.Margin = Thickness(10)
        
        # OK Button
        self.okButton = Button()
        self.okButton.Content = 'OK'
        self.okButton.Width = 100
        self.okButton.Margin = Thickness(5)
        self.okButton.Click += self.on_ok
        DockPanel.SetDock(self.okButton, Dock.Left)
        self.button_panel.Children.Add(self.okButton)
        
        # Cancel Button
        self.cancelButton = Button()
        self.cancelButton.Content = 'Cancel'
        self.cancelButton.Width = 100
        self.cancelButton.Margin = Thickness(5)
        self.cancelButton.Click += self.on_cancel
        DockPanel.SetDock(self.cancelButton, Dock.Right)
        self.button_panel.Children.Add(self.cancelButton)
        
        self.main_stack.Children.Add(self.button_panel)
        self.Content = self.main_stack

    def on_ok(self, sender, e):
        self.DialogResult = True
        self.Close()

    def on_cancel(self, sender, e):
        self.DialogResult = False
        self.Close()

# Create and show the dialog
dialog = CustomDialog()
result = dialog.ShowDialog()

if result:
    option1 = dialog.checkBox1.IsChecked
    option2 = dialog.checkBox2.IsChecked
    output.print_md("**Option 1:** %s" % option1)
    output.print_md("**Option 2:** %s" % option2)
else:
    output.print_md("**Dialog was cancelled or closed.**")