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
        error_correction[(int(version), error_level)] = {
            "total-codewords" : int(row["Total Number of Data Codewords for this Version and EC Level"]),
            "ec-codewords-per-block" : int(row["EC Codewords Per Block"]),
            "num-blocks-group-1" : int(row["Number of Blocks in Group 1"]),
            "num-codewords-group-1": int(row["Number of Data Codewords in Each of Group 1's Blocks"]),
            "num-blocks-group-2" : 0 if row["Number of Blocks in Group 2"] == '' else int(row["Number of Blocks in Group 2"]),
            "num-codewords-group-2" : 0 if row["Number of Data Codewords in Each of Group 2's Blocks"] == '' else int(row["Number of Data Codewords in Each of Group 2's Blocks"]),
            "total-codewords" : int(row["Total Data Codewords"]),

        }
        
def clamp(a, b, n):
    if n < a:
        return a
    if n > b:
        return b
    return n

if __name__ == '__main__':
    for key in error_correction.keys():
        pass
        #print(error_correction[key])
