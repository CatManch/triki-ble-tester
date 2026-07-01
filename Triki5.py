import asyncio
import struct
import pygame
from bleak import BleakClient

ADDRESS = "EE:B9:8E:E4:5F:47"
WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NOTIFY_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Pozycja kwadratu
box_x = 400
box_y = 300
data_buffer = bytearray()

# Zmienne do kalibracji
calibration_offsets = {"x": 0, "y": 0, "z": 0}
calibration_samples = []
is_calibrated = False
trigger_calibration = False
CALIBRATION_LIMIT = 40

# --- PARAMETRY KONTROLI (Możesz je potem doregulować) ---
DEADZONE = 40        # Zmniejszone, bo przy poprawnej synchronizacji szum będzie mniejszy
SENSITIVITY = 0.01   # Średnia czułość
MAX_SPEED = 15       # Maksymalny przeskok na klatkę
# --------------------------------------------------------

def parse_imu_data(payload):
    """Dekoduje 10-bajtową paczkę danych IMU (Little Endian, int16)"""
    try:
        header, x, y, z, extra = struct.unpack("<hhhhh", payload[:10])
        return x, y, z
    except Exception:
        return None

def callback(sender, data):
    global data_buffer, box_x, box_y, is_calibrated, calibration_offsets, calibration_samples, trigger_calibration
    data_buffer.extend(data)
    
    # Przetwarzaj bufor dopóki ma przynajmniej 10 bajtów
    while len(data_buffer) >= 10:
        # KLUCZOWE: Szukamy początku pakietu (nagłówek 0x22, czyli 34)
        if data_buffer[0] == 34:
            packet = data_buffer[:10]
            del data_buffer[:10] # Usuwamy przetworzony pakiet
            
            res = parse_imu_data(packet)
            if res:
                raw_x, raw_y, raw_z = res
                
                # Faza 1: Kalibracja na żądanie (klawisz K)
                if trigger_calibration:
                    calibration_samples.append((raw_x, raw_y, raw_z))
                    if len(calibration_samples) >= CALIBRATION_LIMIT:
                        avg_x = sum(p[0] for p in calibration_samples) // len(calibration_samples)
                        avg_y = sum(p[1] for p in calibration_samples) // len(calibration_samples)
                        avg_z = sum(p[2] for p in calibration_samples) // len(calibration_samples)
                        calibration_offsets = {"x": avg_x, "y": avg_y, "z": avg_z}
                        
                        box_x = 400
                        box_y = 300
                        trigger_calibration = False
                        is_calibrated = True
                        print(f"\n[!] SYNCHRONIZACJA I REKALIBRACJA OK! Offsety: {calibration_offsets}")
                    continue
                
                # Faza 2: Sterowanie po udanej kalibracji
                if is_calibrated:
                    acc_x = raw_x - calibration_offsets["x"]
                    acc_y = raw_y - calibration_offsets["y"]
                    
                    # Filtrowanie martwej strefy
                    move_x = acc_x if abs(acc_x) > DEADZONE else 0
                    move_y = acc_y if abs(acc_y) > DEADZONE else 0
                    
                    step_x = int(move_x * SENSITIVITY)
                    step_y = int(move_y * SENSITIVITY)
                    
                    # Ograniczenie prędkości
                    step_x = max(-MAX_SPEED, min(MAX_SPEED, step_x))
                    step_y = max(-MAX_SPEED, min(MAX_SPEED, step_y))
                    
                    if step_x != 0 or step_y != 0:
                        print(f"X: {step_x:3d} | Y: {step_y:3d}")
                    
                    box_x += step_x
                    box_y -= step_y
                    
                    box_x = max(20, min(780, box_x))
                    box_y = max(20, min(580, box_y))
        else:
            # Jeśli pierwszy bajt to NIE jest 34, usuwamy go i sprawdzamy następny w kolejnej iteracji pętli
            del data_buffer[0]

async def run_pygame():
    global trigger_calibration, calibration_samples, is_calibrated
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Triki BLE - Stabilny Strumień")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont(None, 24)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    print("\n[!] Czyszczenie bufora i start kalibracji...")
                    calibration_samples = []
                    trigger_calibration = True
                
        screen.fill((30, 30, 40))
        
        if trigger_calibration:
            txt = font.render(f"Synchronizacja i kalibracja... {len(calibration_samples)}/{CALIBRATION_LIMIT}", True, (255, 150, 50))
        elif not is_calibrated:
            txt = font.render("Połóż Trikiego stabilnie i kliknij 'K' na klawiaturze", True, (255, 255, 100))
        else:
            txt = font.render("Strumień zsynchronizowany. Klawisz 'K' resetuje pozycję.", True, (100, 255, 100))
            
        screen.blit(txt, (20, 20))
        pygame.draw.rect(screen, (0, 255, 150), (box_x - 20, box_y - 20, 40, 40))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0.01)
        
    pygame.quit()

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Połączono:", client.is_connected)
        await client.start_notify(NOTIFY_UUID, callback)
        await client.write_gatt_char(WRITE_UUID, bytes([0x01, 0x00]), response=True)
        await client.write_gatt_char(
            WRITE_UUID, 
            bytes([0x20, 0x10, 0x00, 0xD0, 0x07, 0x34, 0x00, 0x03]), 
            response=False
        )
        await run_pygame()

asyncio.run(main())