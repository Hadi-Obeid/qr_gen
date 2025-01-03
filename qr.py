from character_capacity import *
#from galois_field import *
from gf256 import GF256LT as gf
from PIL import Image, ImageDraw
import colorama
import random

from itertools import zip_longest, chain, product
import copy

# For the png image
QR_MODULE_WIDTH = 10

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

ec_format_bits = {"L": "01", "M": "00", "Q": "11", "H": "10"}

def set_format_code(quality, mask):
    format_str = ec_format_bits[quality] + format(mask, "03b")
    gen_polynomial = "10100110111"

    format_str += "0" * (15 - len(format_str))
    if format_str[0] == "0":
        format_str = format_str[1::]

    while len(format_str) >= 11:

        gen_padded = gen_polynomial + ("0" * (len(format_str) - len(gen_polynomial)))
        factor = format(int(format_str, 2) ^ int(gen_padded, 2) , f"0{len(format_str)}b")
        format_str = factor
        if format_str[0] == "0":
            format_str = format_str[1::]

    format_str = ("0" * clamp(0, 20, (10 - len(format_str)))) + format_str
    format_str = ec_format_bits[quality] + format(mask, "03b") + format_str
    final = format(int(format_str, 2) ^ int('101010000010010', 2) , f"015b")
    return final

def version_information(version):
    format_str = format(version, "06b")
    gen_polynomial = "1111100100101"

    format_str += "0" * (18 - len(format_str))
    while format_str[0] == "0":
        format_str = format_str[1::]


    while len(format_str) > 12:

        gen_padded = gen_polynomial + ("0" * (len(format_str) - len(gen_polynomial)))
        factor = format(int(format_str, 2) ^ int(gen_padded, 2) , f"0{len(format_str)}b")
        format_str = factor
        while format_str[0] == "0":
            format_str = format_str[1::]

    format_str = ("0" * clamp(0, 20, (12 - len(format_str)))) + format_str
    format_str = format(version, "06b") + format_str
    return format_str

