import pandas as pd
import numpy as np
import hashlib
import os

# Step 1: Load datasets
ap_data = pd.read_csv("access_points.csv")  # Simulated Access Points data
wifi_data = pd.read_csv("wifi_sessions.csv")  # Simulated Wi-Fi session data

# Step 2: Hash pseudo-identifiers (e.g., callingstationid)
def hash_sensitive_data(data, salt=None):
    if not salt:
        salt = os.urandom(16)
    salted_data = salt.hex() + str(data)
    hashed = hashlib.sha256(salted_data.encode()).hexdigest()
    return hashed

wifi_data['hashed_user_id'] = wifi_data['callingstationid'].apply(hash_sensitive_data)

# Step 3: Aggregate session data to handle splits
wifi_data_agg = wifi_data.groupby(['acctsessionid', 'hashed_user_id']).agg({
    'upload': 'max',  # Max upload
    'download': 'max',  # Max download
    'acctsessiontime': 'sum',  # Sum session time
    'acctstarttime': 'min',  # Earliest start time
    'calledstationid': 'first'  # Retain one AP per session
}).reset_index()

# Step 4: Merge with Access Points data
wifi_data_merged = wifi_data_agg.merge(ap_data, left_on='calledstationid', right_on='MAC Radius', how='left')

# Step 5: Add noise for differential privacy
def add_noise_to_column(data, epsilon=1.0):
    scale = 1 / epsilon
    noisy_data = data + np.random.laplace(0, scale, len(data))
    return noisy_data.clip(min=0)

wifi_data_merged['noisy_upload'] = add_noise_to_column(wifi_data_merged['upload'], epsilon=0.5)
wifi_data_merged['noisy_download'] = add_noise_to_column(wifi_data_merged['download'], epsilon=0.5)

# Step 6: Extract trajectories
trajectories = wifi_data_merged.groupby('hashed_user_id').agg({
    'acctstarttime': list,
    'Latitude': list,
    'Longitude': list
}).reset_index()

# Save results
wifi_data_merged.to_csv("processed_wifi_data.csv", index=False)
trajectories.to_csv("user_trajectories.csv", index=False)

print("Processed Wi-Fi data and user trajectories saved.")

