from character_capacity import *
#from galois_field import *
from gf256 import GF256LT as gf

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


def multiplyPolynomial(p1, p2):
    p3 = [gf(0)] * (len(p1 + p2) - 1) 
    # Polynomial multiplication
    # E.g (x + 1)(x + 2) = x**2 + (2+1)x + 2
    for i, t1 in enumerate(p1):
        for j, t2 in enumerate(p2):
            # Use exponent property to add powers 
            n = i + j
            p3[n] += (t1 * t2)
    return p3

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
        

        #if self.version == 5 and self.quality == "Q":
        #    pass
        #    self.data = '0100001101010101010001101000011001010111001001100101010111000010011101110011001000000110000100100000011001100111001001101111011011110110010000100000011101110110100001101111001000000111001001100101011000010110110001101100011110010010000001101011011011100110111101110111011100110010000001110111011010000110010101110010011001010010000001101000011010010111001100100000011101000110111101110111011001010110110000100000011010010111001100101110000011101100000100011110110000010001111011000001000111101100'

        # Use regex to break down codewords into chunks of 8 bytes
        codewords = re.findall(r"." * 8 + r"?", self.data)

        # Break down message into groups and blocks
        ec = error_correction[(self.version, self.quality)]

        group_1_blocks = ec["num-blocks-group-1"]
        group_2_blocks = ec["num-blocks-group-2"]

        group_1_codewords = ec["num-codewords-group-1"]
        group_2_codewords = ec["num-codewords-group-2"]

        total_group1_blocks = group_1_blocks * group_1_codewords
        group_1 = [codewords[group_1_codewords * b : group_1_codewords * (b + 1)] for b in range(group_1_blocks)]
        group_2 = [codewords[total_group1_blocks + group_2_codewords * b : total_group1_blocks + group_2_codewords * (b + 1)] for b in range(group_2_blocks)]

        self.gen_polynomial = [gf(1), gf(1)] # (x + a0)
        for i in range(1, ec["ec-codewords-per-block"]):
            self.gen_polynomial = multiplyPolynomial(self.gen_polynomial, [gf(1), gf(2) ** gf(i)])

        gen_poly_10 = [gf.exponentiation_table[i] for i in [0, 251, 67, 46, 61, 118, 70, 64, 94, 32, 45]]
        print([gf.logarithm_table[int(i)-1] for i in self.gen_polynomial])
    




        




    
#qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO WORLD")

qr = QRCode(QREncoding.ALPHA, "M", 1, "HELLO WORLD")

e = gf(1)
