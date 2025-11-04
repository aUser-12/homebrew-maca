#!/usr/bin/env python3

import os
import sys
import subprocess
import random
import re
import argparse
import time


SCRIPT_NAME = os.path.basename(sys.argv[0])
INTERFACE = "en0"  #macos default sometimes en1
STATE_DIR = os.path.expanduser("~/Library/Application Support/maca")
SAVE_FILE = os.path.join(STATE_DIR, f"{SCRIPT_NAME}_orig_{INTERFACE}")
ACTION_COUNT = 0
FIRST_ACTION = None

#make the config directory, if it exists then ok
os.makedirs(STATE_DIR, exist_ok=True)

#this was vibe translated into python

#thank god i can use proper regex finally screw old bash

#me likey these ai descriptions so imma leave it
def run_command(command, capture_output=False):
    """Run a shell command and capture the output."""
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip() if capture_output else None

def is_full_mac(mac):
    """Validate MAC address format (xx:xx:xx:xx:xx:xx)."""
    return bool(re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac))

def is_mac_ending(mac):
    """Validate MAC address ending format (xx:xx)."""
    return bool(re.match(r'^([0-9a-fA-F]{2}:){2}[0-9a-fA-F]{2}$', mac))

def get_current_mac(interface):
    """Get the current MAC address for a given interface."""
    return run_command(f"ifconfig {interface} | awk '/ether/{{print $2}}'", capture_output=True)

def get_prefix(mac):
    """Get the first 3 octets of a MAC address."""
    return ":".join(mac.split(":")[:3]).lower()

def save_original_mac(interface):
    """Save the current MAC address for later restoration."""
    mac = get_current_mac(interface)
    if mac:
        with open(SAVE_FILE, 'w') as f:
            f.write(mac)
        os.chmod(SAVE_FILE, 0o600)  #600 = secure
    else:
        print(f"Failed to get MAC address for {interface}", file=sys.stderr)
        sys.exit(1)

def restore_original_mac(interface):
    """Restore the original MAC address."""
    if not os.path.isfile(SAVE_FILE):
        print(f"No saved MAC for {interface}.", file=sys.stderr)
        sys.exit(1)
    
    with open(SAVE_FILE, 'r') as f:
        orig_mac = f.read().strip()
        if not is_full_mac(orig_mac):
            print(f"Saved MAC '{orig_mac}' is invalid.", file=sys.stderr)
            sys.exit(1)
        set_mac(interface, orig_mac)

def set_mac(interface, mac):
    """Set a new MAC address on a given interface."""
    if not is_full_mac(mac):
        print(f"Invalid MAC format: {mac}", file=sys.stderr)
        sys.exit(1)
    
    #this could prolly be better but oh well
    run_command(f"ifconfig {interface} up")
    run_command(f"ifconfig {interface} ether {mac}")
    run_command(f"ifconfig {interface} down")
    time.sleep(0.5)
    run_command(f"ifconfig {interface} up") 
    run_command("networksetup -detectnewhardware", capture_output=True)  #renew DHCP in case bouncy house deflates
     
    #check if mac changed
    current_mac = get_current_mac(interface).lower()
    if current_mac == mac.lower():
        print(f"MAC address successfully set to {current_mac}")
    else:
        print(f"Failed to set MAC. Current MAC is {current_mac}", file=sys.stderr)
        sys.exit(1)

def generate_random_mac(interface):
    """Generate a random MAC address."""
    current_mac = get_current_mac(interface)
    prefix = get_prefix(current_mac)
    b1, b2, b3 = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    return f"{prefix}:{b1:02x}:{b2:02x}:{b3:02x}"

#yay no more callign external python files from bash
def generate_mac_from_template(template):
    """Generate a MAC address based on a template."""
    parts = template.split(":")
    if len(parts) != 6:
        print("Template must contain exactly 6 sections.", file=sys.stderr)
        sys.exit(1)
    
    result = []
    for part in parts:
        if part == "xx" or part == "??":
            result.append(f"{random.randint(0, 255):02x}")
        elif re.match(r'^[0-9a-fA-F]{2}$', part):
            result.append(part)
        else:
            print(f"Invalid byte in template: {part}", file=sys.stderr)
            sys.exit(1)
    return ":".join(result)

