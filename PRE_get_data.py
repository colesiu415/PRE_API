import asyncio
import websockets
import requests
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_token(env_file):
    # Load environment variables from the JSON file
    try:
        with open(env_file, "r") as file:
            print(f"Loading environment variables from '{env_file}'...\n")
            env_data = json.load(file)
            # Extract variables from the JSON file
            app_key = next((item["value"] for item in env_data["values"] if item["key"] == "app_key"), None)
            app_secret = next((item["value"] for item in env_data["values"] if item["key"] == "app_se"), None)
    except FileNotFoundError:
        raise FileNotFoundError(f"Environment file '{env_file}' not found.")
    except KeyError:
        raise ValueError(f"Invalid format in environment file '{env_file}'.")
    if not app_key or not app_secret:
        raise ValueError("Missing required environment variables: PRE_APP_KEY, PRE_APP_SECRET")

    # Get the access token using PRE credentials
    url = "https://api.interact-lighting.com/oauth/accesstoken"
    payload = f'app_key={app_key}&app_secret={app_secret}&service=officeCloud'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic QmxFT203QTJfc2lnbmlmeV9jb206NHNpSjdGb2o2VHFRSE9lc3c3cWZ1WQ=='
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print("Token response received successfully...\n")  
        
        token_data = response.json()  # Parse the JSON response
        if not token_data.get("token"):
            raise ValueError("Token not found in the response.")
        token = "Bearer" +" "+ token_data.get("token")  # Extract the "token" field
        print("Access token extracted successfully...\n")
        return token  # Return the token string 
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}\n")  # Handle HTTP errors
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}\n")  # Handle connection errors
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}\n")  # Handle timeout errors
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}\n")  # Handle any other request errors
    except ValueError as val_err:
        print(f"Value error: {val_err}\n")  # Handle missing or invalid token


