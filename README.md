# Google Drive Folder Upload Script

This Python script is used to upload a local folder to Google Drive. The script authenticates using the Google Drive API and uploads the specified folder as a zip file to Google Drive.

## Installation

### Prerequisites

- Python 2.7 or Python 3.x
- A Google account with Google Drive API enabled

### Installing Dependencies

Install the required Python libraries to run the script:

```bash
pip install -r requirements.txt
```
## Authentication Credentials

1. Create a new project in the Google API Console.
2. Create OAuth 2.0 Client Credentials and download the `client_secret.json` file.
3. Place the downloaded `client_secret.json` file in the root directory of your project.
4. When you run the script, a `google-drive-credentials.json` file will be created for authentication. This file allows the script to access the Google Drive API.

## Usage

To use the script, follow these steps:

```bash
python main.py <folder_name> <folder_path>
```
* <folder_name>: The name of the folder to be created in Google Drive.
* <folder_path>: The local path of the folder to be uploaded.

The script will package the specified folder as a zip file, create a new folder in Google Drive, and upload the zip file to this folder.

## Example
```bash
python main.py "MyFolder" "/path/to/local/folder"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

