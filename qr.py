from enum import Enum

class QREncoding(Enum):
    # Values correspond to QR mode indicators in binary
    # e.g
    NUMERIC = 0b0001
    ALPHA = 0b0010
    BYTE = 0b0100
    KANJI = 0b1000
    ECI = 0b0111

class QRCode:
    def __init__(self):
        self.encoding = QREncoding.ALPHA
