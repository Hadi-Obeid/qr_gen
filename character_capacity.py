from enum import Enum
import csv


class QREncoding(Enum):
    # Values correspond to QR mode indicators in binary
    # e.g
    NUMERIC = 0b0001
    ALPHA = 0b0010
    BYTE = 0b0100
    KANJI = 0b1000
    #ECI = 0b0111

char_capacity = {}
with open('character_capacity.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for name, member in QREncoding.__members__.items():
            char_capacity[(int(row["Version"]), row["Error Correction Level"], member)] = int(row[name])

error_correction = {}
with open('error_correction_table.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        version, error_level = tuple(row["Version and EC Level"].split('-'))
        

if __name__ == '__main__':
    for key in char_capacity.keys():
        break
        #print(char_capacity[key])
