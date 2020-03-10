#!/usr/bin/env python
# coding: utf-8
#
# Explode library for PKWARE compression library
# based on Ladislav Zezula's StormLib explode.c @ 2003
# ported to Python by O. Kutal @ 2020
#

CMP_BINARY = 0  # Binary compression
CMP_ASCII = 1   # Ascii compression

CMP_NO_ERROR = 0
CMP_INVALID_DICTSIZE = 1
CMP_INVALID_MODE = 2
CMP_BAD_DATA = 3
CMP_ABORT = 4

CMP_IMPLODE_DICT_SIZE1 = 1024  # Dictionary size of 1024
CMP_IMPLODE_DICT_SIZE2 = 2048  # Dictionary size of 2048
CMP_IMPLODE_DICT_SIZE3 = 4096  # Dictionary size of 4096

PKDCL_OK = 0
PKDCL_STREAM_END = 1  # All data from the input stream is read
PKDCL_NEED_DICT = 2  # Need more data (dictionary)
PKDCL_CONTINUE = 10  # Internal flag, not returned to user
PKDCL_GET_INPUT = 11  # Internal flag, not returned to user

dist_bits = [
    0x02, 0x04, 0x04, 0x05, 0x05, 0x05, 0x05, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
    0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
    0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08
]

dist_code = [
    0x03, 0x0D, 0x05, 0x19, 0x09, 0x11, 0x01, 0x3E, 0x1E, 0x2E, 0x0E, 0x36, 0x16, 0x26, 0x06, 0x3A,
    0x1A, 0x2A, 0x0A, 0x32, 0x12, 0x22, 0x42, 0x02, 0x7C, 0x3C, 0x5C, 0x1C, 0x6C, 0x2C, 0x4C, 0x0C,
    0x74, 0x34, 0x54, 0x14, 0x64, 0x24, 0x44, 0x04, 0x78, 0x38, 0x58, 0x18, 0x68, 0x28, 0x48, 0x08,
    0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10, 0xE0, 0x60, 0xA0, 0x20, 0xC0, 0x40, 0x80, 0x00
]

ex_len_bits = [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08
]

len_base = [
    0x0000, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006, 0x0007,
    0x0008, 0x000A, 0x000E, 0x0016, 0x0026, 0x0046, 0x0086, 0x0106
]

len_bits = [
    0x03, 0x02, 0x03, 0x03, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x05, 0x06, 0x06, 0x06, 0x07, 0x07
]

len_code = [
    0x05, 0x03, 0x01, 0x06, 0x0A, 0x02, 0x0C, 0x14, 0x04, 0x18, 0x08, 0x30, 0x10, 0x20, 0x40, 0x00
]

ch_bits_asc = [
    0x0B, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x08, 0x07, 0x0C, 0x0C, 0x07, 0x0C, 0x0C,
    0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0D, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C,
    0x04, 0x0A, 0x08, 0x0C, 0x0A, 0x0C, 0x0A, 0x08, 0x07, 0x07, 0x08, 0x09, 0x07, 0x06, 0x07, 0x08,
    0x07, 0x06, 0x07, 0x07, 0x07, 0x07, 0x08, 0x07, 0x07, 0x08, 0x08, 0x0C, 0x0B, 0x07, 0x09, 0x0B,
    0x0C, 0x06, 0x07, 0x06, 0x06, 0x05, 0x07, 0x08, 0x08, 0x06, 0x0B, 0x09, 0x06, 0x07, 0x06, 0x06,
    0x07, 0x0B, 0x06, 0x06, 0x06, 0x07, 0x09, 0x08, 0x09, 0x09, 0x0B, 0x08, 0x0B, 0x09, 0x0C, 0x08,
    0x0C, 0x05, 0x06, 0x06, 0x06, 0x05, 0x06, 0x06, 0x06, 0x05, 0x0B, 0x07, 0x05, 0x06, 0x05, 0x05,
    0x06, 0x0A, 0x05, 0x05, 0x05, 0x05, 0x08, 0x07, 0x08, 0x08, 0x0A, 0x0B, 0x0B, 0x0C, 0x0C, 0x0C,
    0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D,
    0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D,
    0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D,
    0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C,
    0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C,
    0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C,
    0x0D, 0x0C, 0x0D, 0x0D, 0x0D, 0x0C, 0x0D, 0x0D, 0x0D, 0x0C, 0x0D, 0x0D, 0x0D, 0x0D, 0x0C, 0x0D,
    0x0D, 0x0D, 0x0C, 0x0C, 0x0C, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D, 0x0D
]

