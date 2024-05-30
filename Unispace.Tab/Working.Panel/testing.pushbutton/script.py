import os
import clr
clr.AddReference('PresentationFramework')
clr.AddReference('System.Windows.Forms')
clr.AddReference('PresentationCore')

from System.Windows import Window, Application, MessageBox, MessageBoxButton, MessageBoxImage
from System.Windows.Media.Imaging import BitmapImage
from System import Uri, UriKind
import wpf

class MyWindow(Window):
    def __init__(self):
        # Construct the full path to the XAML file based on the script's location
        dirname = os.path.dirname(__file__)
        xaml_path = os.path.join(dirname, 'wpf_ui.xaml')
        wpf.LoadComponent(self, xaml_path)
        
        # Construct the full path to the image file
        image_path = os.path.join(dirname, 'grid_image.png')
        
        # Print the image path for debugging
        print("Image Path: {}".format(image_path))
        
        # Check if the image file exists
        if os.path.exists(image_path):
            print("Image file found.")
            
            # Set the image source programmatically
            bitmap = BitmapImage()
            bitmap.BeginInit()
            bitmap.UriSource = Uri(image_path, UriKind.Absolute)
            bitmap.EndInit()
            self.gridImage.Source = bitmap
        else:
            print("Image file not found.")
            MessageBox.Show("Image file not found: {}".format(image_path), "Error", MessageBoxButton.OK, MessageBoxImage.Error)
        
        self.ok_clicked = False  # Flag to check if OK was clicked

    def OnOkButtonClick(self, sender, e):
        self.ok_clicked = True
        self.Close()

    def OnClosed(self, e):
        if not self.ok_clicked:
            print("Window was closed without clicking OK. Exiting...")
            # Application.Current.Shutdown()

if __name__ == '__main__':
    app = Application()
    window = MyWindow()
    window.Closed += window.OnClosed  # Attach the OnClosed event handler
    app.Run(window)
    
    if window.ok_clicked:
        print("OK button was clicked. Continuing...")
        # Your script's continuation logic here
    else:
        print("Script stopped because the window was closed without clicking OK.")