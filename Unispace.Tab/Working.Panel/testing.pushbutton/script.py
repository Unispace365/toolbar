import os
import clr
clr.AddReference('PresentationFramework')
clr.AddReference('System.Windows.Forms')

from System.Windows import Window
import wpf

class MyWindow(Window):
    def __init__(self):
        # Construct the full path to the XAML file based on the script's location
        dirname = os.path.dirname(__file__)
        xaml_path = os.path.join(dirname, 'wpf_ui.xaml')
        wpf.LoadComponent(self, xaml_path)
    
    def OnGreetButtonClick(self, sender, e):
        user_input = self.inputText.Text
        self.outputText.Text = "Hello, {}!".format(user_input)

if __name__ == '__main__':
    window = MyWindow()
    window.ShowDialog()  # Use ShowDialog to run the window modally