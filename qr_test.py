import pytest
from qr import *

# TESTS
def test_bit_length_simple():
    foo = QRCode()
    assert foo.char_count_bits == 9

    foo = QRCode(QREncoding.ALPHA, "Q", 10)
    assert foo.char_count_bits == 11

    foo = QRCode(QREncoding.ALPHA, "Q", 11)
    assert foo.char_count_bits == 11

    foo = QRCode(QREncoding.ALPHA, "Q", 27)
    assert foo.char_count_bits == 13

    foo = QRCode(QREncoding.ALPHA, "Q", 28)
    assert foo.char_count_bits == 13

    foo = QRCode(QREncoding.ALPHA, "Q", 40)
    assert foo.char_count_bits == 13

def test_invalid_versions():
    with pytest.raises(ValueError):
        QRCode(QREncoding.ALPHA, "Q", 50)
        QRCode(QREncoding.ALPHA, "Q", -1)

def test_bit_length_numeric():
    foo = QRCode(QREncoding.NUMERIC, "Q", 10)
    assert foo.char_count_bits == 12

    foo = QRCode(QREncoding.NUMERIC, "Q", 27)
    assert foo.char_count_bits == 14

    foo = QRCode(QREncoding.NUMERIC, "Q", 40)
    assert foo.char_count_bits == 14

def test_bit_length_byte():
    foo = QRCode(QREncoding.BYTE, "Q", 1)
    assert foo.char_count_bits == 8

    foo = QRCode(QREncoding.BYTE, "Q", 10)
    assert foo.char_count_bits == 16

    foo = QRCode(QREncoding.BYTE, "Q", 27)
    assert foo.char_count_bits == 16

    foo = QRCode(QREncoding.BYTE, "Q", 40)
    assert foo.char_count_bits == 16


def test_encoding():
    # Checking every value in the coding table is correct
    for key in alphanumeric.keys():
        assert alphanumeric[key] == [*"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"].index(key)

def test_char_capacity():
    assert char_capacity[(40, "L", QREncoding.BYTE)] == 2953
    assert char_capacity[(8, "L", QREncoding.BYTE)] == 192
    assert char_capacity[(20, "L", QREncoding.ALPHA)] == 1249
    assert char_capacity[(20, "M", QREncoding.ALPHA)] == 970

def test_hello():
    qr = QRCode(QREncoding.ALPHA, "Q", 1, "HELLO WORLD")
    # Hello world example from the thonky site
    assert qr.data == "00100000010110110000101101111000110100010111001011011100010011010100001101000000111011000001000111101100"

def test_message():
    # Generator polynomials from thonky site
    qr = QRCode(QREncoding.ALPHA, "M", 1, "HELLO WORLD")
    gen_poly_10 = [0, 251, 67, 46, 61, 118, 70, 64, 94, 32, 45]
    assert [gf.logarithm_table[int(i) - 1] for i in qr.gen_polynomial] == gen_poly_10

    qr = QRCode(QREncoding.ALPHA, "H", 40, "GOODBYE WORLD")
    gen_poly_30 = [0, 41, 173, 145, 152, 216, 31, 179, 182, 50, 48, 110, 86, 239, 96, 222, 125, 42, 173, 226, 193, 224, 130, 156, 37, 251, 216, 238, 40, 192, 180]
    assert [gf.logarithm_table[int(i)-1] for i in qr.gen_polynomial] == gen_poly_30

def test_format_code():
    assert set_format_code("H", 7) == '000100000111011'
    assert set_format_code("M", 0) == '101010000010010'
    assert set_format_code("L", 4) == '110011000101111'
    assert set_format_code("Q", 2) == '011111100110001'

    assert version_information(7) == "000111110010010100"
    assert version_information(25) == "011001000111100001"
    assert version_information(40) == "101000110001101001"