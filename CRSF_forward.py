# this runs on the pi 

# uses the UART on GPIO 14 and 13 

import serial 

import socket 

import threading 

import time 

  

class CRSF_Final: 

    def __init__(self): 

        # RPi 5 Hardware UART 

        self.ser = serial.Serial('/dev/ttyAMA0', 420000, timeout=0.1) 

        self.channels = [1500] * 16 

        self.channels[2] = 1000 # Throttle 

        self.channels[4] = 1000 # AUX 1 (Arm) 

        self.running = True 

  

    def pwm_to_crsf(self, pwm): 

        # Precise scaling to prevent "out of range" errors 

        pwm = max(1000, min(2000, pwm)) 

        return int((pwm - 1000) * 1.6384 + 191) 

  

    def crc8_dvb_s2(self, data): 

        crc = 0 

        for b in data: 

            crc ^= b 

            for _ in range(8): 

                crc = (crc << 1) ^ 0xD5 if crc & 0x80 else crc << 1 

                crc &= 0xFF 

        return crc 

  

    def pack_channels(self): 

        payload = bytearray(22) 

        bit_buf, bit_count, byte_idx = 0, 0, 0 

        for i in range(16): 

            val = self.pwm_to_crsf(self.channels[i]) 

            bit_buf |= (val & 0x07FF) << bit_count 

            bit_count += 11 

            while bit_count >= 8 and byte_idx < 22: 

                payload[byte_idx] = bit_buf & 0xFF 

                bit_buf >>= 8 

                bit_count -= 8 

                byte_idx += 1 

        return payload 

  

    def send_loop(self): 

        print("RC Pulse Active...") 

        while self.running: 

            try: 

                payload = self.pack_channels() 

                packet = bytearray([0xC8, 24, 0x16]) + payload 

                packet.append(self.crc8_dvb_s2(packet[2:])) 

                self.ser.write(packet) 

                time.sleep(0.02) # 50Hz is mandatory 

            except Exception as e: 

                print(f"Serial Error: {e}") 

  

if __name__ == '__main__': 

    backend = CRSF_Final() 

    threading.Thread(target=backend.send_loop, daemon=True).start() 

  

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    sock.bind(('0.0.0.0', 5005)) 

     

    while True: 

        data, _ = sock.recvfrom(1024) 

        try: 

            # R, P, T, Y, AUX1 

            v = list(map(int, data.decode().split(','))) 

            backend.channels[0:5] = v[0:5] 

        except: 

            continue 
