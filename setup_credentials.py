#!/usr/bin/env python3
"""
Setup script to help users obtain Google Calendar API credentials.
Run this script to set up the necessary credentials for CS2 tracking.
"""

import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def create_credentials_json():
    """Guide user through creating credentials.json file"""
    print("=" * 60)
    print("SETTING UP GOOGLE CALENDAR API CREDENTIALS")
    print("=" * 60)
    print()
    
    if os.path.exists('credentials.json'):
        print("✓ credentials.json already exists!")
        return True
    
    print("You need to create a credentials.json file from Google Cloud Console.")
    print("Follow these steps:")
    print()
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Calendar API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Calendar API'")
    print("   - Click on it and press 'Enable'")
    print("4. Create credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Choose 'Desktop application' as the application type")
    print("   - Give it a name (e.g., 'CS2 Tracker')")
    print("   - Click 'Create'")
    print("5. Download the JSON file:")
    print("   - Click the download button next to your new credential")
    print("   - Save it as 'credentials.json' in this directory")
    print()
    
    input("Press Enter after you've downloaded credentials.json to this directory...")
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found! Please download it and try again.")
        return False
    
    # Validate the credentials file
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data:
            print("✓ credentials.json is valid!")
            return True
        else:
            print("❌ credentials.json doesn't appear to be for a desktop application.")
            print("Please make sure you selected 'Desktop application' when creating the OAuth client ID.")
            return False
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON!")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def create_token_json():
    """Create token.json through OAuth flow"""
    print("\n" + "=" * 60)
    print("CREATING ACCESS TOKEN")
    print("=" * 60)
    
    if os.path.exists('token.json'):
        print("✓ token.json already exists!")
        
        # Check if token is still valid
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds.valid:
                print("✓ Existing token is still valid!")
                return True
            elif creds.expired and creds.refresh_token:
                print("🔄 Token expired, refreshing...")
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("✓ Token refreshed successfully!")
                return True
        except Exception as e:
            print(f"⚠️ Error with existing token: {e}")
            print("Creating new token...")
    
    try:
        print("Starting OAuth flow...")
        print("A browser window will open. Please:")
        print("1. Sign in to your Google account")
        print("2. Grant permission to access your Google Calendar")
        print("3. You may see a warning about the app not being verified - click 'Advanced' then 'Go to [app name] (unsafe)'")
        print()
        
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("✓ token.json created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return False

def create_env_file():
    """Create .env file with calendar ID"""
    print("\n" + "=" * 60)
    print("SETTING UP ENVIRONMENT FILE")
    print("=" * 60)
    
    if os.path.exists('.env'):
        print("✓ .env file already exists!")
        return True
    
    print("Creating .env file...")
    
    # Check if example file exists
    if os.path.exists('env.example'):
        print("📋 Found env.example file as template")
    
    print("You need to provide your Google Calendar ID.")
    print()
    print("To find your Calendar ID:")
    print("1. Go to https://calendar.google.com/")
    print("2. On the left sidebar, find the calendar you want to use")
    print("3. Click the three dots (...) next to the calendar name")
    print("4. Select 'Settings and sharing'")
    print("5. Scroll down to 'Calendar ID' and copy the ID")
    print()
    
    while True:
        cal_id = input("Enter your Calendar ID: ").strip()
        if cal_id:
            break
        print("Please enter a valid Calendar ID.")
    
    # Create .env file with template format
    with open('.env', 'w') as f:
        f.write("# CS2 Tracker Environment Variables\n")
        f.write("# This file contains sensitive information - never commit to version control\n")
        f.write("\n")
        f.write(f"CALENDAR_ID={cal_id}\n")
    
    print("✓ .env file created successfully!")
    return True

def main():
    """Main setup function"""
    print("CS2 Tracker - Credential Setup")
    print("This script will help you set up the necessary files for CS2 tracking.")
    print()
    
    # Check if required packages are installed
    try:
        import google_auth_oauthlib
        import google.auth.transport.requests
        import google.oauth2.credentials
    except ImportError:
        print("❌ Required packages not found!")
        print("Please install requirements first:")
        print("    pip install -r requirements.txt")
        sys.exit(1)
    
    success = True
    
    # Step 1: Create credentials.json
    if not create_credentials_json():
        success = False
    
    # Step 2: Create token.json
    if success and not create_token_json():
        success = False
    
    # Step 3: Create .env file
    if success and not create_env_file():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SETUP COMPLETE!")
        print()
        print("All credential files have been created successfully.")
        print("You can now run the CS2 tracker:")
        print("    python track_cs2.py")
        print()
        print("Don't forget to:")
        print("1. Update the path in Launch_CS2.bat to match your project location")
        print("2. Never commit credentials.json, token.json, or .env to version control")
    else:
        print("❌ SETUP FAILED!")
        print("Please resolve the errors above and try again.")
    
    print("=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main() 