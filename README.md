# Clair Organizer

## Description
Clair Organizer is a standalone desktop application that automatically sorts the contents of any folder into subfolders based on file types. Select a folder, click **Organize**, and watch as Documents, Images, Videos, Music, Archives and other files are moved into their own folders.

## Features
1. One-click organization of any folder’s files.  
2. Customizable categories and extensions via an intuitive graphical interface.  
3. Save, rename and delete presets for multiple workflows.  
4. Optional recursive scan of subfolders with the ability to remove empty directories.  
5. Dark-mode interface built on Qt (PySide6) for a modern look and feel.  

## Technologies Used
- **Python 3.11**: Core language for file system operations and application logic.
- **OS module**: Used to interact with the operating system for file management.  
- **PySide6 (Qt for Python)**: Cross-platform GUI framework.  
- **PyInstaller**: Packages the Python code and JSON data into a single executable.  
- **Inno Setup**: Builds a Windows installer that bundles the executable and configuration files.  

## Installation

### Option 1: Download Installer
1. Download **ClairInstaller.exe** from the release page: https://github.com/nicolasgioanni/Clair/releases
2. Run the installer and follow the prompts.  
3. Launch **Clair** from the Start menu.  

### Option 2: Clone and Run Manually

#### Requirements  
- Windows 10+ or macOS 10.13+  
- Python 3.11 (for manual install)  
- Dependencies listed in `requirements.txt`  

#### Steps to Run the App Manually

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/clair-organizer.git
2. Navigate to the Clair directory:
   ```bash
   cd clair-organizer
4. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # macOS/Linux
   .\venv\Scripts\Activate.ps1    # Windows
  
6. Install dependencies:
   ```bash
   pip install -r requirements.txt

7. Run the application:
   ```bash
   python clair.py 
   
## Usage
1. Click **Browse** and select the folder you want to organize.  
2. (Optional) Check **Include Subfolders** to process nested directories.  
3. (Optional) Check **Delete Empty Subfolders** to remove any now-empty folders.  
4. Click **Organize Now** and observe files moving into categorized folders.  
5. Use the **Manage Categories** panel to add, remove or rename categories and toggle extensions.
6. Click **Add Preset**, **Delete Preset**, or **Rename Preset** to add, delete, or rename custom preset respectively.

## How It Works
1. **Scan**: The application lists all files in the chosen folder (and subfolders if enabled).  
2. **Map**: Each file’s extension is matched against your defined categories.  
3. **Move**: Files are moved into subfolders named after their category; missing folders are created automatically.  
4. **Clean Up**: If enabled, any subdirectories left empty after moving files are deleted.  

## Customization
- Open the **Manage Categories** panel to add, remove or rename folders and toggle file extensions with a single click (your changes take effect immediately).  
- Save your current setup as a new preset, or switch between presets for different scenarios (for example, Desktop cleanup, Downloads, or Project folders).  
- Enable or disable individual extensions to fine-tune exactly which files get sorted.  
- Choose whether to include nested subfolders and optionally remove them when they’re empty.  
- Export or share your presets by copying the `presets.json` file; import shared presets by dropping them into the install directory.  
- For full manuel control, open and edit `categories.json` or `presets.json` in any text editor, Clair will load your changes the next time you run the app.  

## License
This project is licensed under the MIT License. see the LICENSE file for details.
