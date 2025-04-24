#!/usr/bin/env python3

import os
import sys
import time
import logging
import argparse
from getpass import getpass
from pathlib import Path

try:
    from jnpr.junos import Device
    from jnpr.junos.utils.sw import SW
    from jnpr.junos.utils.fs import FS
    from jnpr.junos.exception import ConnectError, RpcError
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Error: Required module not found: {e}")
    print("Please install required packages: pip install junos-eznc python-dotenv")
    sys.exit(1)

# Configure custom logger with emojis
class EmojiLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, msg):
        self.logger.info(f"ℹ️ {msg}")
    
    def success(self, msg):
        self.logger.info(f"✅ {msg}")
    
    def warning(self, msg):
        self.logger.warning(f"⚠️ {msg}")
    
    def error(self, msg):
        self.logger.error(f"❌ {msg}")
    
    def debug(self, msg):
        self.logger.debug(f"🔍 {msg}")

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('junos_upgrade.log')
    ]
)
standard_logger = logging.getLogger(__name__)
logger = EmojiLogger(standard_logger)

def load_config():
    """Load configuration from .env file or command line arguments"""
    # Load .env if it exists
    load_dotenv(verbose=True)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Junos OS Upgrade Utility')
    parser.add_argument('-H', '--host', help='Junos device hostname/IP')
    parser.add_argument('-u', '--user', help='Username for device authentication')
    parser.add_argument('-p', '--password', help='Password (omit for secure prompt)')
    parser.add_argument('-i', '--image', help='Junos image filename')
    parser.add_argument('-l', '--local-path', help='Local directory containing the image')
    parser.add_argument('-r', '--remote-path', help='Remote path on device (usually USB mount)')
    parser.add_argument('-e', '--expected-version', help='Expected version prefix after upgrade')
    parser.add_argument('-t', '--timeout', type=int, default=720, help='Reboot timeout in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Configure logging level based on verbose flag
    if args.verbose:
        standard_logger.setLevel(logging.DEBUG)
    
    # Priority: command line args > env vars > defaults
    config = {
        'host': args.host or os.getenv("JUNOS_HOST"),
        'user': args.user or os.getenv("JUNOS_USER"),
        'password': args.password or os.getenv("JUNOS_PASSWORD"),
        'image_name': args.image or os.getenv("JUNOS_IMAGE"),
        'local_image_dir': args.local_path or os.getenv("JUNOS_IMAGE_PATH"),
        'remote_path': args.remote_path or os.getenv("REMOTE_PATH", "/var/tmp/usb"),
        'expected_version': args.expected_version or os.getenv("EXPECTED_VERSION", "24.2R2.18"),
        'timeout': args.timeout
    }
    
    # Validate required parameters
    missing = [k for k, v in config.items() if v is None and k not in ['password']]
    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        parser.print_help()
        sys.exit(1)
    
    # If password not provided, prompt securely
    if not config['password']:
        config['password'] = getpass("Enter device password: ")
    
    # Set full paths for convenience
    config['local_image_fullpath'] = os.path.join(config['local_image_dir'], config['image_name'])
    config['remote_image_fullpath'] = os.path.join(config['remote_path'], config['image_name'])
    
    logger.success("Configuration loaded successfully")
    return config

def connect_device(host, user, password):
    """Connect to the Junos device with error handling."""
    logger.info(f"Connecting to device {host}...")
    try:
        dev = Device(host=host, user=user, password=password)
        dev.open()
        logger.success(f"Connected to {host}")
        return dev
    except ConnectError as err:
        logger.error(f"Connection error: {err}")
        return None
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        return None

def probe_device(host, user, password, timeout=720):
    """Probe device to check if it's back online after reboot."""
    logger.info(f"Waiting for device {host} to come back online (timeout: {timeout}s)...")
    deadline = time.time() + timeout
    
    while time.time() < deadline:
        try:
            dev = Device(host=host, user=user, password=password)
            dev.open()
            logger.success(f"Device {host} is back online")
            return dev
        except ConnectError:
            logger.debug("Device not ready yet, retrying...")
        except Exception as err:
            logger.warning(f"Unexpected error while probing: {err}")
        time.sleep(10)
    
    logger.error(f"Device did not come back online within {timeout} seconds")
    return None

def check_image_on_device(dev, remote_path, image_name):
    """Check if image file exists on the remote path."""
    logger.info(f"Checking if image exists on device at {remote_path}/{image_name}")
    fs = FS(dev)
    try:
        # Check if the directory exists
        ls_result = fs.ls(remote_path)
        if 'files' not in ls_result:
            logger.warning(f"Remote path {remote_path} not found or empty")
            return False
        
        # Check if the image exists
        for file_entry in ls_result['files']:
            if file_entry.get('name') == image_name:
                logger.success(f"Image found on device at {remote_path}/{image_name}")
                return True
                
        logger.info(f"Image not found on device")
        return False
    except RpcError as err:
        logger.error(f"Error checking for image: {err}")
        return False

def copy_image_to_device(dev, local_path, remote_path, image_name):
    """Copy image to device via SCP with proper error handling."""
    full_local_path = os.path.join(local_path, image_name)
    logger.info(f"Copying image from {full_local_path} to {remote_path}/{image_name}")
    
    # Check if local file exists
    if not os.path.exists(full_local_path):
        logger.error(f"Local file not found: {full_local_path}")
        return False
    
    # Get file size for better progress tracking
    file_size = os.path.getsize(full_local_path)
    logger.info(f"File size: {file_size/1024/1024:.2f} MB")
    
    try:
        sw = SW(dev)
        result = sw.safe_copy(
            package=full_local_path,
            remote_path=remote_path,
            progress=True
        )
        if result:
            logger.success("Image copy completed successfully")
            return True
        else:
            logger.error("Image copy failed")
            return False
    except Exception as err:
        logger.error(f"SCP error: {err}")
        return False

def install_image(dev, remote_path, image_name):
    """Install Junos software from the remote path."""
    image_name = os.path.basename(image_name)
    remote_full_path = os.path.join(remote_path, image_name)
    logger.info(f"Installing image from {remote_full_path}")
    
    try:
        sw = SW(dev)
        logger.info("Starting installation (this may take several minutes)...")
        ok, msg = sw.install(
            package=image_name,
            validate=False,
            remote_path=remote_path,  # Temp directory for installation
            progress=True,
            no_copy=True,  # File is already on device
            timeout=2400,
            checksum_timeout=400,
            checksum_algorithm='sha256'
        )
        
        if ok:
            logger.success(f"Installation successful: {msg}")
            logger.info("Initiating reboot...")
            sw.reboot()
            return True
        else:
            logger.error(f"Installation failed: {msg}")
            return False
    except Exception as err:
        logger.error(f"Installation error: {err}")
        return False

def verify_version(dev, expected_prefix):
    """Verify the device version after upgrade."""
    try:
        version = dev.facts.get("version", "")
        logger.info(f"Detected version: {version}")
        
        if version.startswith(expected_prefix):
            logger.success(f"Version verification successful: {version}")
            return True
        else:
            logger.error(f"Version mismatch. Expected prefix '{expected_prefix}' but found '{version}'")
            return False
    except Exception as err:
        logger.error(f"Version verification error: {err}")
        return False

def main():
    """Main function that coordinates the upgrade process."""
    print("\n" + "="*60)
    print(" 🔄 JUNOS OS UPGRADE UTILITY ".center(60, "="))
    print("="*60 + "\n")
    
    logger.info("Starting upgrade process")
    config = load_config()
    
    # Connect to device
    dev = connect_device(config['host'], config['user'], config['password'])
    if not dev:
        logger.error("Failed to connect to device, aborting")
        return 1
    
    try:
        # Check version before upgrade
        current_version = dev.facts.get('version')
        logger.info(f"Current version: {current_version}")
        if current_version.startswith(config['expected_version']):
            logger.info("Device is already on the expected version, no upgrade needed")
            return 0
        # Check and copy image if needed
        image_exists = check_image_on_device(dev, config['remote_path'], config['image_name'])
        if not image_exists:
            logger.info("Image not found on device, initiating copy...")
            if not copy_image_to_device(dev, config['local_image_dir'], config['remote_path'], config['image_name']):
                logger.error("Image copy failed, aborting")
                return 1
        
        # Install the image
        if install_image(dev, config['remote_path'], config['image_name']):
            # Close connection before reboot
            dev.close()
            logger.info("Device is rebooting approximately in 12 minutes...")
            logger.info("Please wait for the device to reboot and come back online...")
            # wait for device to goinf to reboot
            time.sleep(720)  # Wait for 120 seconds before probing again
            # Wait for device to come back online
            dev = probe_device(config['host'], config['user'], config['password'], config['timeout'])
            if dev:
                # Verify version after upgrade
                if verify_version(dev, config['expected_version']):
                    print("\n" + "="*60)
                    print(" ✅ UPGRADE COMPLETED SUCCESSFULLY ".center(60, "="))
                    print("="*60 + "\n")
                    return 0
                else:
                    print("\n" + "="*60)
                    print(" ❌ UPGRADE COMPLETED WITH VERSION MISMATCH ".center(60, "="))
                    print("="*60 + "\n")
                    return 1
            else:
                print("\n" + "="*60)
                print(" ❌ DEVICE REBOOT FAILED ".center(60, "="))
                print("="*60 + "\n")
                return 1
        else:
            print("\n" + "="*60)
            print(" ❌ IMAGE INSTALLATION FAILED ".center(60, "="))
            print("="*60 + "\n")
            return 1
    except Exception as err:
        logger.error(f"Unexpected error during upgrade process: {err}")
        print("\n" + "="*60)
        print(" ❌ UPGRADE PROCESS FAILED ".center(60, "="))
        print("="*60 + "\n")
        return 1
    finally:
        # Ensure we close the connection
        if dev and hasattr(dev, 'connected') and dev.connected:
            dev.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print(" ❌ UPGRADE PROCESS INTERRUPTED ".center(60, "="))
        print("="*60 + "\n")
        sys.exit(1)