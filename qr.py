from character_capacity import *
#from galois_field import *
from gf256 import GF256LT as gf
import colorama

from itertools import zip_longest, chain, product
import copy

alphanumeric = {x:i for i, x in enumerate([*"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"])}


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

def generateECC(message, generator, n):
    # Len generator -> num of ecc code words
    num_steps = len(message)

    message += [gf(0)] * (n)
    generator_p = generator + [gf(0)] * abs(len(message) - len(generator))

    factor = message[0]
    for i in range(num_steps):
        result = [factor * g for g in generator_p]
        message = [m + r for m, r in zip(message, result)]
        if message[0] == gf(0):
            message.pop(0)

        factor = message[0]
    return message

def square(code, y, x, w, v):
    for i in range(y, y + w):
        for j in range(x, x + w):
            code[j][i] = v

def line_h(code, y, x, l, v):
    for i in range(x, x + l):
        code[y][i] = v

def line_v(code, y, x, l, v):
    for i in range(y, y + l):
        code[i][x] = v

def insert_finder(code, y, x):
    square(code, y, x, 7, "1")
    square(code, y+1, x+1, 5, "0")
    square(code, y+2, x+2, 3, "1")

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
        

        if self.version == 5 and self.quality == "Q":
            pass
            self.data = '0100001101010101010001101000011001010111001001100101010111000010011101110011001000000110000100100000011001100111001001101111011011110110010000100000011101110110100001101111001000000111001001100101011000010110110001101100011110010010000001101011011011100110111101110111011100110010000001110111011010000110010101110010011001010010000001101000011010010111001100100000011101000110111101110111011001010110110000100000011010010111001100100001000011101100000100011110110000010001111011000001000111101100'
        # Use regex to break down codewords into chunks of 8 bytes
        codewords = re.findall(r"." * 8 + r"?", self.data)

        # Break down message into groups and blocks
        ec = error_correction[(self.version, self.quality)]

        group_1_blocks = ec["num-blocks-group-1"]
        group_2_blocks = ec["num-blocks-group-2"]

        group_1_codewords = ec["num-codewords-group-1"]
        group_2_codewords = ec["num-codewords-group-2"]

        num_ecc_codewords = ec["ec-codewords-per-block"]

        total_group1_blocks = group_1_blocks * group_1_codewords
        group_1 = [codewords[group_1_codewords * b : group_1_codewords * (b + 1)] for b in range(group_1_blocks)]
        group_2 = [codewords[total_group1_blocks + group_2_codewords * b : total_group1_blocks + group_2_codewords * (b + 1)] for b in range(group_2_blocks)]
        groups = [group_1, group_2]

        self.gen_polynomial = [gf(1), gf(1)] # (x + a0)


        for i in range(1, num_ecc_codewords):
            self.gen_polynomial = multiplyPolynomial(self.gen_polynomial, [gf(1), gf(gf.exponentiation_table[i])])

        qr_err = []
        for group in groups:
            for block in group:
                message_polynomial = [gf(int(x, 2)) for x in block]
                codes = generateECC(message_polynomial, self.gen_polynomial, num_ecc_codewords)
                qr_err.append(codes)
        
        # Interleave data codewords from each block
        interleaved_message = [] 

        for col in zip_longest(*(group_1 + group_2)):
            for x in [int(a, 2) for a in col if type(a) == str]:
                interleaved_message.append(x)
        #print(interleaved_message)
        interleaved_error = [int(x) for x in chain(*zip_longest(*qr_err)) if x is not None]
        interleaved_data = [format(i, "08b") for i in (interleaved_message + interleaved_error)]
        interleaved_data += "0" * remainder_bits[self.version]



        module_width = 17 + (self.version * 4)
        qr_code = [['*' for i in range(module_width)] for j in range(module_width)]

        # Place finder patterns

        insert_finder(qr_code, 0, 0)
        line_h(qr_code, 7, 0, 8, "0")
        line_v(qr_code, 0, 7, 7, "0")

         
        insert_finder(qr_code, (((self.version- 1 ) * 4) + 21) - 7, 0)
        line_h(qr_code, (((self.version- 1 ) * 4) + 21) - 8, 0, 8, "0")
        line_v(qr_code, (((self.version- 1 ) * 4) + 21) - 7, 7, 7, "0")

        insert_finder(qr_code, 0, (((self.version- 1 ) * 4) + 21) - 7)
        line_h(qr_code, 7, (((self.version- 1 ) * 4) + 21) - 8, 8, "0")
        line_v(qr_code, 0, (((self.version- 1 ) * 4) + 21) - 8, 7, "0")

        # Separators


        if self.version >= 2:
            pattern = alignment_patterns[self.version]
            print(list(product(pattern, pattern)))
            for position in list(product(pattern, pattern)):
                overlap = False
                for i in range(5):
                    for j in range(5):
                        # position[1] for y and position[0] for x
                        if qr_code[position[1] + i - 2][position[0] + j - 2] != "*":
                            overlap = True
                        #print(qr_code[position[0] + i - 2][position[1] + j - 2], end= ' ')
                    #print()
                if not overlap:
                    print(position[0], position[1])
                    square(qr_code, position[0] - 2, position[1] - 2, 5, "1")
                    square(qr_code, position[0] - 1, position[1] - 1, 3, "0")
                    square(qr_code, position[0], position[1], 1, "1")
                #print()

        for row in qr_code:
            for c in row:
                if c == "1":
                    print(colorama.Fore.GREEN + c, end='')
                elif c == "0":
                    print(colorama.Fore.WHITE + c, end='')
                else:
                    print("*", end="")
                print(colorama.Fore.RESET + ' ', end='')
            print()
        #print(''.join(interleaved_data))
        #print(remainder_bits[5])


#qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO WORLD")

qr = QRCode(QREncoding.ALPHA, "Q", 15, "HELLO WORLD")