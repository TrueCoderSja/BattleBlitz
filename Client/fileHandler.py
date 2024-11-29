import requests
import os
import zipfile
import appdirs

# Global Variables
directory = None
map_DataFile = None
D = {}

def initialise():
    """Initializes the directory and loads existing map data."""
    global directory, map_DataFile, D

    app_name = "Battle Blitz"  # App's name
    app_author = "Dextern"  # Company name
    directory = appdirs.user_data_dir(app_name, app_author)
    map_DataFile = os.path.join(directory, "mapdata.txt")

    os.makedirs(directory, exist_ok=True)

    if os.path.exists(map_DataFile):
        with open(map_DataFile, "r") as file:
            lines = [line.strip() for line in file if line.strip()]  # Skip blank lines

        # Populate dictionary in URL -> file path pairs
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):  # Ensure we don't access out of bounds
                url, file_path = lines[i], lines[i + 1]
                D[url] = file_path

        print(f"Data loaded from: {map_DataFile}")
    else:
        open(map_DataFile, 'w').close()  # Create an empty file if it doesn't exist
        print(f"Created new map data file at: {map_DataFile}")

# Call initialise() as soon as the module is imported
initialise()

def file_checker(url):
    """Check if the URL exists in the map data."""
    global D
    return D.get(url)

def fetch_tilemap_file(url, name):
    """Fetch the file from the URL, unzip it, and return the extracted directory."""
    global directory, D, map_DataFile

    savePath = os.path.join(directory, f"{name}.zip")

    if file_checker(url):
        # If the URL already exists in the map data, return the saved path
        return D[url]

    try:
        print("Not found.... Downloading....")
        response = requests.get(url)
        response.raise_for_status()
        with open(savePath, "wb") as file:
            file.write(response.content)
        
        # Add the new entry to map data and save it
        extracted_dir = unzip_file(savePath)
        if extracted_dir:
            add_entry(url, extracted_dir)  # Update map data with extracted directory
            print(f"File saved as {savePath}")
            return extracted_dir
        else:
            raise ValueError(f"Failed to extract {savePath}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while fetching the file: {e}")

def fetch_file(url , name):
    """Fetch the file from the URL and return the path of the downloaded file."""
    global directory, D

    savePath = os.path.join(directory, name)

    if file_checker(url):
        # If the URL already exists in the map data, return the saved path
        return D[url]

    try:
        print("Not found.... Downloading....")
        response = requests.get(url)
        response.raise_for_status()
        with open(savePath, "wb") as file:
            file.write(response.content)
        
        # Add the new entry to map data and save it
        add_entry(url, savePath)  # Update map data with the file path
        print(f"File saved as {savePath}")
        return savePath
    except Exception as e:
        print(f"An error occurred while fetching the file: {e}")
        return None


def unzip_file(zip_path):
    """Unzips the downloaded file to a new directory and returns the extracted directory path."""
    extracted_dir = zip_path.replace(".zip", "")
    os.makedirs(extracted_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print(f"File unzipped to {extracted_dir}")
        return extracted_dir
    except Exception as e:
        print(f"Error unzipping file: {e}")
        return None

def add_entry(url, filepath):
    """Add a new entry to the map data and save it."""
    global D, map_DataFile

    # Update the in-memory dictionary
    D[url] = filepath

    try:
        # Write the URL and file path in the correct format
        with open(map_DataFile, "a") as file:
            file.write(f"{url}\n{filepath}\n")  # No leading/trailing blank lines
    except Exception as e:
        print(f"Error saving map data: {e}")

def callback(file_path):
    """Callback function that is invoked when the file is fetched and unzipped."""
    print("Callback function called")
    print(f"Extracted directory path: {file_path}")