ch_code_asc = [
    0x0490, 0x0FE0, 0x07E0, 0x0BE0, 0x03E0, 0x0DE0, 0x05E0, 0x09E0,
    0x01E0, 0x00B8, 0x0062, 0x0EE0, 0x06E0, 0x0022, 0x0AE0, 0x02E0,
    0x0CE0, 0x04E0, 0x08E0, 0x00E0, 0x0F60, 0x0760, 0x0B60, 0x0360,
    0x0D60, 0x0560, 0x1240, 0x0960, 0x0160, 0x0E60, 0x0660, 0x0A60,
    0x000F, 0x0250, 0x0038, 0x0260, 0x0050, 0x0C60, 0x0390, 0x00D8,
    0x0042, 0x0002, 0x0058, 0x01B0, 0x007C, 0x0029, 0x003C, 0x0098,
    0x005C, 0x0009, 0x001C, 0x006C, 0x002C, 0x004C, 0x0018, 0x000C,
    0x0074, 0x00E8, 0x0068, 0x0460, 0x0090, 0x0034, 0x00B0, 0x0710,
    0x0860, 0x0031, 0x0054, 0x0011, 0x0021, 0x0017, 0x0014, 0x00A8,
    0x0028, 0x0001, 0x0310, 0x0130, 0x003E, 0x0064, 0x001E, 0x002E,
    0x0024, 0x0510, 0x000E, 0x0036, 0x0016, 0x0044, 0x0030, 0x00C8,
    0x01D0, 0x00D0, 0x0110, 0x0048, 0x0610, 0x0150, 0x0060, 0x0088,
    0x0FA0, 0x0007, 0x0026, 0x0006, 0x003A, 0x001B, 0x001A, 0x002A,
    0x000A, 0x000B, 0x0210, 0x0004, 0x0013, 0x0032, 0x0003, 0x001D,
    0x0012, 0x0190, 0x000D, 0x0015, 0x0005, 0x0019, 0x0008, 0x0078,
    0x00F0, 0x0070, 0x0290, 0x0410, 0x0010, 0x07A0, 0x0BA0, 0x03A0,
    0x0240, 0x1C40, 0x0C40, 0x1440, 0x0440, 0x1840, 0x0840, 0x1040,
    0x0040, 0x1F80, 0x0F80, 0x1780, 0x0780, 0x1B80, 0x0B80, 0x1380,
    0x0380, 0x1D80, 0x0D80, 0x1580, 0x0580, 0x1980, 0x0980, 0x1180,
    0x0180, 0x1E80, 0x0E80, 0x1680, 0x0680, 0x1A80, 0x0A80, 0x1280,
    0x0280, 0x1C80, 0x0C80, 0x1480, 0x0480, 0x1880, 0x0880, 0x1080,
    0x0080, 0x1F00, 0x0F00, 0x1700, 0x0700, 0x1B00, 0x0B00, 0x1300,
    0x0DA0, 0x05A0, 0x09A0, 0x01A0, 0x0EA0, 0x06A0, 0x0AA0, 0x02A0,
    0x0CA0, 0x04A0, 0x08A0, 0x00A0, 0x0F20, 0x0720, 0x0B20, 0x0320,
    0x0D20, 0x0520, 0x0920, 0x0120, 0x0E20, 0x0620, 0x0A20, 0x0220,
    0x0C20, 0x0420, 0x0820, 0x0020, 0x0FC0, 0x07C0, 0x0BC0, 0x03C0,
    0x0DC0, 0x05C0, 0x09C0, 0x01C0, 0x0EC0, 0x06C0, 0x0AC0, 0x02C0,
    0x0CC0, 0x04C0, 0x08C0, 0x00C0, 0x0F40, 0x0740, 0x0B40, 0x0340,
    0x0300, 0x0D40, 0x1D00, 0x0D00, 0x1500, 0x0540, 0x0500, 0x1900,
    0x0900, 0x0940, 0x1100, 0x0100, 0x1E00, 0x0E00, 0x0140, 0x1600,
    0x0600, 0x1A00, 0x0E40, 0x0640, 0x0A40, 0x0A00, 0x1200, 0x0200,
    0x1C00, 0x0C00, 0x1400, 0x0400, 0x1800, 0x0800, 0x1000, 0x0000
]


