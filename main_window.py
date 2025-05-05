import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import json
import os
import threading
from client import ModbusToolClient
from time import sleep
import serial

class CommSetupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("COMM Setup")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create and pack widgets
        self.create_widgets()
        
        # Center the dialog on parent
        self.center_on_parent()

    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Serial Port Selection
        ttk.Label(main_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(main_frame, textvariable=self.port_var)
        self.port_combo['values'] = self.get_available_ports()
        self.port_combo.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Baud Rate Selection
        ttk.Label(main_frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.baud_var = tk.StringVar(value="9600")
        baud_rates = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        self.baud_combo = ttk.Combobox(main_frame, textvariable=self.baud_var, values=baud_rates)
        self.baud_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Data Bits Selection
        ttk.Label(main_frame, text="Data Bits:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.data_bits_var = tk.StringVar(value="8")
        data_bits = ['7', '8']
        self.data_bits_combo = ttk.Combobox(main_frame, textvariable=self.data_bits_var, values=data_bits)
        self.data_bits_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Parity Selection
        ttk.Label(main_frame, text="Parity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.parity_var = tk.StringVar(value="None")
        parity_options = ['None', 'Even', 'Odd']
        self.parity_combo = ttk.Combobox(main_frame, textvariable=self.parity_var, values=parity_options)
        self.parity_combo.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        # Configure grid
        main_frame.columnconfigure(1, weight=1)

    def get_available_ports(self):
        """Get list of available serial ports"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def center_on_parent(self):
        """Center the dialog on parent window"""
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def on_ok(self):
        # Here we'll add the logic to save the settings
        self.result = {
            'port': self.port_var.get(),
            'baudrate': int(self.baud_var.get()),
            'bytesize': int(self.data_bits_var.get()),
            'parity': self.parity_var.get().lower(),
            'stopbits': 1  # Default to 1 stop bit
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class MainWindow(tk.Tk):
    def validate_address(self, value):
        """Validate address entry"""
        # Allow empty value for deletion
        if value == "":
            return True
        # Check if value is numeric and in valid range
        try:
            num = int(value)
            return 1 <= num <= 247
        except ValueError:
            return False

    def __init__(self):
        super().__init__()
        
        self.title("Modbus RTU Tool")
        self.geometry("1200x600")
        
        # Initialize variables
        self.scanning = False
        self.scan_thread = None
        self.modbus_client = None
        self.connected_device = None
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left frame for COMM setup and device discovery (fixed width)
        self.left_frame = ttk.Frame(self.main_frame, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_frame.pack_propagate(False)  # Maintain fixed width
        
        # Create right frame for registers data
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create COMM Setup button
        self.comm_setup_btn = ttk.Button(
            self.left_frame, 
            text="COMM Setup",
            command=self.show_comm_setup
        )
        self.comm_setup_btn.pack(anchor=tk.W)
        
        # Create configuration display frame
        self.config_frame = ttk.LabelFrame(self.left_frame, text="Current Configuration", padding="10")
        self.config_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
        
        # Configuration labels
        self.port_label = ttk.Label(self.config_frame, text="Port: Not configured")
        self.port_label.pack(anchor=tk.W)
        
        self.baud_label = ttk.Label(self.config_frame, text="Baud Rate: Not configured")
        self.baud_label.pack(anchor=tk.W)
        
        self.data_bits_label = ttk.Label(self.config_frame, text="Data Bits: Not configured")
        self.data_bits_label.pack(anchor=tk.W)
        
        self.parity_label = ttk.Label(self.config_frame, text="Parity: Not configured")
        self.parity_label.pack(anchor=tk.W)
        
        # Create Device Discovery frame
        self.discovery_frame = ttk.LabelFrame(self.left_frame, text="Device Discovery", padding="10")
        self.discovery_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
        
        # Create address range frame with fixed width
        addr_frame = ttk.Frame(self.discovery_frame)
        addr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start address (left-aligned)
        start_frame = ttk.Frame(addr_frame)
        start_frame.pack(side=tk.LEFT)
        ttk.Label(start_frame, text="Start:", width=6, anchor='e').pack(side=tk.LEFT)
        vcmd = (self.register(self.validate_address), '%P')
        self.start_addr = ttk.Entry(start_frame, width=4, justify=tk.CENTER, validate='key', validatecommand=vcmd)
        self.start_addr.pack(side=tk.LEFT, padx=(2, 10))
        self.start_addr.insert(0, "1")
        
        # End address (right-aligned)
        end_frame = ttk.Frame(addr_frame)
        end_frame.pack(side=tk.LEFT)
        ttk.Label(end_frame, text="End:", width=4, anchor='e').pack(side=tk.LEFT)
        self.end_addr = ttk.Entry(end_frame, width=4, justify=tk.CENTER, validate='key', validatecommand=vcmd)
        self.end_addr.pack(side=tk.LEFT, padx=2)
        self.end_addr.insert(0, "10")
        
        self.start_addr.config(validate='key', validatecommand=vcmd)
        self.end_addr.config(validate='key', validatecommand=vcmd)
        
        # Buttons frame
        button_frame = ttk.Frame(self.discovery_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Start/Stop Scan buttons
        self.start_scan_btn = ttk.Button(button_frame, text="Start Scan", command=self.start_scan)
        self.start_scan_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_scan_btn = ttk.Button(button_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_scan_btn.pack(side=tk.LEFT)
        
        # Progress bar frame
        self.progress_frame = ttk.Frame(self.discovery_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar and status label
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(self.progress_frame, text="")
        self.status_label.pack(fill=tk.X)
        
        # Device list
        ttk.Label(self.discovery_frame, text="Discovered Devices:").pack(anchor=tk.W, pady=(10, 5))
        self.device_list = ttk.Treeview(self.discovery_frame, columns=("address", "status"), show="headings", height=6)
        self.device_list.heading("address", text="Device Address")
        self.device_list.heading("status", text="Status")
        self.device_list.column("address", width=100)
        self.device_list.column("status", width=100)
        self.device_list.pack(fill=tk.X)
        
        # Bind double-click event for connection
        self.device_list.bind("<Double-1>", self.connect_to_device)
        
        # Create Registers Data frame
        self.registers_frame = ttk.LabelFrame(self.right_frame, text="Registers Data", padding="10")
        self.registers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Register type selection frame
        self.register_type_frame = ttk.Frame(self.registers_frame)
        self.register_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Register type radio buttons
        self.register_type = tk.StringVar(value="holding")
        register_types = [
            ("Read Coils (01)", "coils"),
            ("Read Discrete Inputs (02)", "discrete"),
            ("Read Holding Registers (03)", "holding"),
            ("Read Input Registers (04)", "input")
        ]
        
        # Add radio buttons in a single row
        for text, value in register_types:
            ttk.Radiobutton(
                self.register_type_frame,
                text=text,
                value=value,
                variable=self.register_type,
                command=self.read_registers
            ).pack(side=tk.LEFT, padx=8)
        
        # Register count and device info frame
        info_frame = ttk.Frame(self.registers_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Register count and device info in single row
        ttk.Label(info_frame, text="Number of registers:").pack(side=tk.LEFT)
        self.register_count = ttk.Spinbox(
            info_frame,
            from_=1,
            to=100,
            width=5,
            command=self.read_registers
        )
        self.register_count.set("10")
        self.register_count.pack(side=tk.LEFT, padx=(5, 15))
        
        # Connected device info
        ttk.Label(info_frame, text="Device Connected to:").pack(side=tk.LEFT)
        self.connected_device_label = ttk.Label(info_frame, text="None")
        self.connected_device_label.pack(side=tk.LEFT, padx=5)
        
        # Register values display
        self.register_display = ttk.Treeview(
            self.registers_frame,
            columns=("address", "value"),
            show="headings",
            height=15
        )
        self.register_display.heading("address", text="Address")
        self.register_display.heading("value", text="Value")
        self.register_display.column("address", width=100)
        self.register_display.column("value", width=100)
        self.register_display.pack(fill=tk.BOTH, expand=True)
        
        # Load last configuration
        self.config = self.load_configuration()
        if self.config:
            self.update_config_display(self.config)

    def show_comm_setup(self):
        dialog = CommSetupDialog(self)
        # If there's existing configuration, set it as default
        if self.config:
            dialog.port_var.set(self.config.get('port', ''))
            dialog.baud_var.set(str(self.config.get('baudrate', '9600')))
            dialog.data_bits_var.set(str(self.config.get('bytesize', '8')))
            dialog.parity_var.set(self.config.get('parity', 'none').capitalize())
            
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            self.config = dialog.result
            self.update_config_display(self.config)
            self.save_configuration(self.config)
            
    def update_config_display(self, config):
        """Update the configuration display labels"""
        self.port_label.config(text=f"Port: {config['port']}")
        self.baud_label.config(text=f"Baud Rate: {config['baudrate']}")
        self.data_bits_label.config(text=f"Data Bits: {config['bytesize']}")
        self.parity_label.config(text=f"Parity: {config['parity'].capitalize()}")
        
    def save_configuration(self, config):
        """Save configuration to a JSON file"""
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, 'comm_config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f)
            
    def load_configuration(self):
        """Load configuration from JSON file"""
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, 'comm_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
        
    def start_scan(self):
        """Start the device discovery scan"""
        if not self.config:
            messagebox.showerror("Error", "Please configure COM port settings first")
            return
            
        # If there's an existing scan running, stop it first
        if self.scanning:
            self.stop_scan()
            sleep(0.5)  # Give time for cleanup
            
        try:
            start = int(self.start_addr.get())
            end = int(self.end_addr.get())
            if not (1 <= start <= end <= 247):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid address range. Use numbers between 1-247")
            return
            
        # Clear existing items
        for item in self.device_list.get_children():
            self.device_list.delete(item)
            
        # Reset progress bar and status
        self.progress_var.set(0)
        self.status_label.config(text="Initializing scan...")
        
        self.scanning = True
        self.start_scan_btn.config(state=tk.DISABLED)
        self.stop_scan_btn.config(state=tk.NORMAL)
        
        # Start scanning thread
        self.scan_thread = threading.Thread(target=self.scan_worker, args=(start, end))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def stop_scan(self):
        """Stop the device discovery scan"""
        self.scanning = False
        self.start_scan_btn.config(state=tk.NORMAL)
        self.stop_scan_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Scan stopped by user")
        
        # Wait for scan thread to finish if it exists
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1.0)
        
    def scan_worker(self, start_addr, end_addr):
        """Worker function for device scanning"""
        client = None
        try:
            # Ensure any previous client is properly disconnected
            if hasattr(self, 'modbus_client') and self.modbus_client:
                self.modbus_client.disconnect()
                self.modbus_client = None
                sleep(1.0)  # Give extra time for port cleanup
            
            # Convert parity from text to single letter
            parity_map = {'none': 'N', 'even': 'E', 'odd': 'O'}
            parity = parity_map.get(self.config['parity'].lower(), 'N')
            
            # Create Modbus client
            client = ModbusToolClient(
                mode='rtu',
                port=self.config['port'],
                baudrate=int(self.config['baudrate']),
                parity=parity_map[self.config['parity'].lower()],
                bytesize=int(self.config['bytesize']),
                stopbits=int(self.config['stopbits']),
                timeout=0.05
            )
            
            # Try to connect multiple times
            max_retries = 3
            for retry in range(max_retries):
                if client.connect():
                    break
                sleep(1.0)  # Wait between retries
                if retry == max_retries - 1:
                    raise Exception("Failed to connect to COM port after multiple attempts")
            
            total_devices = end_addr - start_addr + 1
            devices_scanned = 0
            timeout = 0.05  # Reduced timeout for faster scanning
            
            for addr in range(start_addr, end_addr + 1):
                if not self.scanning:
                    break
                
                # Update progress
                devices_scanned += 1
                progress = (devices_scanned / total_devices) * 100
                self.after(0, lambda p=progress: self.progress_var.set(p))
                self.after(0, lambda a=addr: self.status_label.config(
                    text=f"Scanning device {a} ({devices_scanned}/{total_devices})")
                )
                
                # Try to read from device with shorter timeout
                try:
                    result = client.read_holding_registers(0, 1, unit=addr)
                    if result is not None:
                        self.after(0, lambda a=addr: self.device_list.insert("", tk.END, values=(a, "Available"), tags=()))
                except:
                    pass  # Skip errors for faster scanning
                
                sleep(timeout)  # Reduced delay between scans
            
            self.after(0, lambda: self.status_label.config(text="Scan complete"))
            
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: messagebox.showerror("Error", f"Scan error: {error_msg}"))
        finally:
            # Ensure client is properly disconnected
            if client:
                try:
                    client.disconnect()
                    sleep(1.0)  # Give time for port cleanup
                except:
                    pass
            self.after(0, self.stop_scan)
            
    def __del__(self):
        """Cleanup when the window is destroyed"""
        if hasattr(self, 'modbus_client') and self.modbus_client:
            try:
                self.modbus_client.disconnect()
            except:
                pass
    
    def clear_register_display(self):
        """Clear all values from the register display"""
        for item in self.register_display.get_children():
            self.register_display.delete(item)

    def read_registers(self, *args):
        """Read registers based on selected type"""
        if not hasattr(self, 'modbus_client') or not self.modbus_client or not self.connected_device:
            self.clear_register_display()
            return
            
        try:
            count = int(self.register_count.get())
            if not (1 <= count <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid register count. Use numbers between 1-100")
            return
            
        # Clear existing values
        for item in self.register_display.get_children():
            self.register_display.delete(item)
            
        try:
            # Read values based on selected type
            reg_type = self.register_type.get()
            if reg_type == "coils":
                values = self.modbus_client.read_coils(0, count, self.connected_device)
            elif reg_type == "discrete":
                values = self.modbus_client.read_discrete_inputs(0, count, self.connected_device)
            elif reg_type == "holding":
                values = self.modbus_client.read_holding_registers(0, count, self.connected_device)
            else:  # input registers
                values = self.modbus_client.read_input_registers(0, count, self.connected_device)
                
            if values is not None:
                for i, value in enumerate(values):
                    self.register_display.insert("", tk.END, values=(i, value))
            else:
                messagebox.showerror("Error", f"Failed to read {reg_type}")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading registers: {e}")
    
    def connect_to_device(self, event):
        """Connect to the selected device"""
        if not self.config:
            messagebox.showerror("Error", "Please configure COM port settings first")
            return
            
        selection = self.device_list.selection()
        if not selection:
            return
            
        # Get device address from selection
        address = int(self.device_list.item(selection[0])["values"][0])
        
        # If clicking the same device, disconnect it
        if self.connected_device == address:
            if self.modbus_client:
                self.modbus_client.disconnect()
                self.modbus_client = None
            self.connected_device = None
            self.device_list.item(selection[0], values=(address, "Available"), tags=())
            # Clear display and update device label when disconnecting
            self.clear_register_display()
            self.connected_device_label.config(text="None")
            return
            
        # Disconnect from any previously connected device
        if self.modbus_client:
            self.modbus_client.disconnect()
            
        # Convert parity from text to single letter
        parity_map = {'none': 'N', 'even': 'E', 'odd': 'O'}
        parity = parity_map.get(self.config['parity'].lower(), 'N')
        
        try:
            # Create new Modbus client
            self.modbus_client = ModbusToolClient(
                port=self.config['port'],
                mode='rtu',
                baudrate=int(self.config['baudrate']),
                parity=parity,
                bytesize=int(self.config['bytesize'])
            )
            
            if self.modbus_client.connect():
                # Update previously connected device (if any)
                if self.connected_device:
                    for item in self.device_list.get_children():
                        if int(self.device_list.item(item)['values'][0]) == self.connected_device:
                            self.device_list.item(item, values=(self.connected_device, "Available"), tags=())
                            break
                
                # Update new connected device
                self.connected_device = address
                self.device_list.item(selection[0], values=(address, "Connected"), tags=("connected",))
                self.device_list.tag_configure("connected", background="#90EE90")
                # Update connected device label and read registers
                self.connected_device_label.config(text=str(address))
                self.clear_register_display()
                self.read_registers()
            else:
                messagebox.showerror("Error", "Failed to connect to device")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
