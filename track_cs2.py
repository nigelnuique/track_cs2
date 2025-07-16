import time
import psutil
from datetime import datetime
import os
import sys
import atexit
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
LOCK_FILE = "cs2_tracker.lock"

ENTERTAINMENT_CAL_ID = os.getenv('CALENDAR_ID')
if not ENTERTAINMENT_CAL_ID:
    print("Warning: CALENDAR_ID not found in .env. Using 'primary' calendar.")
    ENTERTAINMENT_CAL_ID = 'primary'

def check_single_instance():
    """Check if another instance of the tracker is already running"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if the process is still running
            try:
                process = psutil.Process(pid)
                if process.is_running() and 'track_cs2.py' in ' '.join(process.cmdline()):
                    print(f"✗ CS2 Tracker is already running (PID: {pid})")
                    print("Only one instance can run at a time.")
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process doesn't exist, remove stale lock file
                os.remove(LOCK_FILE)
        except (ValueError, FileNotFoundError):
            # Invalid or missing lock file, remove it
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
    
    # Create lock file with current PID
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    return True

def cleanup_lock_file():
    """Remove lock file when exiting"""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass

def auth_calendar():
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found.")
        sys.exit(1)

    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            sys.exit(1)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                sys.exit(1)
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"OAuth error: {e}")
                sys.exit(1)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error creating calendar client: {e}")
        sys.exit(1)

def create_event(service, start, end):
    event = {
        'summary': 'CS2 Session',
        'description': 'Tracked automatically',
        'start': {'dateTime': start.isoformat()},
        'end': {'dateTime': end.isoformat()},
    }
    try:
        service.events().insert(calendarId=ENTERTAINMENT_CAL_ID, body=event).execute()
        print(f"✓ Logged session from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")
    except Exception as e:
        print(f"✗ Failed to log event: {e}")

def track_game():
    # Check for existing instance
    if not check_single_instance():
        sys.exit(1)
    
    # Register cleanup function
    atexit.register(cleanup_lock_file)
    
    print("Starting CS2 session tracker...")
    calendar_service = auth_calendar()
    print(f"✓ Authenticated. Using calendar: {ENTERTAINMENT_CAL_ID}")
    print(f"✓ Instance lock created (PID: {os.getpid()})")

    cs2_active = False
    session_start = None
    local_tz = datetime.now().astimezone().tzinfo

    try:
        while True:
            is_running = False
            for p in psutil.process_iter(['name']):
                try:
                    name = p.info['name'] or p.name()
                    if name.lower() == GAME_NAME.lower():
                        is_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            if is_running and not cs2_active:
                cs2_active = True
                session_start = datetime.now(tz=local_tz)
                print(f"▶ CS2 started at {session_start}")
            elif not is_running and cs2_active:
                session_end = datetime.now(tz=local_tz)
                print(f"■ CS2 ended at {session_end}")
                create_event(calendar_service, session_start, session_end)
                cs2_active = False
                session_start = None
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n⛔ Tracker stopped by user.")
        if cs2_active and session_start:
            session_end = datetime.now(tz=local_tz)
            print(f"■ Final session ended at {session_end}")
            create_event(calendar_service, session_start, session_end)
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cleanup_lock_file()

if __name__ == '__main__':
    track_game()
