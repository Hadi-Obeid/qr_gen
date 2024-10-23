from enum import Enum

class QREncoding(Enum):
    # Values correspond to QR mode indicators in binary
    # e.g
    NUMERIC = 0b0001
    ALPHA = 0b0010
    BYTE = 0b0100
    KANJI = 0b1000
    ECI = 0b0111

alphanumeric = {x:i for i, x in enumerate([*"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"])}
print(alphanumeric)

def get_char_count_bits(version, encoding):
    if version < 1 or version > 40:
        raise ValueError("ERROR: QR Version must be between 1 and 40!")
    match encoding:
        case QREncoding.NUMERIC:
            if version < 10:
                return 10
            elif version < 27:
                return 12
            else:
                return 14
        case QREncoding.ALPHA:
            if version < 10:
                return 9
            elif version < 27:
                return 11
            else:
                return 13
        case QREncoding.BYTE:
            return 8 if version < 10 else 16
        case QREncoding.KANJI:
            if version < 10:
                return 8
            elif version < 27:
                return 10
            else:
                return 12

class QRCode:
    def __init__(self, encoding = QREncoding.ALPHA, quality = "Q", version = 1):
        self.encoding = encoding
        self.quality = quality
        self.version = version
        self.char_count_bits = get_char_count_bits(self.version, self.encoding)