import csv

int_to_alpha = {}
alpha_to_int = {}

i_alpha = {}
alpha_i = {}

v = 0b00000001
for i in range(0, 255):
    print(v, format(v, "8b"))
    i_alpha[i] = v
    alpha_i[v] = i
    v = v << 1
    if v > 255:
        v ^= 256
        v ^= 0b00011101


class GF():
    """
        GF256 (Galois finite field)
    """
    def __init__(self, val):
        self.val = val
    
    def __eq__(self, other):
        return self.val == other.val
    
    def __add__(self, other):
        return GF(self.val ^ other.val)