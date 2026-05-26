import urllib.request
import os

url = 'https://raw.githubusercontent.com/alpigmk3/gs_art_center_dev/main/img/logo.png'
filename = 'logo.png'

try:
    print(f"Downloading {url} to {filename}...")
    urllib.request.urlretrieve(url, filename)
    if os.path.exists(filename):
        print(f"Success! Saved logo locally as: {os.path.abspath(filename)}")
    else:
        print("Error: File was not created.")
except Exception as e:
    print(f"Failed to download logo. Error: {e}")
