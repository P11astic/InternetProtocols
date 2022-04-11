import argparse
import socket
import time
import struct

TIME = 0

parser = argparse.ArgumentParser(description='SNTP server which "lies" for N seconds', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--real-time', action='store_true', dest='real', help='additionally shows real time', default=False)
parser.add_argument('-s', '--shift', action='store_true', dest='show', help='additionally shows selected shift', default=False)
args = parser.parse_args()


class Packet:
    _FORMAT = '!B B b b 11I'
    def __init__(self, version = 3, mode = 3, tx_timestamp = 0):
        self.leap = 0
        self.version = version
        self.mode = mode
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = 0
        self.ref_timestamp = 0
        self.orig_timestamp = 0
        self.recv_timestamp = 0
        self.tx_timestamp = tx_timestamp

    def pack(self):
        return struct.pack(Packet._FORMAT,
                (self.leap << 6) + 
                    (self.version << 3) + self.mode,
                self.stratum,
                self.poll,
                self.precision,
                int(self.root_delay),
                int(self.root_dispersion) ,
                self.ref_id,
                int(self.ref_timestamp),0,
                int(self.orig_timestamp),0,
                int(self.recv_timestamp),0,
                int(self.tx_timestamp),0)


def get_shift():
    try:
        with(open('config.txt')) as config:
            global TIME
            time_now = time.time()
            shift = int(config.readline())
            TIME = time_now + shift
            int_part, frac_part = [int(x) for x in str(time_now + shift).split('.')]
            if args.show:
                print(f'Shift is {shift} seconds')
            if args.real:
                print(f'Real time is: {time.ctime(time_now)}')
            return (int_part, frac_part)
    except Exception as e:
        print(f'Caught exception: {e}')
        

def main(host, port):
    global TIME
    sock = socket.socket()
    sock.settimeout(5)
    sock.bind(('', port))
    sock.listen(1)
    s, address = sock.accept()
    while True:
        data = s.recv(1024)
        if not data:
            break
        s.send(make_packet(unpack(data)))
        print(f'According to this server time is: {time.ctime(TIME)}')
    sock.close()



def make_packet(received: Packet):
    int_part, frac_part = get_shift()
    #according to SNTP, server corrcts only REFERENCE field
    packet = struct.pack(Packet._FORMAT,
                (received.leap << 6 | received.version << 3 | received.mode),0,0,0,0,0,0,
                int_part,
                frac_part,0,0,0,0,0,0)
    return packet

def unpack(data):
    unpacked = struct.unpack(Packet._FORMAT, data)
    res = Packet()
    res.leap = unpacked[0] >> 6  # 2 bits
    res.version = unpacked[0] >> 3 & 0b111  # 3 bits
    res.mode = unpacked[0] & 0b111  # 3 bits

    res.stratum = unpacked[1]  # 1 byte
    res.poll = unpacked[2]  # 1 byte
    res.precision = unpacked[3]  # 1 byte

    # 2 bytes | 2 bytes
    res.root_delay = (unpacked[4] >> 16) + \
        (unpacked[4] & 0xFFFF) / 2 ** 16
        # 2 bytes | 2 bytes
    res.root_dispersion = (unpacked[5] >> 16) + \
        (unpacked[5] & 0xFFFF) / 2 ** 16 

    # 4 bytes
    res.ref_id = str((unpacked[6] >> 24) & 0xFF) + " " + \
                    str((unpacked[6] >> 16) & 0xFF) + " " +  \
                    str((unpacked[6] >> 8) & 0xFF) + " " +  \
                    str(unpacked[6] & 0xFF)

    res.ref_timestamp = unpacked[7] + unpacked[8] / 2 ** 32  # 8 bytes
    res.orig_timestamp = unpacked[9] + unpacked[10] / 2 ** 32  # 8 bytes
    res.recv_timestamp = unpacked[11] + unpacked[12] / 2 ** 32  # 8 bytes
    res.tx_timestamp = unpacked[13] + unpacked[14] / 2 ** 32  # 8 bytes

    return res

if __name__=='__main__':
    main('127.0.0.1', 123)