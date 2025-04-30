import requests
import socket
import threading
import time
import pystray
from PIL import Image
from typing import Dict, Any, Optional
import sys
from datetime import datetime
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

# Global configuration
config = {}

def log(message: str):
    log_file = "spaceship_dns.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} {message}\n"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def delete_dns_record(address: str) -> Dict[str, Any]:
    url = f"https://spaceship.dev/api/v1/dns/records/{config['domainName']}"

    headers = {
        "X-API-Key": config["apiKey"],
        "X-API-Secret": config["apiSecret"],
        "Content-Type": "application/json"
    }
    
    data = [
        {
            "type": config["recordType"],
            "address": address,
            "name": config["recordName"]
        }
    ]
    
    response = requests.delete(url, headers=headers, json=data)
    
    # 204 means success with no content
    if response.status_code == 204:
        log("DNS record " + address + " deleted successfully " + response.text)
        return {"success": True, "message": "DNS record updated successfully"}
    
    # For other status codes, try to parse JSON response
    try:
        return response.json()
    except ValueError:
        log("Error deleting DNS record: " + response.text)
        return {
            "success": False,
            "status": response.status_code,
            "message": response.text or "Unknown error occurred"
        }

def update_dns_record(address: str) -> Dict[str, Any]:
    url = f"https://spaceship.dev/api/v1/dns/records/{config['domainName']}"

    headers = {
        "X-API-Key": config["apiKey"],
        "X-API-Secret": config["apiSecret"],
        "Content-Type": "application/json"
    }
    
    data = {
        "force": True,
        "items": [
            {
                "type": config["recordType"],
                "address": address,
                "name": config["recordName"],
                "ttl": config["recordTtl"]*60
            }
        ]
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    # 204 means success with no content
    if response.status_code == 204:
        return {"success": True, "message": "DNS record updated successfully"}
    
    # For other status codes, try to parse JSON response
    try:
        log("DNS record " + address + " updated successfully " + response.text)
        return response.json()
    except ValueError:
        log("Error updating DNS record: " + response.text)
        return {
            "success": False,
            "status": response.status_code,
            "message": response.text or "Unknown error occurred"
        }

def get_ip_address(address: str) -> str:
    try:
        return socket.gethostbyname(address)
    except socket.gaierror:
        log("Could not resolve " + address + ", assuming no record exists")
        return None

def check_and_update_ip_address():
    try:
        address = config["recordName"] + "." + config["domainName"]
        local_ip_address = requests.get('https://api.ipify.org?format=json').json()['ip']
        ip_address = get_ip_address(address)

        if ip_address is None:
            log("Error server address not found")
            return;

        if ip_address == local_ip_address:
            log("IP addresses are the same, no need to update " + ip_address + " to " + local_ip_address)
        else:
            log("IP addresses are different, updating " + ip_address + " to " + local_ip_address)
            delete_result = delete_dns_record(address=ip_address);
            if delete_result["success"] == False:
                return;
            
            update_result = update_dns_record(address=local_ip_address);
            if update_result["success"] == False:
                return;
            
            log("DNS record updated successfully");
    
    except Exception as e:
        log("Error checking and updating IP address: " + str(e))

def validate_config(config: dict) -> bool:
    required_fields = ['apiKey', 'apiSecret', 'domainName', 'recordName', 'recordType', 'recordTtl', 'checkInterval']
    for field in required_fields:
        if field not in config or not config[field]:
            return False
    return True

def load_config() -> tuple[bool, dict]:
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            if validate_config(config):
                return True, config
            return False, config
    except (FileNotFoundError, json.JSONDecodeError):
        return False, {}

def save_config(config: dict) -> bool:
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        log(f"Error saving config: {e}")
        return False

def create_default_config():
    default_config = {
        'apiKey': '',
        'apiSecret': '',
        'domainName': '',
        'recordName': '',
        'recordType': 'A',
        'recordTtl': 60,
        'checkInterval': 60
    }
    save_config(default_config)
    return default_config

def edit_config(icon):
    try:
        os.startfile('config.json')
    except Exception as e:
        log(f"Error opening config file: {e}")

def on_exit(icon):
    log("Closing the app.")
    icon.stop()
    sys.exit(0)

def open_log(icon):
    log_file = "spaceship_dns.log"
    try:
        os.startfile(log_file)
    except Exception as e:
        log(f"Error opening log file: {e}")

def run_application(config: dict):
    log("Starting the app.")
    icon = pystray.Icon("spaceship_ip")
    icon.icon = Image.open('spaceship.png')
    icon.title = "Spaceship IP Updater"
    icon.menu = pystray.Menu(
        pystray.MenuItem("Edit Parameters", edit_config),
        pystray.MenuItem("Open Log", open_log),
        pystray.MenuItem("Close", on_exit)
    )
    
    # Start the IP check in a separate thread
    def run_ip_check():
        while True:
            check_and_update_ip_address()
            time.sleep(config["checkInterval"] * 60)
    
    check_thread = threading.Thread(target=run_ip_check, daemon=True)
    check_thread.start()
    
    # Run the system tray icon
    icon.run()

if __name__ == "__main__":
    config_valid, loaded_config = load_config()
    if not config_valid:
        # Create or update config file
        config = create_default_config()
        # Open config file for editing
        try:
            os.startfile('config.json')
        except Exception as e:
            log(f"Error opening config file: {e}")
        # Exit application
        sys.exit(0)
    
    config = loaded_config
    run_application(config)
