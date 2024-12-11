import pandas as pd
import hashlib
import os

# Step 1: Load datasets
wifi_data = pd.read_csv("200lines.csv")  # Simulated 200 line file

# Step 2: Hash pseudo-identifiers (e.g., callingstationid, acctstarttime, acctsessiontime)
def hash_sensitive_data(data, salt=None):
    if not salt:
        salt = os.urandom(16)
    salted_data = salt.hex() + str(data)
    hashed = hashlib.sha256(salted_data.encode()).hexdigest()
    return hashed

wifi_data['callingstationid'] = wifi_data['callingstationid'].apply(hash_sensitive_data)
wifi_data['acctstarttime'] = wifi_data['acctstarttime'].apply(hash_sensitive_data)
wifi_data['acctsessiontime'] = wifi_data['acctsessiontime'].apply(hash_sensitive_data)

# Save the updated data to a new CSV file
wifi_data.to_csv("updated_200lines.csv", index=False)

print("Updated 200lines.csv file saved with hashed sensitive data.")