class TDcmpStruct:

    def __init__(self, input_buffer):
        self.offs0000 = 0  # 0000
        self.ctype = 0  # 0004: Compression type (CMP_BINARY or CMP_ASCII)
        self.output_pos = 0  # 0008: Position in output buffer
        self.dsize_bits = 0  # 000C: Dict size (4, 5, 6 for 0x400, 0x800, 0x1000)
        self.dsize_mask = 0  # 0010: Dict size bitmask (0x0F, 0x1F, 0x3F for 0x400, 0x800, 0x1000)
        self.bit_buff = 0  # 0014: 16-bit buffer for processing input data
        self.extra_bits = 0  # 0018: Number of extra (above 8) bits in bit buffer
        self.in_pos = 0  # 001C: Position in in_buff
        self.in_bytes = 0  # 0020: Number of bytes in input buffer
        self.out_buff = bytearray(0x2204)  # 0030: Output circle buffer.
        #        0x0000 - 0x0FFF: Previous uncompressed data, kept for repetitions
        #        0x1000 - 0x1FFF: Currently decompressed data
        #        0x2000 - 0x2203: Reserve space for the longest possible repetition
        self.in_buff = bytearray(0x800)  # 2234: Buffer for data to be decompressed
        self.dist_pos_codes = bytearray(0x100)  # 2A34: Table of distance position codes
        self.length_codes = bytearray(0x100)  # 2B34: Table of length codes
        self.offs2C34 = bytearray(0x100)  # 2C34: Buffer for
        self.offs2D34 = bytearray(0x100)  # 2D34: Buffer for
        self.offs2E34 = bytearray(0x80)  # 2EB4: Buffer for
        self.offs2EB4 = bytearray(0x100)  # 2EB4: Buffer for
        self.ch_bits_asc = bytearray(0x100)  # 2FB4: Buffer for
        self.dist_bits = bytearray(0x40)  # 30B4: Numbers of bytes to skip copied block length
        self.len_bits = bytearray(0x10)  # 30F4: Numbers of bits for skip copied block length
        self.ex_len_bits = bytearray(0x10)  # 3104: Number of valid bits for copied block
        self.len_base = [0] * 0x10  # 3114: Buffer for

        self.compressed = input_buffer  # 0024: Custom parameter
        self.compressed_offset = 0
        self.decompressed = bytearray()

    def read_buf(self, size):
        n_max_avail = (len(self.compressed) - self.compressed_offset) & 0xFFFFFFFF
        n_to_read = size

        # Check the case when not enough data available
        if n_to_read > n_max_avail:
            n_to_read = n_max_avail

        # Load data and increment offsets
        ret = self.compressed[self.compressed_offset:self.compressed_offset + n_to_read]
        self.compressed_offset += n_to_read
        assert (self.compressed_offset <= len(self.compressed))
        return ret

    def write_buf(self, buf):
        self.decompressed += buf


