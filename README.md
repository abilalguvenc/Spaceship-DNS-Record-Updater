# Spaceship DNS Record Updater

A Windows system tray application that automatically updates DNS records when your IP address changes, using the Spaceship API.

![Application Icon](app/spaceship.png)

## Features

- 🖥️ Runs in system tray for minimal intrusion
- 🔄 Automatically checks for IP changes
- 📝 Updates DNS records via Spaceship API
- ⚙️ Simple configuration via JSON file
- 📊 Detailed logging of all operations

## Requirements

- Windows 10/11
- Python 3.8 or higher
- Internet connection

## Installation

1. Clone this repository:
```powershell
git clone https://github.com/yourusername/spaceship-dns-updater.git
cd spaceship-dns-updater
```

2. Install required packages:
```powershell
pip install -r requirements.txt
```

## Configuration

The application uses a `config.json` file for settings. On first run, it will create this file with default values and open it for editing. You'll need to fill in:

```json
{
    "apiKey": "your-api-key",
    "apiSecret": "your-api-secret",
    "domainName": "your-domain.com",
    "recordName": "subdomain",
    "recordType": "A",
    "recordTtl": 60,
    "checkInterval": 60
}
```

- `apiKey` and `apiSecret`: Your Spaceship API credentials
- `domainName`: Your domain name
- `recordName`: The subdomain to update
- `recordType`: DNS record type (usually "A")
- `recordTtl`: Time-to-live in minutes
- `checkInterval`: How often to check for IP changes (in minutes)

## Usage

1. Run the application using the shortcut `Spaceship Record Updater`.

2. The application will:
   - Start in the system tray
   - Check for IP changes at the specified interval
   - Update DNS records when changes are detected
   - Log all activities to `spaceship_dns.log`

3. System Tray Menu:
   - **Edit Parameters**: Opens config.json for editing
   - **Open Log**: Opens the log file
   - **Close**: Exits the application

## Security Notes

- `config.json` and `spaceship_dns.log` are excluded from version control
- API credentials are stored locally in `config.json`
- Consider setting appropriate file permissions on `config.json`

## Troubleshooting

- Check `spaceship_dns.log` for error messages
- Ensure your API credentials are correct and DNS Records access is enabled
- Verify your domain and record settings
- Make sure the application has network access

## License

GNU General Public License v3 - See LICENSE file for details 
