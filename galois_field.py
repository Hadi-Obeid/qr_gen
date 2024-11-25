import csv

int_to_alpha = {}
alpha_to_int = {}

with open('log_antilog.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        int_to_alpha[int(row["int"])] = int(row["alpha"])
        alpha_to_int[int(row["alpha"])] = int(row["int"])


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
    


print(int_to_alpha[1])