def gen_decode_tabs(positions, start_indexes, length_bits):
    assert (len(length_bits) == len(start_indexes))
    for i in range(len(length_bits)):
        length = 1 << length_bits[i]  # Get the length in bytes
        index = start_indexes[i]
        while index < 0x100:
            positions[index] = i & 0xFF
            index += length


def gen_asc_tabs(work):
    pch_code_asc_idx = 0xFF
    count = 0x00FF

    while pch_code_asc_idx >= 0:
        pch_bits_asc_idx = count
        bits_asc = work.ch_bits_asc[pch_bits_asc_idx]

        if bits_asc <= 8:
            add = (1 << bits_asc)
            acc = ch_code_asc[pch_code_asc_idx]

            while True:
                work.offs2C34[acc] = count & 0xFF
                acc += add
                if acc >= 0x100:
                    break

        else:
            acc = (ch_code_asc[pch_code_asc_idx] & 0xFF)
            if acc != 0:
                work.offs2C34[acc] = 0xFF

                if ch_code_asc[pch_code_asc_idx] & 0x3F:
                    bits_asc -= 4
                    work.ch_bits_asc[pch_bits_asc_idx] = bits_asc

                    add = (1 << bits_asc)
                    acc = ch_code_asc[pch_code_asc_idx] >> 4

                    while True:
                        work.offs2D34[acc] = count & 0xFF
                        acc += add
                        if acc >= 0x100:
                            break
                else:
                    bits_asc -= 6
                    work.ch_bits_asc[pch_bits_asc_idx] = bits_asc

                    add = (1 << bits_asc)
                    acc = ch_code_asc[pch_code_asc_idx]

                    while True:
                        work.offs2E34[acc] = count & 0xFF
                        acc += add
                        if acc >= 0x80:
                            break

            else:
                bits_asc -= 8
                work.ch_bits_asc[pch_bits_asc_idx] = bits_asc

                add = (1 << bits_asc)
                acc = ch_code_asc[pch_code_asc_idx] >> 8

                while True:
                    work.offs2EB4[acc] = count & 0xFF
                    acc += add
                    if acc >= 0x100:
                        break

        pch_code_asc_idx -= 1
        count -= 1


# -----------------------------------------------------------------------------
#  Removes given number of bits in the bit buffer. New bits are reloaded from
#  the input buffer, if needed.
#  Returns: PKDCL_OK:         Operation was successful
#           PKDCL_STREAM_END: There are no more bits in the input buffer
def waste_bits(work, n_bits):
    #  If number of bits required is less than number of (bits in the buffer) ?
    if n_bits <= work.extra_bits:
        work.extra_bits -= n_bits
        work.bit_buff >>= n_bits
        return PKDCL_OK

    #  Load input buffer if necessary
    work.bit_buff >>= work.extra_bits
    if work.in_pos == work.in_bytes:
        work.in_pos = len(work.in_buff)
        read_data = work.read_buf(work.in_pos)
        work.in_bytes = len(read_data)
        work.in_buff[:work.in_bytes] = read_data
        if work.in_bytes == 0:
            return PKDCL_STREAM_END
        work.in_pos = 0

    #  Update bit buffer
    work.in_pos += 1
    work.bit_buff |= (work.in_buff[work.in_pos - 1] << 8)
    work.bit_buff >>= (n_bits - work.extra_bits)
    work.extra_bits = (work.extra_bits - n_bits) + 8
    return PKDCL_OK