def get_site_uuid(token):
   # Get the site UUID using the access token
    url = "https://api.interact-lighting.com/interact/api/v1/officeCloud/sites"
    payload = {}
    headers = {
    'Authorization': token
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print("Sites data received successfully...\n")
        return response.json()  # Parse the JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")  # Handle connection errors
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")  # Handle timeout errors
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")  # Handle any other request errors
    except ValueError as val_err:
        print(f"Value error: {val_err}")  # Handle missing or invalid token


def get_building_uuid(token, site_uuid):
    # Get the building UUID using the site UUID
    url = f"https://api.interact-lighting.com/interact/api/v1/officeCloud/sites/{site_uuid}/buildings"
    payload = {}
    headers = {
    'Authorization': token
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print("Building data received successfully...\n")
        return response.json()  # Parse the JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")  # Handle connection errors
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")  # Handle timeout errors
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")  # Handle any other request errors
    except ValueError as val_err:
        print(f"Value error: {val_err}")  # Handle missing or invalid token


def get_websocket(token, build_uuid, ws_type):
    #Get the occupancy websocket using the building UUID
    url = f"https://api.interact-lighting.com/interact/api/v1/officeCloud/subscription/{build_uuid}/{ws_type}"
    payload = {}
    headers = {
    'Authorization': token
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print("Websocket received successfully...\n")
        ws = response.json().get('websocketUrl')  # Parse the JSON response
        return ws    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")  # Handle connection errors
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")  # Handle timeout errors
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")  # Handle any other request errors
    except ValueError as val_err:
        print(f"Value error: {val_err}")  # Handle missing or invalid token

# Function to write data to Google Sheets
def write_to_sheet(service, SPREADSHEET_ID, data, range_name):
    try:
        body = {"values": data}
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
        print("Data written to Google Sheet successfully...\n")
    except HttpError as err:
        print(f"An error occurred while writing to Google Sheets: {err}")



# Create concurrent WebSocket connections to get data stream
async def listen_to_websockets(token, build_uuid, ws_types, service, SPREADSHEET_ID):

    async def get_data(ws, ws_type):
        timeout = 60 * 20  # seconds
        start_time = asyncio.get_event_loop().time()  # Get the current time in seconds
        print(f"Starting WebSocket connection for {ws}...\n")

        try:
            async with websockets.connect(ws) as websocket:
                print(f"Connected to WebSocket server: {ws}\n")
                while True:
                    # Check if the timeout has been reached
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        print(f"Timeout reached for {ws}, closing connection.\n")
                        break

                    try:
                        # Wait for a message from the server
                        raw_data = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                        print(f"Received raw data from websocket {ws_type}\n{raw_data}\n")

                        
                            
                        # Parse the JSON data by ws_type
                        if ws_type == "OCCUPANCY":
                            parsed_data = json.loads(raw_data)
                            time = parsed_data.get("time")
                            space_id = parsed_data.get("spaceId")  
                            timestamp = parsed_data.get("timestamp")
                            occupancy = parsed_data.get("occupancy")
                            formatted_data = [[time, space_id, occupancy, timestamp]] # Format the data as a list of lists

                        if ws_type == "TEMPERATURE": 
                            parsed_data = json.loads(raw_data)
                            time = parsed_data.get("time")
                            space_id = parsed_data.get("spaceId")  
                            timestamp = parsed_data.get("timestamp")
                            temp = parsed_data.get("temperature")
                            formatted_data = [[time, space_id, temp, timestamp]]
                        
                        if ws_type == "AGGREGATED_AREA_ENERGY": 
                            parsed_data = json.loads(raw_data)
                            time = parsed_data.get("reportTime")
                            space_id = parsed_data.get("spaceId")  
                            timestamp = parsed_data.get("timestamp")
                            energy = parsed_data.get("accumulatedEnergy")
                            formatted_data = [[time, space_id, energy, timestamp]]
                        
                        if ws_type == "HUMIDITY": 
                            parsed_data = json.loads(raw_data)
                            time = parsed_data.get("time")
                            space_id = parsed_data.get("spaceId")  
                            timestamp = parsed_data.get("timestamp")
                            energy = parsed_data.get("humidity")
                            formatted_data = [[time, space_id, energy, timestamp]]
                        

                        print(f"Formatted data for {ws_type}: {formatted_data}\n")
                        # Write the formatted data to the corresponding Google Sheet range
                        write_to_sheet(service, SPREADSHEET_ID, formatted_data, range_name=ws_type)

                    except asyncio.TimeoutError(timeout):
                        print(f"No data received from websocket: ({ws_type}), quitting...\n")
                        
        except Exception as e:
            print(f"An error occurred with {ws}: {e}\n")

    # Create WebSocket connections for all ws_types
    tasks = []
    for ws_type in ws_types:
        ws = get_websocket(token, build_uuid, ws_type)  # Get the WebSocket URL
        if not ws:
            print(f"WebSocket URL not found for {ws_type}. Skipping...\n")
            continue
        tasks.append(get_data(ws, ws_type))  # Add the WebSocket task to the list

    # Run all WebSocket connections concurrently
    await asyncio.gather(*tasks)



def main():

    # Google Sheets API setup
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SERVICE_ACCOUNT_FILE = "gskey.json"
    SPREADSHEET_ID = "1ehUXfUaUawb7FTK3jzVjKgN3HtMZbC6e8MARF6cZOfA"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)
    print("Google Sheets API setup completed...\n")


    token = get_token("PRE-Signify HK.postman_environment.json")  # Get the access token using the function
    sites = get_site_uuid(token)  # Get the site UUID using the access token
    site_name = []
    site_uuid = []
    for site in sites:
        site_name.append(site.get('name'))
        site_uuid.append(site.get('uuid'))

    buildings = get_building_uuid(token, site_uuid[0])  # Get the building UUID using the site UUID
    build_name = []
    build_uuid = []
    for building in buildings:
        build_name.append(building.get('name'))
        build_uuid.append(building.get('uuid'))
  
    ws_types = [
        'AGGREGATED_AREA_ENERGY',  # WebSocket stream for energy use data
        'OCCUPANCY',  # WebSocket stream for occupancy data
        'TEMPERATURE',  # WebSocket stream for temperature data
        'HUMIDITY',  # WebSocket stream for humidity data
        #'ACOUSTIC_COMFORT',  # WebSocket stream for noise level
        #'AIR_QUALITY'  # WebSocket stream for air quality data
    ]


    # Run the WebSocket listeners asynchronously
    asyncio.run(listen_to_websockets(token, build_uuid[0], ws_types, service, SPREADSHEET_ID))
    print ("Script finished.\n")


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    This function acts as the entry point for the Lambda function.
    """
    try:
        # Call the main function
        main()
        return {
            "statusCode": 200,
            "body": "Script executed successfully."
        }
    except Exception as e:
        # Handle any errors that occur during execution
        return {
            "statusCode": 500,
            "body": f"An error occurred: {str(e)}"
        }

#if __name__ == "__main__":
#    main()