# Clair Organizer

## Description
Clair Organizer is a standalone desktop application that automatically sorts the contents of any folder into categorized subfolders. Instead of manually organizing files, simply launch Clair, select your folder, and let it group Documents, Images, Videos, Music, Archives, and more for you.

## Features
- **One-click organization**: Instantly sort a folder’s files with a single button.
- **Custom categories**: Add, remove or rename categories; toggle which file extensions belong to each.
- **Preset management**: Save, rename and delete presets to switch between different organization schemes.
- **Subfolder support**: Optionally include nested folders in the scan and remove them if they become empty.
- **Modern GUI**: Dark-mode interface built with PySide6 for a clean, user-friendly experience.
- **Installer**: Easy Windows installer and macOS app bundle, no Python install required.

## Technologies Used
- **Python 3**  
- **PySide6** (Qt for Python)  
- **PyInstaller** (creates a single-file executable)  
- **Inno Setup** (Windows installer)  
- Core modules: `pathlib`, `shutil`, `json`, `os`

## Installation
1. Download the latest installer for your platform: [Download Link]  
2. Run the installer and follow the prompts.  
3. Launch **Clair Organizer** from your Start Menu (Windows) or Applications folder (macOS).

## How It Works
1. **Scan**: Clair examines every file in the chosen folder (and subfolders, if enabled).  
2. **Categorize**: File extensions are matched against your defined categories.  
3. **Move**: Files are moved into folders named after their category. Missing folders are created automatically.  
4. **Clean Up**: If enabled, any subfolders left empty after organizing will be removed.

## Customization
- **In-App**: Use the GUI to adjust your categories and extensions—changes save automatically.  
- **Presets**: Create multiple presets for different use cases (e.g., Desktop vs. Downloads).  
- **Manual**: Edit `categories.json` and `presets.json` in the installation directory for advanced tweaks.

---
