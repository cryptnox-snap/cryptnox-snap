# Backup Configurations

This directory contains backup snapcraft configurations for different use cases.

## Files

### snapcraft.yaml.i2c-full
Full configuration with all interfaces including:
- `raw-usb` - USB card readers
- `hardware-observe` - Hardware detection
- `i2c` - I2C connected readers (PN532 on Raspberry Pi)
- `serial-port` - Serial card readers
- `raw-input` - Raw input devices
- `mount-observe` - Mount observation
- `removable-media` - Removable media access

**Use this for:**
- Raspberry Pi with PN532 board via I2C
- Serial-connected card readers
- Full hardware support

**Note:** This configuration requires extended manual review in the Snap Store.

## Usage

To restore full I2C support:
```bash
cp backup/snapcraft.yaml.i2c-full snap/snapcraft.yaml
```

Then rebuild:
```bash
snapcraft remote-build --build-for=amd64,arm64
```
