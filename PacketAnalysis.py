import pymongo
import mysql.connector
import csv
import re
from datetime import datetime

# MongoDB connection
client = pymongo.MongoClient("your_mongodb_URI") # update monogDB URI
db = client["network_data"]
collection = db["frames"]

# MySQL connection 
# update details of your MySQL database
mysql_config = {
    'user': 'root',
    'password': '123456',
    'host': 'host.docker.internal',  
    'port': 3305,
    'database': 'hpe_packets',
    'auth_plugin': 'mysql_native_password'
}

conn = mysql.connector.connect(**mysql_config)
cursor = conn.cursor()

def dropTable():
    # Drop the existing 'keyword_matches' table if it exists
    try:
        cursor.execute("DROP TABLE IF EXISTS keyword_matches")
        conn.commit()
    except mysql.connector.Error as err:
        print("Error dropping table:", err)

# Check if the 'keyword_matches' table exists, if not, create it
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keyword_matches (
        arrival_time DATETIME,
        keyword VARCHAR(255),
        interface VARCHAR(255),
        nf INT
    )
    """)
    conn.commit()
except mysql.connector.Error as err:
    print("Error creating table:", err)

# Define your interface-keyword mapping
interface_keywords_map = {
    "N12": {
        "primary": ["nausf-auth"],
        "secondary": ["ue-authentications", "deregister", "5g-aka-confirmation", "eap-session", "rg-authentications"]
    },
    "N13": {
        "primary": ["nudm-ueau"],
        "secondary": ["GenerateAuthData", "GetRgAuthData", "ConfirmAuth", "DeleteAuth", "GenerateAv", "GenerateGbaAv", "GenerateProseAV", "authenticationVector"]
    },
    "N22": {
        "primary": ["nnssf-nssaiavailability", "nnssf-nsselection"],
        "secondary": []
    },
    "N11": {
        "primary": ["nsmf-pdusession", "nsmf-event-exposure", "nsmf-nidd"],
        "secondary": []
    },
    "N7": {
        "primary": ["npcf-smpolicycontrol", "sm-policies"],
        "secondary": []
    },
    "N10": {
        "primary": ["nudm-uecm"],
        "secondary": ["registrations", "restore-pcscf", "sdm-subscriptions", "shared-data-subscriptions", "am-data"]
    },
    "N15": {
        "primary": ["npcf-am-policy-control", "npcf-ue-policy-control"],
        "secondary": []
    },
    "N8": {
        "primary": ["nudm-sdm", "nudm-uecm", "namf-mt", "namf-location", "namf-comm"],
        "secondary": ["registration", "deregistration", "deregistration-notification", "context", "domain-selection", "location", "subscriber-data", "subscriptions", "notifications", "status-change"]
    },
    "N14": {
        "primary": ["namf-mt", "namf-evts", "namf-location", "namf-event-exposure", "n1n2-message-transfer", "amf-status-change-notify"],
        "secondary": ["sms", "locations"]
    }
}

# Function to find interface based on extracted keywords
def extract_interface(text):
    # Split text by '/' to handle paths correctly
    path_tokens = text.split('/')
    
    potential_interfaces = {}
    path_keywords = []
    
    # First, match primary keywords
    for interface, keywords in interface_keywords_map.items():
        primary_matches = [token for token in path_tokens if token in keywords["primary"]]
        if primary_matches:
            potential_interfaces[interface] = primary_matches
            path_keywords.extend(primary_matches)
    
    # If only one interface matches primary keywords, return it
    if len(potential_interfaces) == 1:
        return list(potential_interfaces.keys())[0], path_keywords
    
    # If multiple interfaces match, check secondary keywords
    for interface, matches in potential_interfaces.items():
        secondary_keywords = interface_keywords_map[interface]["secondary"]
        if any(token in path_tokens for token in secondary_keywords):
            return interface, path_keywords
    
    # If no clear match is found, return None or raise an error
    return None, path_keywords

def convert_to_mysql_datetime(date_str):
    try:
        # Remove the nanoseconds part
        dt = datetime.strptime(date_str[:-14], "%b %d, %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print("Error converting datetime:", e)
        return None

def extract_data_and_keywords():
    try:
        count = collection.count_documents({})
        if count==0:
            dropTable()
        cursor_mongo = collection.find({"analyzed": False, "frame_data": {"$regex": ":path:", "$options": "i"}})
        with open('random.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["arrival_time", "keyword", "interface", "nf"])  # Writing the header

            batch_data = []
            batch_size = 100  # Adjust the batch size as needed

            for document in cursor_mongo:
                arrival_time_str = document["arrival_time"]
                print(arrival_time_str)
                arrival_time = convert_to_mysql_datetime(arrival_time_str)

                frame_data = document["frame_data"]

                # Find the :path: line
                path_match = re.search(r":path:\s+(/\S+)", frame_data)
                # Update the analysed field to True in MongoDB
                collection.update_one({"_id": document["_id"]}, {"$set": {"analyzed": True}})
                if path_match:
                    path = path_match.group(1)

                    # Extract keywords from the path
                    interface, path_keywords = extract_interface(path)

                    # Extract the numeric part of the interface
                    nf = int(re.search(r'\d+', interface).group()) if interface else None

                    print(f"Document ID: {document['_id']}")
                    print(f"Extracted Path: {path}")
                    print(f"Extracted Keywords: {path_keywords}")
                    print(f"Corresponding Interface: {interface}")
                    print(f"Numeric part of Interface (nf): {nf}")

                    # Add to batch data
                    for keyword in path_keywords:
                        batch_data.append((arrival_time, keyword, interface, nf))
                        # Write to CSV
                        writer.writerow([arrival_time, keyword, interface, nf])
                        break



                    # Insert batch to MySQL
                    if len(batch_data) >= batch_size:
                        print(f"Inserting batch of {len(batch_data)} records into MySQL...")
                        cursor.executemany("INSERT INTO keyword_matches (arrival_time, keyword, interface, nf) VALUES (%s, %s, %s, %s)", batch_data)
                        conn.commit()
                        batch_data.clear()

            # Insert any remaining data in the batch
            if batch_data:
                print(f"Inserting final batch of {len(batch_data)} records into MySQL...")
                cursor.executemany("INSERT INTO keyword_matches (arrival_time, keyword, interface, nf) VALUES (%s, %s, %s, %s)", batch_data)
                conn.commit()
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
    finally:
        conn.close()

if __name__ == "__main__":
    extract_data_and_keywords()
    print("Data extraction and keyword processing completed.")
