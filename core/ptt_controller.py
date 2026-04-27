import serial
import logging

class PTTController:
    def __init__(self):
        self.ser = None
        self.port = None
        self.pin = 'RTS'

    def setup(self, port, pin='RTS High'):
        """
        Configures the serial port for PTT control.
        pin can be 'RTS High', 'RTS Low', 'DTR High', 'DTR Low'.
        """
        self.port = port
        self.pin = pin # Keep original casing for logic
        
        if self.ser and self.ser.is_open:
            self.ser.close()
            
        if not self.port or self.port == 'None':
            logging.info("PTT Control disabled (No port selected).")
            return
            
        try:
            self.ser = serial.Serial(self.port)
            # Ensure PTT is closed initially (RX state)
            self.set_ptt(False)
            logging.info(f"PTT configured on {self.port} using {self.pin} mode.")
        except Exception as e:
            logging.error(f"Failed to open PTT serial port {self.port}: {e}")
            self.ser = None

    def set_ptt(self, state: bool):
        """
        Sets the PTT state. True = Transmit (ON), False = Receive (OFF).
        """
        if not self.ser or not self.ser.is_open:
            return
            
        try:
            # Logic:
            # RTS High: TX ON -> RTS=True, TX OFF -> RTS=False
            # RTS Low:  TX ON -> RTS=False, TX OFF -> RTS=True
            # DTR High: TX ON -> DTR=True, TX OFF -> DTR=False
            # DTR Low:  TX ON -> DTR=False, TX OFF -> DTR=True
            
            if 'RTS' in self.pin:
                if 'High' in self.pin:
                    self.ser.rts = state
                else: # RTS Low
                    self.ser.rts = not state
            elif 'DTR' in self.pin:
                if 'High' in self.pin:
                    self.ser.dtr = state
                else: # DTR Low
                    self.ser.dtr = not state
                
            state_str = "ON (TX)" if state else "OFF (RX)"
            logging.info(f"PTT {self.pin} set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set PTT state: {e}")

    def trigger(self, state: bool):
        """Callback suitable for passing to the audio engine."""
        self.set_ptt(state)

# Global instance
ptt_instance = PTTController()