# -----------------------------------------------------------------------------
#  Decodes next literal from the input (compressed) data.
#  Returns : 0x000: One byte 0x00
#            0x001: One byte 0x01
#            ...
#            0x0FF: One byte 0xFF
#            0x100: Repetition, length of 0x02 bytes
#            0x101: Repetition, length of 0x03 bytes
#            ...
#            0x304: Repetition, length of 0x206 bytes
#            0x305: End of stream
#            0x306: Error
def decode_lit(work):
    #  Test the current bit in byte buffer. If is not set, simply return the next 8 bits.
    if work.bit_buff & 1 != 0:
        #  Remove one bit from the input data
        if waste_bits(work, 1):
            return 0x306

        #  The next 8 bits hold the index to the length code table
        length_code = work.length_codes[work.bit_buff & 0xFF]

        #  Remove the apropriate number of bits
        if waste_bits(work, work.len_bits[length_code]):
            return 0x306

        #  Are there some extra bits for the obtained length code ?
        extra_length_bits = work.ex_len_bits[length_code]
        if extra_length_bits != 0:
            extra_length = work.bit_buff & ((1 << extra_length_bits) - 1)

            if waste_bits(work, extra_length_bits):
                if (length_code + extra_length) != 0x10E:
                    return 0x306
            length_code = work.len_base[length_code] + extra_length

        #  In order to distinguish uncompressed byte from repetition length,
        #  we have to add 0x100 to the length.
        return length_code + 0x100

    #  Remove one bit from the input data
    if waste_bits(work, 1):
        return 0x306

    #  If the binary compression type, read 8 bits and return them as one byte.
    if work.ctype == CMP_BINARY:
        uncompressed_byte = work.bit_buff & 0xFF

        if waste_bits(work, 8):
            return 0x306
        return uncompressed_byte

    #  When ASCII compression ...
    if work.bit_buff & 0xFF:
        value = work.offs2C34[work.bit_buff & 0xFF]

        if value == 0xFF:
            if work.bit_buff & 0x3F != 0:
                if waste_bits(work, 4):
                    return 0x306

                value = work.offs2D34[work.bit_buff & 0xFF]
            else:
                if waste_bits(work, 6):
                    return 0x306

                value = work.offs2E34[work.bit_buff & 0x7F]
    else:
        if waste_bits(work, 8):
            return 0x306

        value = work.offs2EB4[work.bit_buff & 0xFF]

    return 0x306 if waste_bits(work, work.ch_bits_asc[value]) else value


# -----------------------------------------------------------------------------
#  Decodes the distance of the repetition, backwards relative to the
#  current output buffer position
def decode_dist(work, rep_length):
    #  Next 2-8 bits in the input buffer is the distance position code
    dist_pos_code = work.dist_pos_codes[work.bit_buff & 0xFF]
    dist_pos_bits = work.dist_bits[dist_pos_code]
    if waste_bits(work, dist_pos_bits):
        return 0

    if rep_length == 2:
        #  If the repetition is only 2 bytes length,
        #  then take 2 bits from the stream in order to get the distance
        distance = (dist_pos_code << 2) | (work.bit_buff & 0x03)
        if waste_bits(work, 2):
            return 0
    else:
        #  If the repetition is more than 2 bytes length,
        #  then take "dsize_bits" bits in order to get the distance
        distance = (dist_pos_code << work.dsize_bits) | (work.bit_buff & work.dsize_mask)
        if waste_bits(work, work.dsize_bits):
            return 0
    return distance + 1


