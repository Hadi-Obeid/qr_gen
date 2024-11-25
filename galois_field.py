import csv

int_to_alpha = {}
alpha_to_int = {}

with open('log.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_int = int(row["int"])
        row_alpha = int(row["alpha"])
        alpha_to_int[row_alpha] = row_int
        int_to_alpha[row_int] = row_alpha


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
    

print(alpha_to_int[255])
