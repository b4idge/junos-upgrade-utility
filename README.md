# Junos OS Upgrade Utility

A robust Python utility for automating Junos OS upgrades across network devices.

## Features

- ✅ Automated Junos OS image installation
- ✅ Secure device authentication
- ✅ USB device support
- ✅ Automatic version verification
- ✅ Comprehensive logging with visual indicators
- ✅ Command-line and environment variable configuration

# Disclaimer

AI-Generated Content: This project's code, documentation, and associated files were generated with the assistance of AI (Claude 3.7 Sonnet by Anthropic). While efforts have been made to ensure accuracy and functionality, users should review and test all code before deployment in production environments.

## Quick Start

### Prerequisites

- Python 3.6+
- Network connectivity to Junos devices
- Authentication credentials for target devices

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/junos-upgrade-utility.git
cd junos-upgrade-utility

# Install dependencies
pip install -r requirements.txt

# Prepare your configuration
cp .env.example .env
# Edit .env with your settings
```

### Basic Usage

```bash
# Using .env configuration
python junos_upgrade.py

# Using command line arguments
python junos_upgrade.py -H 192.168.1.1 -u admin -i junos-srxsme-24.2R2.18-signed.tgz -l /path/to/images -r /var/tmp/usb
```

## Configuration

Configuration can be provided either through command-line arguments or an `.env` file:

| Parameter | CLI Flag | ENV Variable | Description |
|-----------|----------|--------------|-------------|
| Host | `-H, --host` | `JUNOS_HOST` | Device hostname or IP address |
| Username | `-u, --user` | `JUNOS_USER` | Authentication username |
| Password | `-p, --password` | `JUNOS_PASSWORD` | Authentication password (prompt if omitted) |
| Image name | `-i, --image` | `JUNOS_IMAGE` | OS image filename |
| Local path | `-l, --local-path` | `JUNOS_IMAGE_PATH` | Directory containing the image |
| Remote path | `-r, --remote-path` | `REMOTE_PATH` | Path on device (usually USB mount) |
| Expected version | `-e, --expected-version` | `EXPECTED_VERSION` | Version prefix to verify after upgrade |
| Timeout | `-t, --timeout` | - | Reboot timeout in seconds (default: 720) |
| Verbose | `-v, --verbose` | - | Enable verbose logging |

For detailed usage instructions, see the [documentation](docs/usage.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.