def expand(work):
    work.output_pos = 0x1000  # Initialize output buffer position

    #  Decode the next literal from the input data.
    #  The returned literal can either be an uncompressed byte (next_literal < 0x100)
    #  or an encoded length of the repeating byte sequence that
    #  is to be copied to the current buffer position
    result = next_literal = decode_lit(work)

    while result < 0x305:
        #  If the literal is greater than 0x100, it holds length
        #  of repeating byte sequence
        #  literal of 0x100 means repeating sequence of 0x2 bytes
        #  literal of 0x101 means repeating sequence of 0x3 bytes
        #  ...
        #  literal of 0x305 means repeating sequence of 0x207 bytes
        if next_literal >= 0x100:
            #  Get the length of the repeating sequence.
            #  Note that the repeating block may overlap the current output position,
            #  for example if there was a sequence of equal bytes
            rep_length = next_literal - 0xFE

            #  Get backward distance to the repetition
            minus_dist = decode_dist(work, rep_length)
            if minus_dist == 0:
                result = 0x306
                break

            #  Target and source pointer
            target_offset = work.output_pos
            source_offset = work.output_pos - minus_dist

            #  Copy the repeating sequence
            work.out_buff[target_offset:target_offset + rep_length] = \
                work.out_buff[source_offset:source_offset + rep_length]

            #  Update buffer output position
            work.output_pos += rep_length

        else:
            work.output_pos += 1
            work.out_buff[work.output_pos - 1] = next_literal & 0xFF

        #  Flush the output buffer, if number of extracted bytes has reached the end
        if work.output_pos >= 0x2000:
            #  Copy decompressed data into user buffer
            copy_bytes = 0x1000
            work.write_buf(work.out_buff[0x1000:0x1000 + copy_bytes])

            #  Now copy the decompressed data to the first half of the buffer.
            #  This is needed because the decompression might reuse them as repetitions.
            #  Note that if the output buffer overflowed previously, the extra decompressed bytes
            #  are stored in "out_buff_overflow", and they will now be
            #  within decompressed part of the output buffer.
            target_offset = 0
            source_offset = 0x1000
            copy_length = work.output_pos - 0x1000

            work.out_buff[target_offset:target_offset + copy_length] = \
                work.out_buff[source_offset:source_offset + copy_length]

            work.output_pos -= 0x1000

        result = next_literal = decode_lit(work)

    #  Flush any remaining decompressed bytes
    copy_bytes = work.output_pos - 0x1000
    work.write_buf(work.out_buff[0x1000:0x1000 + copy_bytes])
    return result


# -----------------------------------------------------------------------------
#  Main exploding function.
def explode(input_buffer):
    work = TDcmpStruct(input_buffer)

    #  Initialize work struct and load compressed data
    #  Note: The caller must zero the "work_buff" before passing it to explode
    work.in_pos = len(work.in_buff)
    read_data = work.read_buf(work.in_pos)
    work.in_bytes = len(read_data)
    work.in_buff[:work.in_bytes] = read_data
    if work.in_bytes <= 4:
        raise Exception("CMP_BAD_DATA")

    work.ctype = work.in_buff[0]  # Get the compression type (CMP_BINARY or CMP_ASCII)
    work.dsize_bits = work.in_buff[1]  # Get the dictionary size
    work.bit_buff = work.in_buff[2]  # Initialize 16-bit bit buffer
    work.extra_bits = 0  # Extra (over 8) bits
    work.in_pos = 3  # Position in input buffer

    #  Test for the valid dictionary size
    if 4 > work.dsize_bits or work.dsize_bits > 6:
        raise Exception("CMP_INVALID_DICTSIZE")

    work.dsize_mask = 0xFFFF >> (0x10 - work.dsize_bits)  # Shifted by 'sar' instruction

    if work.ctype != CMP_BINARY:
        if work.ctype != CMP_ASCII:
            raise Exception("CMP_INVALID_MODE")

        work.ch_bits_asc[:len(work.ch_bits_asc)] = ch_bits_asc
        gen_asc_tabs(work)

    work.len_bits[:len(work.len_bits)] = len_bits
    gen_decode_tabs(work.length_codes, len_code, work.len_bits, )
    work.ex_len_bits[:len(work.ex_len_bits)] = ex_len_bits
    work.len_base[:len(work.len_base)] = len_base
    work.dist_bits[:len(work.dist_bits)] = dist_bits
    gen_decode_tabs(work.dist_pos_codes, dist_code, work.dist_bits)
    if expand(work) != 0x306:
        return work.decompressed

    raise Exception("CMP_ABORT")
