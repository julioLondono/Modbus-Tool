# Modbus RTU Tool

A desktop application for testing and debugging Modbus RTU slave devices. Built with Python and tkinter, this tool provides a user-friendly interface for Modbus communication, device discovery, and real-time data visualization.

## Features

- **COMM Port Configuration**
  - Serial port selection
  - Configurable baud rate, data bits, and parity
  - Settings persistence across sessions

- **Device Discovery**
  - Scan for Modbus devices in a specified address range
  - Real-time progress tracking
  - Visual feedback with progress bar
  - Device list with connection status

- **Connection Management**
  - Double-click to connect/disconnect from devices
  - Robust port handling with automatic cleanup
  - Connection retry mechanism
  - Clear status indicators

- **Real-time Data Visualization**
  - Live plotting of register values
  - Multiple register selection via checkboxes
  - Time-based x-axis with scrolling view
  - Auto-scaling y-axis
  - Clear legend and grid lines

## Requirements

- Python 3.x
- Windows 10/11
- USB-to-Serial adapter

## Installation

### Option 1: Executable (Windows)
1. Download the latest release from the [Releases](https://github.com/julioLondono/Modbus-Tool/releases) page
2. Extract the ModbusTool.zip file
3. Run `Modbus Tool.exe`

### Option 2: From Source
1. Clone the repository:
```bash
git clone https://github.com/julioLondono/Modbus-Tool.git
cd Modbus-Tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
   - If using the executable, double-click `Modbus Tool.exe`
   - If running from source: `python main_window.py`

2. Configure COM Port:
   - Click "COMM Setup"
   - Select your COM port
   - Configure baud rate, data bits, and parity
   - Click "OK" to save settings

3. Discover Devices:
   - Enter start and end addresses (1-247)
   - Click "Start Scan"
   - Monitor progress in the status bar
   - View discovered devices in the list

4. Connect to Devices:
   - Double-click a discovered device to connect
   - Double-click again to disconnect

5. Monitor Register Values:
   - Select registers to monitor by clicking checkboxes
   - Start live polling
   - Click the Graph button to open visualization
   - Watch real-time value changes

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pymodbus](https://github.com/pymodbus-dev/pymodbus)
- Uses [pyserial](https://github.com/pyserial/pyserial) for serial communication
- Uses [matplotlib](https://matplotlib.org/) for data visualization
