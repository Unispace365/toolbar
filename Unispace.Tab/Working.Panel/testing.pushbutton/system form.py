import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')

from System.Windows.Forms import Application, Form, PictureBox, Button, CheckBox, DialogResult, TableLayoutPanel, DockStyle, PictureBoxSizeMode, ColumnStyle, RowStyle, SizeType, Label
from System.Drawing import Image, Size, Point, ContentAlignment
from pyrevit import forms, script
import os

# Get the output object
output = script.get_output()

class CustomDialog(Form):
    def __init__(self):
        self.Text = 'Custom Popup'
        self.Size = Size(400, 600)
        
        # Table Layout Panel
        self.table = TableLayoutPanel()
        self.table.Dock = DockStyle.Fill
        self.table.ColumnCount = 1
        self.table.RowCount = 10
        self.table.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100))
        for i in range(10):
            self.table.RowStyles.Add(RowStyle(SizeType.Absolute, 50))  # Fixed height for rows
        self.Controls.Add(self.table)
        
        # Text Label 1
        self.label1 = Label()
        self.label1.Text = "This will renumber all rooms in the model based on the NY 10' grid system. Room codes are determined based on alphanumeric coordinate system within the 10` grid interval.  Columns are alphabetical and rows are numeric"
        self.label1.TextAlign = ContentAlignment.MiddleCenter
        self.label1.Dock = DockStyle.Fill
        self.table.Controls.Add(self.label1, 0, 0)
        
        # Image 1
        self.pictureBox1 = PictureBox()
        self.pictureBox1.Image = Image.FromFile(os.path.join(os.path.dirname(__file__), 'grid.png'))
        self.pictureBox1.SizeMode = PictureBoxSizeMode.Zoom
        self.pictureBox1.Dock = DockStyle.Fill
        self.table.Controls.Add(self.pictureBox1, 0, 1)
        self.table.SetRowSpan(self.pictureBox1, 7)  # Span across two rows
        
        # Text Label 2
        self.label2 = Label()
        self.label2.Text = "This is the second image:"
        self.label2.TextAlign = ContentAlignment.MiddleCenter
        self.label2.Dock = DockStyle.Fill
        self.table.Controls.Add(self.label2, 0, 3)
        
        # Image 2
        self.pictureBox2 = PictureBox()
        self.pictureBox2.Image = Image.FromFile(os.path.join(os.path.dirname(__file__), 'name_template.png'))
        self.pictureBox2.SizeMode = PictureBoxSizeMode.Zoom
        self.pictureBox2.Dock = DockStyle.Fill
        self.table.Controls.Add(self.pictureBox2, 0, 4)
        self.table.SetRowSpan(self.pictureBox2, 5)  # Span across two rows
        
        # Checkboxes
        self.checkBox1 = CheckBox()
        self.checkBox1.Text = 'Does this project have work on multiple floors? If yes the level number will be added to each room name.'
        self.checkBox1.TextAlign = ContentAlignment.MiddleCenter
        self.checkBox1.Dock = DockStyle.Fill
        self.table.Controls.Add(self.checkBox1, 0, 6)
        
        self.checkBox2 = CheckBox()
        self.checkBox2.Text = "Create the red 10' grid"
        self.checkBox2.TextAlign = ContentAlignment.MiddleCenter
        self.checkBox2.Dock = DockStyle.Fill
        self.table.Controls.Add(self.checkBox2, 0, 7)
        
        self.checkBox3 = CheckBox()
        self.checkBox3.Text = 'Option 3'
        self.checkBox3.TextAlign = ContentAlignment.MiddleCenter
        self.checkBox3.Dock = DockStyle.Fill
        self.table.Controls.Add(self.checkBox3, 0, 8)
        
        # Button Panel
        self.buttonPanel = TableLayoutPanel()
        self.buttonPanel.Dock = DockStyle.Fill
        self.buttonPanel.ColumnCount = 2
        self.buttonPanel.RowCount = 1
        self.buttonPanel.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50))
        self.buttonPanel.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50))
        self.table.Controls.Add(self.buttonPanel, 0, 9)
        
        # OK Button
        self.okButton = Button()
        self.okButton.Text = 'OK'
        self.okButton.Dock = DockStyle.Fill
        self.okButton.DialogResult = DialogResult.OK
        self.buttonPanel.Controls.Add(self.okButton, 0, 0)
        
        # Cancel Button
        self.cancelButton = Button()
        self.cancelButton.Text = 'Cancel'
        self.cancelButton.Dock = DockStyle.Fill
        self.cancelButton.DialogResult = DialogResult.Cancel
        self.buttonPanel.Controls.Add(self.cancelButton, 1, 0)
        
        # Set the form's Accept and Cancel buttons
        self.AcceptButton = self.okButton
        self.CancelButton = self.cancelButton

# Create and show the dialog
dialog = CustomDialog()
result = dialog.ShowDialog()

if result == DialogResult.OK:
    option1 = dialog.checkBox1.Checked
    option2 = dialog.checkBox2.Checked
    option3 = dialog.checkBox3.Checked
    output.print_md("**Option 1:** %s" % option1)
    output.print_md("**Option 2:** %s" % option2)
    output.print_md("**Option 3:** %s" % option3)
# else:
#     output.print_md("**Dialog was cancelled or closed.**")