from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import serial
import serial.tools.list_ports
import time
from contextlib import contextmanager

class PortManager:
    _instances = {}
    
    @classmethod
    def get_instance(cls, port):
        if port not in cls._instances:
            cls._instances[port] = cls(port)
        return cls._instances[port]
    
    @classmethod
    def release_all(cls):
        """Release all managed ports"""
        for manager in cls._instances.values():
            manager.release()
        cls._instances.clear()
    
    def __init__(self, port):
        self.port = port
        self.in_use = False
        self._serial = None
    
    def acquire(self):
        # Always release first to ensure clean state
        self.release()
        
        try:
            # First check if port exists
            ports = [port.device for port in serial.tools.list_ports.comports()]
            if self.port not in ports:
                print(f"Port {self.port} not found")
                return False
            
            # Try to close any existing connections on this port
            try:
                temp = serial.Serial(self.port)
                temp.close()
            except:
                pass
                
            time.sleep(0.5)  # Wait longer for port to be released
            
            # Now try to acquire the port
            self._serial = serial.Serial(self.port)
            self._serial.close()
            time.sleep(0.2)
            self.in_use = True
            return True
        except Exception as e:
            print(f"Port acquisition error: {e}")
            self.release()
            return False
    
    def release(self):
        self.in_use = False  # Mark as not in use first
        try:
            if self._serial:
                self._serial.close()
                self._serial = None
            time.sleep(0.5)  # Wait longer after release
        except:
            pass

class ModbusToolClient:
    def __init__(self, mode='tcp', host='localhost', port=502, timeout=3, baudrate=9600, parity='N', bytesize=8, stopbits=1):
        self.port_manager = None
        self.port = port  # Store port separately
        """Initialize Modbus client.
        
        Args:
            mode (str): Connection mode ('tcp' or 'rtu')
            host (str): IP address for TCP mode
            port (int): Port number for TCP mode
            timeout (int): Connection timeout in seconds
        """
        self.mode = mode
        if mode == 'tcp':
            self.client = ModbusTcpClient(host=host, port=port, timeout=timeout)
        elif mode == 'rtu':
            self.client = ModbusSerialClient(
                port=port,
                timeout=timeout,
                baudrate=baudrate,
                parity=parity,
                bytesize=bytesize,
                stopbits=stopbits
            )
        else:
            raise ValueError("Mode must be 'tcp' or 'rtu'")

    def connect(self):
        """Connect to the Modbus device."""
        if self.mode == 'rtu':
            # Release any existing port managers for this port
            PortManager.release_all()
            time.sleep(0.5)  # Wait for cleanup
            
            # Try to acquire the port
            self.port_manager = PortManager.get_instance(self.port)
            if not self.port_manager.acquire():
                return False
            
        return self.client.connect()

    def disconnect(self):
        """Disconnect from the Modbus device."""
        try:
            if hasattr(self.client, 'socket') and self.client.socket:
                self.client.socket.close()
            if hasattr(self.client, 'serial') and self.client.serial:
                if self.client.serial.is_open:
                    self.client.serial.close()
            self.client.close()
        except:
            pass  # Ensure we don't throw errors during cleanup
        finally:
            # Release all port managers to ensure clean state
            PortManager.release_all()
            self.port_manager = None
            time.sleep(0.5)  # Wait for cleanup

    def read_coils(self, address, count, unit=1):
        """Read coils (function code 01)."""
        try:
            result = self.client.read_coils(address=address, count=count, slave=unit)
            if hasattr(result, 'bits'):
                return result.bits
        except ModbusException as e:
            print(f"Error reading coils: {e}")
        return None

    def read_discrete_inputs(self, address, count, unit=1):
        """Read discrete inputs (function code 02)."""
        try:
            result = self.client.read_discrete_inputs(address=address, count=count, slave=unit)
            if hasattr(result, 'bits'):
                return result.bits
        except ModbusException as e:
            print(f"Error reading discrete inputs: {e}")
        return None

    def read_holding_registers(self, address, count, unit=1):
        """Read holding registers (function code 03)."""
        try:
            result = self.client.read_holding_registers(address=address, count=count, slave=unit)
            if hasattr(result, 'registers'):
                return result.registers
        except ModbusException as e:
            print(f"Error reading holding registers: {e}")
        return None

    def read_input_registers(self, address, count, unit=1):
        """Read input registers (function code 04)."""
        try:
            result = self.client.read_input_registers(address=address, count=count, slave=unit)
            if hasattr(result, 'registers'):
                return result.registers
        except ModbusException as e:
            print(f"Error reading input registers: {e}")
        return None
