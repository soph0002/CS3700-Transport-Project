from struct import Struct

MTU = 1500
MAX_DATA_SIZE = 1500 - 20 - 8

class Packet:
    """A TCP packet with struct packing"""
    # TODO: handle corrupt packets

    # ! - use network endianness (big-endian)
    # I - sequence number (32-bit unsigned integer)
    # B - flags (8-bit integer)
    #       - 1st bit --> ACK flag
    #       - 2nd bit --> EOF flag
    struct = Struct("! I B s")

    def __init__(self, sequence, ack=False, eof=False, data=""):
        self.sequence = sequence
        self.ack = ack
        self.eof = eof
        self.data = data

    def __str__(self):
        if self.ack:
            return "ACK packet (sequence: %d)" % self.sequence
        else:
            return "Data packet (sequence: %d, eof: %s, data: %d bytes)" % (
                self.sequence, self.eof, len(self.data))

    def __repr__(self):
        if self.ack:
            return "ACK(%d)" % self.sequence
        else:
            return "Data(%d, eof=%s, data=[...] (%d bytes))" % (
                self.sequence, self.eof, len(self.data))

    @property
    def flags(self):
        return 1 * self.ack + 2 * self.eof

    @property
    def packed(self):
        # TODO: determine best way to pack/unpack/represent flags
        return self.struct.pack(self.sequence, self.flags, self.data)

    @classmethod
    def from_packed(cls, raw):
        sequence, flags, data = cls.struct.unpack(raw)
        ack, eof = flags & 1, flags & 2
        return cls(sequence, ack=ack, eof=eof, data=data)

def ACKPacket(sequence):
    return Packet(sequence, ack=True)

def DataPacket(sequence, eof=False, data=""):
    return Packet(sequence, eof=eof, data=data)


def test_packet(pkt):
    from binascii import hexlify

    name = "ACK" if pkt.ack else "Data"

    print("\n== Testing %s packet packing/unpacking ==\n" % name)
    print("%s packet: %s" % (name, pkt))

    pkt_packed = pkt.packed
    print("%s packet (packed): %s" % (name, hexlify(pkt_packed)))

    pkt_unpacked = Packet.from_packed(pkt_packed)
    print("%s packet (unpacked): %s" % (name, pkt_unpacked))

    if pkt_unpacked.sequence == pkt.sequence:
        print("%s successfully encoded and decoded" % pkt)
    else:
        print("%s encoding/decoding failed; got %s" % (pkt, pkt_unpacked))

def test_ack(sequence):
    test_packet(ACKPacket(sequence))

def test_data(sequence, eof=False, data=""):
    test_packet(DataPacket(sequence, eof=eof, data=data))

if __name__ == "__main__":
    test_ack(50)
    test_data(100, eof=False, data="base test")
    test_data(100, eof=True, data="endoffile test")
