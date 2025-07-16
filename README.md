# CS2 Tracker

Automatically track your Counter-Strike 2 gaming sessions and log them to Google Calendar.

## Features

- Automatically detects when CS2 is running
- Logs gaming sessions to Google Calendar
- Launches CS2 through Steam
- Runs silently in the background
- Events are logged using your system's local timezone

## Setup

### Prerequisites

- Python 3.6 or higher
- Google account with Google Calendar access
- Counter-Strike 2 installed via Steam

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd cs2-tracker
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the setup script to configure credentials:
   ```bash
   python setup_credentials.py
   ```
   
   This script will guide you through:
   - Setting up Google Calendar API credentials
   - Creating the necessary authentication files
   - Configuring your calendar ID

4. **Important**: Update the file path in `Launch_CS2.bat`:
   - Open `Launch_CS2.bat` in a text editor
   - Change the path on line 1 to match your project location
   - Example: If your project is in `C:\Users\YourName\Documents\cs2-tracker`, change:
     ```batch
     start "" "pythonw" "C:\Users\pc\Documents\Projects\cs2-tracker\track_cs2.py"
     ```
     to:
     ```batch
     start "" "pythonw" "C:\Users\YourName\Documents\cs2-tracker\track_cs2.py"
     ```

## Usage

### Method 1: Using the Batch File (Recommended)
- Double-click `Launch_CS2.bat`
- This will start the tracker and launch CS2

### Method 2: Manual
- Run the tracker: `python track_cs2.py`
- Launch CS2 separately through Steam

## How It Works

1. The tracker monitors running processes for `cs2.exe`
2. When CS2 starts, it records the start time
3. When CS2 closes, it creates a calendar event with the session duration
4. Events are automatically added to your specified Google Calendar

## Files

- `track_cs2.py` - Main tracking script
- `Launch_CS2.bat` - Batch file to start tracker and launch CS2
- `setup_credentials.py` - Setup script for Google API credentials
- `requirements.txt` - Python dependencies
- `env.example` - Example environment file (copy to `.env`)
- `.env` - Environment variables (created during setup)
- `credentials.json` - Google API credentials (created during setup)
- `token.json` - OAuth token (created during setup)

## Security

- `credentials.json`, `token.json`, and `.env` are automatically excluded from version control
- Never share these files or commit them to a repository
- The setup script will guide you through creating these files safely

## Troubleshooting

### "credentials.json not found"
- Run `python setup_credentials.py` to set up your credentials

### "Permission denied" or authentication errors
- Delete `token.json` and run the setup script again to re-authenticate

### CS2 not being detected
- Make sure CS2 is installed and launches as `cs2.exe`
- Check that the process name hasn't changed in recent updates

### Calendar events not appearing
- Verify your calendar ID in the `.env` file
- Check that the Google Calendar API is enabled in your Google Cloud Console
- Ensure your calendar is not in a different time zone

## License

This project is for personal use. Please respect Valve's terms of service when using with Counter-Strike 2. 