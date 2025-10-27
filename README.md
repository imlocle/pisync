# PiSync: Automated Media Transfer and File Cleanup System

Welcome to **PiSync**, a Python-based application designed to automate the transfer of media files from your MacBook to a Raspberry Pi and manage file cleanup. Built with PySide6 for a user-friendly GUI, PiSync simplifies syncing movies and TV shows to your Pi while maintaining an organized media library.

![PiSync Logo](assets/icons/pisync_logo.png)

## Features

- **Automated Transfer**: Drag and drop media files to sync them to your Raspberry Pi.
- **File Cleanup**: Skip specified files (e.g., `.DS_Store`) and organize by file extensions.
- **Configurable Settings**: Customize Pi credentials, IP, and media paths via a settings window.
- **Monitoring**: Start and stop monitoring with play/stop icons for intuitive control.
- **Logging**: Real-time log display within the app.
- **Last Modified Date**: View the last modification date of your config file in settings.

## Prerequisites

- **Python 3.9+**
- **PySide6** (for GUI)
- **pydantic** (for configuration validation)
- **MacOS** (tested on macOS, may require adjustments for other platforms)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/imlocle/pisync.git
   cd pisync
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Build App with PyInstaller**

   ```bash
   pyinstaller --noconfirm --onedir --windowed \
     -n "PiSync" \
     --icon="assets/icons/pisync_logo.png" \
     --add-data="assets/icons/pisync_logo.png:assets/icons" \
     --add-data="assets/icons/play_icon.svg:assets/icons" \
     --add-data="assets/icons/stop_icon.svg:assets/icons" \
     --add-data="assets/styles/styles.qss:assets/styles" \
     --add-data="ui/controllers/monitor_thread.py:ui/controllers" \
     --add-data="ui/components/file_explorer_widget.py:ui/components" \
     --add-data="ui/components/main_window.py:ui/components" \
     --add-data="ui/components/settings_window.py:ui/components" \
     --add-data="src/config/settings.py:src/config" \
     --add-data="src/utils/logging_signal.py:src/utils" \
     main.py
   ```

4. **Run the App**

   ```bash
   open dist/PiSync.app
   ```

   Or, if running from the terminal:

   ```bash
   dist/PiSync.app/Contents/MacOS/PiSync
   ```
