README.txt
Project Name
PRE API Data Processor

Description
This project is a Python-based application that connects to WebSocket streams, processes real-time data, and writes the formatted data to Google Sheets. It supports multiple WebSocket types, including occupancy, temperature, humidity, and energy data.

Features
Connects to WebSocket streams for real-time data.
Processes and formats JSON data from WebSocket streams.
Writes formatted data to specific ranges in Google Sheets.
Supports multiple WebSocket types:
Occupancy
Temperature
Humidity
Aggregated Area Energy
Requirements
Python 3.8 or higher
Required Python libraries:
asyncio
websockets
requests
google-auth
google-api-python-client
Installation
Clone the repository or download the source code.
Navigate to the project directory:
Install the required dependencies:
Usage
Set Up Google Sheets API:

Create a service account in Google Cloud Console.
Download the service account key file (gskey.json) and place it in the project directory.
Share the target Google Sheet with the service account email.
Prepare the Environment File:

Ensure the PRE-Signify HK.postman_environment.json file contains the required environment variables (app_key, app_secret, etc.).
Run the Script Locally:

Execute the script:
Deploy to AWS Lambda:

Package the code and dependencies into a ZIP file.
Upload the ZIP file to AWS Lambda.
Set the handler to PRE_get_data.lambda_handler.
Schedule the Lambda Function:

Use Amazon EventBridge to schedule the Lambda function to run periodically (e.g., every 3 hours).
File Structure
WebSocket Types and Google Sheets Mapping
WebSocket Type	Google Sheets Range
OCCUPANCY	Sheet1!A1
TEMPERATURE	Sheet2!A1
HUMIDITY	Sheet3!A1
AGGREGATED_AREA_ENERGY	Sheet4!A1
Error Handling
The script includes error handling for:
HTTP errors (e.g., 4xx, 5xx responses).
Connection errors.
Timeout errors.
Invalid or missing tokens.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License.

Contact
For questions or feedback, please contact [Your Name] at [your-email@example.com].

Feel free to customize this README.txt file further based on your specific requirements!
