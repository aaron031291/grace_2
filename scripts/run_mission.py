"""
Run a mission by sending its manifest to the Mission Control API.
"""
import requests
import yaml
import sys

API_URL = "http://localhost:8000"

def run_mission(manifest_path: str):
    """Reads a mission manifest and posts it to the API."""
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Manifest file not found at '{manifest_path}'")
        return
    except Exception as e:
        print(f"Error reading or parsing YAML file: {e}")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"manifest": manifest}

    print(f"Submitting mission: {manifest.get('mission_name', 'Unknown Mission')}")
    
    try:
        response = requests.post(
            f"{API_URL}/mission-control/missions/create-from-manifest",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            print("Mission submitted successfully!")
            print(response.json())
        else:
            print(f"Error submitting mission. Status: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Error: Connection to the Grace API failed. Is the server running?")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_mission.py <path_to_manifest.yaml>")
    else:
        run_mission(sys.argv[1])