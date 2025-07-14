import time
import psutil
from datetime import datetime
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Please install it using 'pip install python-dotenv'")
    sys.exit(1)

GAME_NAME = "cs2.exe"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Get calendar ID from environment variable
CALENDAR_ID = os.getenv('CALENDAR_ID')
if not CALENDAR_ID:
    print("Error: CALENDAR_ID not found in environment variables.")
    print("Please run 'python setup_credentials.py' to set up your environment file.")
    sys.exit(1)

def get_calendar_service():
    """Get authenticated calendar service - following debug script pattern"""
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found.")
        print("Please run 'python setup_credentials.py' to set up your credentials.")
        sys.exit(1)
    
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            print("Please run 'python setup_credentials.py' to recreate your token.")
            sys.exit(1)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print("Please run 'python setup_credentials.py' to recreate your token.")
                sys.exit(1)
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                print("Please run 'python setup_credentials.py' to set up your credentials.")
                sys.exit(1)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def create_single_event(service, start_time, end_time):
    """Create exactly one calendar event for the gaming session"""
    event = {
        'summary': 'CS2 Session',
        'description': 'Tracked automatically',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Australia/Melbourne'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Australia/Melbourne'},
    }
    
    try:
        result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"✓ Session logged: {start_time} to {end_time}")
        print(f"  Event ID: {result.get('id', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error creating calendar event: {e}")
        print("Please check your calendar ID and permissions.")
        return False

def track_game():
    """Main tracking function - single event per session"""
    print("Initializing CS2 tracker...")
    print(f"Target calendar: {CALENDAR_ID}")
    
    try:
        calendar_service = get_calendar_service()
        print("✓ Successfully authenticated with Google Calendar")
    except Exception as e:
        print(f"❌ Failed to authenticate with Google Calendar: {e}")
        return
    
    cs2_active = False
    session_start = None

    print("🎮 Tracking CS2 sessions. Press Ctrl+C to exit.")
    print("=" * 50)
    
    try:
        while True:
            try:
                is_running = any(p.name().lower() == GAME_NAME.lower() for p in psutil.process_iter(['name']))
                
                if is_running and not cs2_active:
                    # CS2 just started
                    cs2_active = True
                    session_start = datetime.now()
                    print(f"🚀 CS2 started at {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                elif not is_running and cs2_active:
                    # CS2 just ended - create single event
                    session_end = datetime.now()
                    if session_start is not None:
                        duration = session_end - session_start
                        print(f"🛑 CS2 ended at {session_end.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"⏱️  Session duration: {duration}")
                        
                        success = create_single_event(calendar_service, session_start, session_end)
                        if success:
                            print("📅 Event created successfully!")
                        else:
                            print("⚠️  Event creation failed!")
                    else:
                        print("⚠️  Session start time was None - skipping event creation")
                        
                    cs2_active = False
                    print("=" * 50)
                    
            except Exception as e:
                print(f"Error checking processes: {e}")
                
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Tracker stopped by user.")
        if cs2_active and session_start is not None:
            session_end = datetime.now()
            # Use local variable to ensure type safety
            start_time = session_start
            duration = session_end - start_time
            print(f"⏱️  Final session duration: {duration}")
            success = create_single_event(calendar_service, start_time, session_end)
            if success:
                print("📅 Final event created successfully!")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    track_game()
