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


def test_gf_basic():
    a = GF(1)
    b = GF(2)
    c = GF(2)
    assert a == GF(1)
    assert a != b
    assert b == c

def test_gf_add():
    a = GF(1)
    b = GF(1)
    assert a + b == GF(0)
    assert GF(0) + GF(1) == GF(1)
