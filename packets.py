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
    struct = Struct("! I B")

    def __init__(self, sequence, ack=False, eof=False, fin=False, data=""):
        self.sequence = sequence
        self.ack = ack
        self.eof = eof
        self.fin = fin
        self.data = data

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Packet(%d, ack=%s, eof=%s, fin=%s, data='%s')" % (
            self.sequence, self.ack, self.eof, self.fin, self.data)

    @property
    def flags(self):
        return 1 * self.ack + 2 * self.eof + 4 * self.fin

    @property
    def packed(self):
        # TODO: determine best way to pack/unpack/represent flags
        return self.struct.pack(self.sequence, self.flags) + self.data

    @classmethod
    def from_packed(cls, raw):
        (sequence, flags), data = cls.struct.unpack(raw[:5]), raw[5:]
        ack, eof, fin = bool(flags & 1), bool(flags & 2), bool(flags & 4)
        return cls(sequence, ack=ack, eof=eof, fin=fin, data=data)

def AckPacket(sequence):
    return Packet(sequence, ack=True)

def FinPacket(sequence):
    return Packet(sequence, fin=True)

def FinAckPacket(sequence):
    return Packet(sequence, ack=True, fin=True)

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

    if pkt_unpacked.sequence == pkt.sequence and \
        pkt_unpacked.ack == pkt.ack and \
        pkt_unpacked.eof == pkt.eof and \
        pkt_unpacked.data == pkt.data:
        # pkt_unpacked.fin == pkt.fin and
        print("%s successfully encoded and decoded" % pkt)
    else:
        print("%s encoding/decoding failed; got %s" % (pkt, pkt_unpacked))

if __name__ == "__main__":
    test_packet(AckPacket(1234))
    test_packet(FinPacket(1234))
    test_packet(FinAckPacket(1234))
    test_packet(DataPacket(1234, eof=False, data="base test"))
    test_packet(DataPacket(1234, eof=True, data="endoffile test"))
