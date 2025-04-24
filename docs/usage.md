# Detailed Usage Guide

## Command-line Usage

The Junos OS Upgrade Utility supports various command-line arguments for flexible usage:

```bash
python junos_upgrade.py [-h] [-H HOST] [-u USER] [-p PASSWORD] [-i IMAGE]
                        [-l LOCAL_PATH] [-r REMOTE_PATH] [-e EXPECTED_VERSION]
                        [-t TIMEOUT] [-v]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-H, --host` | Junos device hostname or IP address |
| `-u, --user` | Username for device authentication |
| `-p, --password` | Password (omit for secure prompt) |
| `-i, --image` | Junos image filename |
| `-l, --local-path` | Local directory containing the image |
| `-r, --remote-path` | Remote path on device (usually USB mount) |
| `-e, --expected-version` | Expected version prefix after upgrade |
| `-t, --timeout` | Reboot timeout in seconds (default: 720) |
| `-v, --verbose` | Enable verbose output |
| `-h, --help` | Show help message |

## Usage Examples

### Basic Usage with .env File

1. Set up your configuration in the `.env` file:
   ```
   JUNOS_HOST=192.168.1.1
   JUNOS_USER=admin
   JUNOS_IMAGE=junos-srxsme-24.2R2.18-signed.tgz
   JUNOS_IMAGE_PATH=/home/user/images
   REMOTE_PATH=/var/tmp/usb
   EXPECTED_VERSION=24.2R2.18
   ```

2. Run the script:
   ```bash
   python junos_upgrade.py
   ```

### Command-line Usage

To override the .env file or run without one:

```bash
python junos_upgrade.py -H 192.168.1.1 -u admin -i junos-srxsme-24.2R2.18-signed.tgz -l /home/user/images -r /var/tmp/usb -e 24.2R2.18
```

### Mixed Usage

You can also mix .env variables with command-line overrides:

```bash
# Override just the host and username
python junos_upgrade.py -H 192.168.2.1 -u operator
```

## Understanding the Upgrade Process

The utility performs these steps in sequence:

1. **Connection**: Establishes a connection to the Junos device
2. **Image Check**: Verifies if the image already exists on the device
3. **Image Transfer**: Copies the image if not already present
4. **Installation**: Installs the Junos OS image
5. **Reboot**: Initiates a device reboot
6. **Verification**: Reconnects and verifies the installed version

## Log File

All operations are logged to `junos_upgrade.log` in the current directory. This provides a detailed record of the upgrade process including:

- Connection attempts
- File transfer statistics
- Installation progress
- Error conditions

Example log output:
```
2025-04-24 10:15:22,345 - INFO - ℹ️ Starting upgrade process
2025-04-24 10:15:22,347 - INFO - ✅ Configuration loaded successfully
2025-04-24 10:15:22,348 - INFO - ℹ️ Connecting to device 192.168.1.1...
2025-04-24 10:15:24,567 - INFO - ✅ Connected to 192.168.1.1
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify IP address/hostname is correct
   - Ensure network connectivity
   - Check username/password

2. **Image Copy Failures**
   - Verify local image path
   - Check disk space on device
   - Ensure appropriate permissions

3. **Installation Failures**
   - Verify image compatibility with device
   - Check for corruption (file size/checksum)
   - Ensure adequate space on device

4. **Version Verification Failures**
   - Check expected version string format
   - Ensure compatible image for device model