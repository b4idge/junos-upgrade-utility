# Configuration Guide

This document provides detailed information about configuring the Junos OS Upgrade Utility.

## Configuration Methods

The utility supports two configuration methods:

1. **Environment Variables** (.env file)
2. **Command-line Arguments** (CLI flags)

Command-line arguments take precedence over environment variables when both are provided.

## Environment Variables

For persistent configuration, create a `.env` file in the same directory as the script with the following parameters:

```properties
# Device Connection Details
JUNOS_HOST=192.168.1.1
JUNOS_USER=admin
JUNOS_PASSWORD=SecurePassword123  # Optional, omit for secure prompt

# Image Details
JUNOS_IMAGE=junos-srxsme-24.2R2.18-signed.tgz
JUNOS_IMAGE_PATH=/path/to/junos/images
REMOTE_PATH=/var/tmp/usb

# Upgrade Settings
EXPECTED_VERSION=24.2R2.18
```

## Parameter Reference

### Device Connection Parameters

| Parameter | Environment Variable | CLI Flag | Default | Description |
|-----------|---------------------|----------|---------|-------------|
| Host | `JUNOS_HOST` | `-H, --host` | None | IP address or hostname of the Junos device. Required. |
| Username | `JUNOS_USER` | `-u, --user` | None | Username for authentication to the device. Required. |
| Password | `JUNOS_PASSWORD` | `-p, --password` | None | Password for authentication. If not provided through environment variables or CLI, you'll be prompted securely. |

### Image Parameters

| Parameter | Environment Variable | CLI Flag | Default | Description |
|-----------|---------------------|----------|---------|-------------|
| Image name | `JUNOS_IMAGE` | `-i, --image` | None | Filename of the Junos OS image to install (e.g., `junos-srxsme-24.2R2.18-signed.tgz`). Required. |
| Local path | `JUNOS_IMAGE_PATH` | `-l, --local-path` | None | Local directory path containing the image file. Required. |
| Remote path | `REMOTE_PATH` | `-r, --remote-path` | `/var/tmp/usb` | Path on the Junos device where the image will be copied. Usually points to a USB mount point. |

### Upgrade Parameters

| Parameter | Environment Variable | CLI Flag | Default | Description |
|-----------|---------------------|----------|---------|-------------|
| Expected version | `EXPECTED_VERSION` | `-e, --expected-version` | `24.2R2.18` | Version prefix that should be detected after upgrade to verify success. |
| Timeout | N/A | `-t, --timeout` | `720` | Timeout in seconds to wait for device to come back online after reboot. |
| Verbose | N/A | `-v, --verbose` | `False` | Enable verbose debug logging. |

## Best Practices

### Secure Password Handling

For security reasons, it's recommended to:


1. **Use ssh key-based authentication instead of passwords** in production environments
2 **Omit passwords from the .env file** 
3. **Use secure password prompts** by not providing the `-p` flag
4. **Never commit .env files** containing passwords to version control

### Remote Path Configuration

The remote path (`REMOTE_PATH` or `--remote-path`) should point to a valid directory on the Junos device:

- For USB installations: typically `/var/tmp/usb`
- For internal storage: typically `/var/tmp`

Ensure the path exists and has sufficient space before running the upgrade.

### Version Verification

When setting the `EXPECTED_VERSION` parameter:

- Use just the version prefix (e.g., `24.2R2.18`) rather than the full version string
- Be specific enough to verify the correct version but not overly restrictive
- For major upgrades, you might use just the major version (e.g., `24.2`)

### Timeout Configuration

The default timeout of 720 seconds (12 minutes) should be sufficient for most devices. 

## Configuration Examples

### Minimal Configuration

```properties
# .env file - minimal configuration
JUNOS_HOST=192.168.1.1
JUNOS_USER=admin
JUNOS_IMAGE=junos-srxsme-24.2R2.18-signed.tgz
JUNOS_IMAGE_PATH=/home/user/junos_images
```

### Complete Configuration

```properties
# .env file - complete configuration
JUNOS_HOST=192.168.1.1
JUNOS_USER=admin
JUNOS_PASSWORD=SecurePassword123
JUNOS_IMAGE=junos-srxsme-24.2R2.18-signed.tgz
JUNOS_IMAGE_PATH=/home/user/junos_images
REMOTE_PATH=/var/tmp/usb
EXPECTED_VERSION=24.2R2.18
```

### Command-line Examples

**Basic usage (using .env for most parameters):**
```bash
python junos_upgrade.py -v
```

**Overriding the host and image:**
```bash
python junos_upgrade.py -H 192.168.2.1 -i junos-srxsme-24.2R2.18-signed.tgz
```

**Complete configuration via command line:**
```bash
python junos_upgrade.py \
  -H 192.168.1.1 \
  -u admin \
  -i junos-srxsme-24.2R2.18-signed.tgz \
  -l /home/user/junos_images \
  -r /var/tmp/usb \
  -e 24.2R2.18 \
  -t 900 \
  -v
```

## Troubleshooting Configuration Issues

### Common Configuration Problems

1. **Missing Required Parameters**
   - Error: `Missing required configuration: host, user, image_name, local_image_dir`
   - Solution: Ensure all required parameters are provided either in .env or via CLI

2. **Image Path Issues**
   - Error: `Local file not found`
   - Solution: Verify the local image path and filename are correct

3. **Remote Path Not Found**
   - Error: `Remote path not found or empty`
   - Solution: Ensure the USB drive is properly mounted on the device

4. **Authentication Failures**
   - Error: `Permission denied`
   - Solution: Check username and password credentials