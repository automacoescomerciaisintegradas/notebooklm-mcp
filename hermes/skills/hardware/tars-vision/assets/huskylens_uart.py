# assets/huskylens_uart.py
"""
HuskyLens I2C/UART Driver - TARS Vision
---------------------------------------
Implementação independente para extração de 21 hand landmarks.
Suporta: I2C (via smbus2) e Modo Simulação.
"""

import os
import time
import struct
from typing import List, Tuple, Optional

# Protocolo HuskyLens
HEADER = [0x55, 0xAA]
ADDRESS_BYTE = 0x11
COMMAND_REQUEST = 0x20
COMMAND_REQUEST_ALGORITHM = 0x2D
COMMAND_RETURN_INFO = 0x29
COMMAND_RETURN_BLOCK = 0x2A

# Algoritmos
ALGORITHM_HAND_LANDMARK = 0x06

try:
    from smbus2 import SMBus, i2c_msg
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False

class HuskyLensDriver:
    """
    Driver otimizado para HuskyLens focado em Hand Landmarks.
    Independente de bibliotecas externas (exceto smbus2 para hardware).
    """

    def __init__(self, bus_id: int = 1, address: int = 0x10):
        self.address = address
        self.bus_id = bus_id
        self.bus = None
        self.connected = False
        
        if HAS_SMBUS:
            try:
                self.bus = SMBus(bus_id)
                self.connected = True
                self._setup_algorithm()
            except Exception as e:
                print(f"[HuskyLens] Erro ao iniciar I2C: {e}")
                self.connected = False
        else:
            print("[HuskyLens] smbus2 não encontrado. Iniciando modo SIMULAÇÃO.")

    def _setup_algorithm(self):
        """Configura o HuskyLens para o modo de reconhecimento de mãos."""
        if self.connected:
            self._send_command(COMMAND_REQUEST_ALGORITHM, [ALGORITHM_HAND_LANDMARK, 0x00])
            time.sleep(0.5)  # Tempo para troca de algoritmo

    def _calculate_checksum(self, data: List[int]) -> int:
        """Soma de verificação padrão do protocolo HuskyLens."""
        return sum(data) & 0xFF

    def _send_command(self, command: int, data: List[int] = []):
        """Envia um pacote formatado para o HuskyLens."""
        if not self.connected: return
        
        length = len(data)
        packet_body = [ADDRESS_BYTE, length, command] + data
        checksum = self._calculate_checksum(packet_body)
        full_packet = HEADER + packet_body + [checksum]
        
        try:
            # Envia o cabeçalho como 'registro' e o resto como dados
            msg = i2c_msg.write(self.address, full_packet)
            self.bus.i2c_rdwr(msg)
        except Exception as e:
            print(f"[HuskyLens] Erro no envio: {e}")
            self.connected = False

    def _read_packet(self, timeout=0.1) -> Optional[dict]:
        """Lê e valida um pacote de resposta do HuskyLens."""
        if not self.connected: return None
        
        try:
            # Primeiro lemos o cabeçalho fixo (5 bytes: Header(2), Addr(1), Len(1), Cmd(1))
            # No I2C do HuskyLens, precisamos ler o stream
            read_msg = i2c_msg.read(self.address, 5)
            self.bus.i2c_rdwr(read_msg)
            header_data = list(read_msg)
            
            if header_data[0:2] != HEADER:
                return None
                
            length = header_data[3]
            command = header_data[4]
            
            # Lemos o payload + checksum
            payload_msg = i2c_msg.read(self.address, length + 1)
            self.bus.i2c_rdwr(payload_msg)
            payload_data = list(payload_msg)
            
            payload = payload_data[:-1]
            checksum_received = payload_data[-1]
            
            # Validação
            check_data = [ADDRESS_BYTE, length, command] + payload
            if self._calculate_checksum(check_data) == checksum_received:
                return {"command": command, "data": payload}
        except Exception:
            return None
        return None

    def get_landmarks(self) -> List[Tuple[int, int]]:
        """
        Obtém os 21 pontos da mão.
        Em modo de hardware, processa o protocolo. 
        Em modo simulação, gera pontos dinâmicos.
        """
        if not self.connected:
            return self._generate_mock_landmarks()

        # Solicita dados
        self._send_command(COMMAND_REQUEST)
        
        # O HuskyLens retorna primeiro um INFO packet (0x29)
        # Seguido por blocos ou um comando específico de landmarks dependendo do firmware
        # Para simplificar e garantir independência, buscamos o padrão de 42 bytes (21x2)
        
        response = self._read_packet()
        if response and response["command"] == COMMAND_RETURN_INFO:
            # Se o HuskyLens estiver no modo Hand Landmark (0.5.1+), 
            # ele retorna os pontos nos pacotes subsequentes ou em um bloco grande.
            # Implementação baseada no firmware estável:
            landmarks = []
            # Tentativa de ler o bloco de pontos
            points_packet = self._read_packet()
            if points_packet and len(points_packet["data"]) >= 42:
                raw = points_packet["data"]
                for i in range(0, 42, 2):
                    # HuskyLens envia X e Y (ajustar escala se necessário)
                    x = raw[i] 
                    y = raw[i+1]
                    landmarks.append((x, y))
            return landmarks
            
        return []

    def _generate_mock_landmarks(self) -> List[Tuple[int, int]]:
        """Gera pontos de mão simulados para desenvolvimento sem hardware."""
        import math
        t = time.time() * 2
        base_x, base_y = 160, 120
        points = []
        # Palma e 5 dedos
        for i in range(21):
            offset_x = math.sin(t + i*0.5) * 20
            offset_y = math.cos(t + i*0.3) * 20
            points.append((base_x + offset_x, base_y + offset_y))
        return points

    def close(self):
        if self.bus:
            self.bus.close()

if __name__ == "__main__":
    driver = HuskyLensDriver()
    print("Iniciando leitura de Hand Landmarks (Pressione Ctrl+C para sair)")
    try:
        while True:
            pts = driver.get_landmarks()
            if pts:
                print(f"Detectados {len(pts)} pontos. Ex: {pts[0]}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        driver.close()
