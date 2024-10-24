from character_capacity import *

alphanumeric = {x:i for i, x in enumerate([*"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"])}
#print(alphanumeric)

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
    def __init__(self, encoding = QREncoding.ALPHA, quality = "Q", version = 1, message=""):
        self.encoding = encoding
        self.quality = quality
        self.version = version
        self.char_count_bits = get_char_count_bits(self.version, self.encoding)

        # Get max capacity of message from args
        # If message len > max len raise error
        self.message_capacity = char_capacity[(self.version, self.quality, self.encoding)]
        if len(message) > self.message_capacity:
            raise ValueError("Chosen message exceeds QR code capacity")
        
        # Encode message in to binary
        if self.encoding == QREncoding.ALPHA:
            message = message.upper()
        else:
            raise NotImplementedError("Only alphanumeric messages can be suppored")

    
qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO, WORLD")

