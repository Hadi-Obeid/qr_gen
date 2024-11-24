from character_capacity import *
from itertools import zip_longest

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

def alphanumeric_coding(message):
    out = []
    for pair in zip_longest(message[0::2], message[1::2]):
        if pair[1] is None:
            out.append(format(alphanumeric[pair[0]], "06b"))
        else:
            out.append(format((45 * alphanumeric[pair[0]]) + alphanumeric[pair[1]], "011b"))
    return out

class QRCode:
    def __init__(self, encoding = QREncoding.ALPHA, quality = "Q", version = 1, message=""):
        self.encoding = encoding
        self.quality = quality
        self.version = version
        self.char_count_bits = get_char_count_bits(self.version, self.encoding)
        self.data = ""

        # Get max capacity of message from args
        # If message len > max len raise error
        self.message_capacity = char_capacity[(self.version, self.quality, self.encoding)]
        if len(message) > self.message_capacity:
            raise ValueError("Chosen message exceeds QR code capacity")

        self.data += format(self.encoding.value, "04b")
        # Encode message in to binary
        if self.encoding == QREncoding.ALPHA:
            message = message.upper()
            self.data += format(len(message), f"0{self.char_count_bits}b")
            self.data += ''.join(alphanumeric_coding(message))

        max_codewords = error_correction[(self.version, self.quality)]["total-codewords"]
        max_bits = max_codewords * 8
        # Add terminator (up to 4 0s)
        self.data += "0" * clamp(0, 4, max_bits - len(self.data))

        # Pad with zeros until multiple of 8
        self.data += "0" * (8 - len(self.data) % 8)

        # Add pad byte pattern 11101100 00010001
        remaining_bytes = (max_bits - len(self.data)) // 8
        for i in range(0, remaining_bytes):
            self.data += ("11101100", "00010001")[i % 2]



    
qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO WORLD")

