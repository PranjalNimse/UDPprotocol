
class Segment:
    def __init__(self, seg_type, win_size, sequence, length, payload):
        self.seg_type = seg_type
        self.win_size = win_size
        self.sequence = sequence
        self.length = length
        self.payload = payload

# Creates a segment from a sequence number and byte data
def create_seg(seq_num, data = b''):
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    return seq_bytes + data

def create_empty_seg():
    return b''

# Extracts sequence number and data from a segment
def disintegrate_seg(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    return seq_num, packet[4:]
