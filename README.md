# XML Overlay Application

A Python application that creates an overlay window displaying XML Properties from a monitored XML file. The overlay stays on top of other windows and can be dragged around the screen.

## Setup

1. Install Python requirements:

   ```
   pip install PyQt5
   ```

2. Configure the XML path:
   - Copy the example config file:
     ```
     config.example.json -> config.json
     ```
   - Edit `config.json` with your XML file path:
     ```json
     {
       "xml_path": "path/to/your/xml/file.xml",
       "xml_config": {
         "root_node": "root",
         "target_node": "DatabaseName",
         "xpath": ".//DatabaseName"
       }
     }
     ```

## Running the Application

1. Run the application:
   ```
   python overlay.py
   ```
   or use the provided batch file:
   ```
   start_overlay.bat
   ```

## Features

- Displays XML properties from the monitored XML file
- Overlay stays on top of other windows
- Draggable window
- System tray icon with options:
  - Show Overlay
  - Hide Overlay
  - Increase Text Size (adjusts font size up to 72 points)
  - Decrease Text Size (adjusts font size down to 8 points)
  - Quit
- Close button appears when hovering over the overlay
- Auto-updates when XML file changes