def ensure_interface_exists(interface):
    """Ensure the network interface exists."""
    try:
        run_command(f"ifconfig {interface}", capture_output=True)
    except SystemExit:
        print(f"Interface {interface} not found.", file=sys.stderr)
        sys.exit(1)


#parse dem args
def parse_args():
    parser = argparse.ArgumentParser(description="MAC address changer for macOS.")
    parser.add_argument("-i", type=str, help="Network interface (default: en0)", default="en0")
    parser.add_argument("-m", type=str, help="Full MAC address (aa:bb:cc:dd:ee:ff)")
    parser.add_argument("-e", type=str, help="Change only last 3 bytes of MAC address (dd:ee:ff)")
    parser.add_argument("-g", action="store_true", help="Generate a random MAC address ending")
    parser.add_argument("-t", type=str, help="Generate a MAC address with a template")
    parser.add_argument("-r", action="store_true", help="Restore previously saved MAC address")
    parser.add_argument("-s", action="store_true", help="Show current MAC address")
    return parser.parse_args()


#Assembling ze ikea furniture 2.0
def main():
    global INTERFACE, ACTION_COUNT, FIRST_ACTION

    args = parse_args()

    INTERFACE = args.i
    ensure_interface_exists(INTERFACE)


    # i wish python had case of
    if args.m:
        FIRST_ACTION = 'm'
        FULL_MAC = args.m
        ACTION_COUNT += 1
    elif args.e:
        FIRST_ACTION = 'e'
        MAC_ENDING = args.e
        ACTION_COUNT += 1
    elif args.t:
        FIRST_ACTION = 't'
        TEMPLATE = args.t
        ACTION_COUNT += 1
    elif args.r:
        FIRST_ACTION = 'r'
        ACTION_COUNT += 1
    elif args.s:
        FIRST_ACTION = 's'
        ACTION_COUNT += 1
    elif args.g:
        FIRST_ACTION = 'g'
        ACTION_COUNT += 1

    #TODO yeah ill fix this after SA2 the vibes stay for now
    if FIRST_ACTION == 'r':
        restore_original_mac(INTERFACE)
    elif FIRST_ACTION == 's':
        current_mac = get_current_mac(INTERFACE)
        print(f"Current MAC for {INTERFACE}: {current_mac}")
    elif FIRST_ACTION == 'g':
        if not os.path.isfile(SAVE_FILE):
            save_original_mac(INTERFACE)
        new_mac = generate_random_mac(INTERFACE)
        set_mac(INTERFACE, new_mac)
    elif FIRST_ACTION == 'm':
        if not is_full_mac(FULL_MAC):
            print(f"Invalid MAC format: {FULL_MAC}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(SAVE_FILE):
            save_original_mac(INTERFACE)
        set_mac(INTERFACE, FULL_MAC)
    elif FIRST_ACTION == 't':
        generated_mac = generate_mac_from_template(TEMPLATE)
        if not os.path.isfile(SAVE_FILE):
            save_original_mac(INTERFACE)
        set_mac(INTERFACE, generated_mac)
    elif FIRST_ACTION == 'e':
        if not is_mac_ending(MAC_ENDING):
            print(f"Invalid MAC ending: {MAC_ENDING}", file=sys.stderr)
            sys.exit(1)
        current_mac = get_current_mac(INTERFACE)
        prefix = get_prefix(current_mac)
        new_mac = f"{prefix}:{MAC_ENDING}"
        set_mac(INTERFACE, new_mac)
    else:
        print(f"Mac address: \n Interface: ", file=sys.stderr)
        sys.exit(1)


#BRRRRRRRRRRRRR
if __name__ == "__main__":
    main()