def eval_row(row):
    streak = {"0": [], "1": []}
    count_ones = 0
    count_zeros = 0
    for bit in row:
        if bit == "1":
            streak["0"].append(count_zeros)
            count_zeros = 0

            count_ones += 1
        elif bit == "0":
            streak["1"].append(count_ones)
            count_ones = 0

            count_zeros += 1
    streak["0"].append(count_zeros)
    streak["1"].append(count_ones)
    return sum([i for i in map(lambda x: 3 + (x - 5) if x >= 5 else 0, (streak["0"] + streak["1"]))])

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
        elif self.encoding == QREncoding.BYTE:
            self.data += format(len(message), f"0{self.char_count_bits}b")
            self.data += ''.join([format(i, "08b") for i in message.encode(encoding='iso-8859-1')])
        
        #return
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

         
        insert_finder(qr_code, module_width - 7, 0)
        line_h(qr_code, module_width - 8, 0, 8, "0")
        line_v(qr_code, module_width - 7, 7, 7, "0")

        insert_finder(qr_code, 0, module_width - 7)
        line_h(qr_code, 7, module_width - 8, 8, "0")
        line_v(qr_code, 0, module_width - 8, 7, "0")

        # Separators


        if self.version >= 2:
            pattern = alignment_patterns[self.version]
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
                    square(qr_code, position[0] - 2, position[1] - 2, 5, "1")
                    square(qr_code, position[0] - 1, position[1] - 1, 3, "0")
                    square(qr_code, position[0], position[1], 1, "1")
                #print()
        
        # Reserved areas
        line_h(qr_code, 8, 0, 9, "2")
        line_v(qr_code, 0, 8, 8, "2")

        line_v(qr_code, module_width - 7, 8, 7, "2")

        line_h(qr_code, 8, module_width - 8, 8, "2")

        # Dark spot on bottom left finder
        qr_code[module_width - 8][8] = "1"

        # Timing pattern
        for y in range(8, module_width - 8):
            if y % 2 == 0:
                qr_code[y][6] = "1" # 1
            else:
                qr_code[y][6] = "0" # 0

        for x in range(8, module_width - 8):
            if x % 2 == 0:
                qr_code[6][x] = "1" # 1
            else:
                qr_code[6][x] = "0" # 0

        # Reserved version info area for version >= 7
        if self.version >= 7:
            version_info = version_information(self.version)[::-1]
            offset = module_width - 11
            for i in range(0, 6):
                for j in range(3):
                    qr_code[j + offset][i] = version_info[j + (i*3)]
                    qr_code[i][j + offset] = version_info[j + (i*3)]

        #print(interleaved_data)

        #data_up = True
        data_i = 0
        data_y = module_width - 1
        data_x = module_width - 1
        data_up = True


        data = ''.join(interleaved_data)
        mask = {}

        while True:
            if data_x == 6:
                data_x = 5
                data_y = 9
                data_up = False

            if data_i >= len(data):
                break

            bit = data[data_i]
            if qr_code[data_y][data_x] == "*":
                qr_code[data_y][data_x] = bit
                mask[(data_y, data_x)] = True
                data_i += 1

            if data_up:
                if data_x > 6:
                    if data_x % 2 == 0:
                        data_x -= 1
                    else:
                        data_x += 1
                        data_y -= 1
                else:
                    if data_x % 2 == 0:
                        data_x += 1
                        data_y -= 1
                    else:
                        data_x -= 1


                if data_y <= -1:
                    data_y += 1
                    data_x -= 2
                    data_up = False

            else:
                if data_x > 6:
                    if data_x % 2 == 0:
                        data_x -= 1
                    else:
                        data_x += 1
                        data_y += 1
                else:
                    if data_x % 2 == 0:
                        data_x += 1
                        data_y += 1
                    else:
                        data_x -= 1

                if data_y >= module_width:
                    data_y -= 1
                    data_x -= 2
                    data_up = True


        penalties = {}
        for mask_pattern in range(6):
            format_code = set_format_code(self.quality, mask_pattern)
            code = copy.deepcopy(qr_code)
            for i in range(6):
                code[8][i] = format_code[i]
                code[i][8] = format_code[len(format_code) - 1 - i]
            for i in range(6,8):
                code[8][i+1] = format_code[i]

            for i in range(8):
                code[8][module_width - 8 + i] = format_code[7 + i]
            
            for i in range(7):
                code[module_width - 1 - i][8] = format_code[i]
            code[7][8] = format_code[8]
            
            #line_h(qr_code, 8, 0, 9, "2")
            for e in mask:
                row = e[0]
                col = e[1]
                bit = code[row][col]
                flip = "1" if bit == "0" else "0"
                # Match 6
                match mask_pattern:
                    case 0:
                        if ((row + col) % 2) == 0:
                            code[e[0]][e[1]] = flip
                    case 1:
                        if (row % 2) == 0:
                            code[e[0]][e[1]] = flip
                    case 2:
                        if (col % 3) == 0:
                            code[e[0]][e[1]] = flip
                    case 3:
                        if ((row + col) % 3) == 0:
                            code[e[0]][e[1]] = flip
                    case 4:
                        if (((row // 2) + (col // 3)) % 2) == 0:
                            code[e[0]][e[1]] = flip
                    case 5:
                        if ( ((row * col) % 2) + ((row * col) % 3)) == 0:
                            code[e[0]][e[1]] = flip
                    case 6:
                        if ((((row * col) % 2) + (((row * col) % 3))) % 2 == 0):
                            code[e[0]][e[1]] = flip
                    case 7:
                        if ((((row + col) % 2) + ((row * col) % 3)) % 2) == 0: 
                            code[e[0]][e[1]] = flip
                

            # Evaluate the code
            code_rotated = [[code[y][x] for y in range(module_width)] for x in range(module_width)]

            # Condition 1
            penalty_1 = sum([eval_row(row) for row in code_rotated]) + sum([eval_row(row) for row in code])

            # Condition 2
            penalty_2 = 0
            for y in range(0, module_width - 1):
                for x in range(0, module_width -1):
                    data_square = code[y][x] + code[y+1][x] + code[y][x+1] + code[y+1][x+1]
                    if data_square == "0000" or data_square == "1111":
                        penalty_2 += 3

            # Condition 3
            penalty_3 = 0
            # Count for specific occurence of pattern
            for i in range(module_width):
                row = ''.join(code[i])
                row_r = ''.join(code_rotated[i])
                penalty_3 += (row_r.count('10111010000') + row.count('10111010000')) * 40
                penalty_3 += (row_r.count('00001011101') + row.count('00001011101')) * 40

            total_modules = module_width * module_width
            total_black = sum([''.join(row).count("1") for row in qr_code])
            percent = round((total_black / total_modules) * 100.)
            # Previous and next multiples of 5 using floor division and modulo
            previous_5 = 5 * (percent // 5)
            next_5 = previous_5 + 5
            penalty_4 = 10 * min(abs(50 - previous_5) // 5, abs(50 - next_5) // 5)
            penalty_score = penalty_1 + penalty_2 + penalty_3 + penalty_4
            penalties[penalty_score] = code
        self.qr_code = penalties[min(penalties.keys())]

    def print_code(self):
        print(colorama.Back.WHITE + '\n' * 10)
        for row in self.qr_code:
            print('\t' * 5, end='')
            for c in row:
                if c == "1":
                    print(colorama.Back.BLACK + ' ' * 2, end='')
                elif c == "0":
                    print(colorama.Back.WHITE + ' ' * 2, end='')
                elif c == "2":
                    print(colorama.Back.BLUE + ' ' * 2, end='')
                else:
                    print(colorama.Back.RED + c , end="")
                print(colorama.Back.WHITE + '', end='')
            print()
        '    '
        print(colorama.Back.WHITE + '\n\n\n\n')
        print(colorama.Back.RESET + '\n\n\n\n')
        #print(''.join(interleaved_data))
        #print(remainder_bits[5])

 
#qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO WORLD")


q = QRCode(QREncoding.BYTE, "Q", 40, "hello")
"""
if __name__ == `__main__`:
    version = 10
    qr = QRCode(QREncoding.BYTE, "L", version, "https://www.youtube.com/watch?v=hkGdXFHX8Wg")

    qr_img = Image.new("L", (QR_MODULE_WIDTH * (25 + (version * 4)), QR_MODULE_WIDTH * (25 + (version * 4))), color = 255)
    img_writer = ImageDraw.Draw(qr_img)
    code = qr.qr_code
    for y, row in enumerate(code):
        for x, bit in enumerate(row):
            y_pos = (y + 4) * QR_MODULE_WIDTH
            x_pos = (x + 4) * QR_MODULE_WIDTH
            color = 255 if bit == "0" else 0
            img_writer.rectangle([(x_pos, y_pos), (x_pos + QR_MODULE_WIDTH, y_pos + QR_MODULE_WIDTH)], fill = color)
    qr_img.show()
"""