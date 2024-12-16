from ipwhois import IPWhois
import json
import sqlite3
from datetime import datetime

# Function to get country from IP using ipstack API (example)
def get_country_from_ip(ip):
    # Check if the IP address is the loopback address (localhost)
    if ip == '127.0.0.1' or ip == 'localhost':
        return "Localhost"  # Return a default value for local IPs

    try:
        # Perform the IP lookup using IPWhois
        ipwhois = IPWhois(ip)
        result = ipwhois.lookup_rdap()
        country = result.get('country', 'Unknown')  # Get country or return 'Unknown'
        return country
    except Exception as e:
        print(f"Error looking up IP: {ip} - {e}")
        return "Unknown"  # Return 'Unknown' in case of error

# Function to log site visit with timestamp and country
def log_visit(ip, DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Insert timestamp and country into the 'visits' table
    country = get_country_from_ip(ip)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO visits (timestamp, ip, country) VALUES (?, ?, ?)", (timestamp, ip, country))

    conn.commit()
    conn.close()

def log_template(ip, config, subconfig, sheets, DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Insert timestamp and request details into the 'templates' table
    country = get_country_from_ip(ip)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheets_json = json.dumps(list(sheets))
    c.execute("INSERT INTO templates (timestamp, ip, country, config, subconfig, sheets) VALUES (?, ?, ?, ?, ?, ?)", (timestamp, ip, country, config, subconfig, sheets_json))

    conn.commit()
    conn.close()