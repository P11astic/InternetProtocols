import socket
import pickle
from time import time

cache = {}
yandex_dns = ('77.88.8.8',53)
local_dns = ('127.0.0.1', 53)
free_port = ('', 0)
cache_filename = 'cache'

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(local_dns)
asker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
asker.bind(free_port)

def parse_req(request: bytes):
    return request[12:]

def read_name(data, index):
    pos = index
    ch = data[pos]
    while ch != 0:
        if ch < 192:
            for i in range(ch):
                pos += 1
            pos += 1
        else:
            pos += 2
        ch = data[pos]
    return pos

def parse_answer(data, index):
    idx = read_name(data, index)
    ttl = data[idx+4: idx+8]
    return ttl, idx + 16
    
def find_ttl(answer):
    ttls = []
    current_byte = 12
    for i in range(int.from_bytes(answer[4:6], byteorder='big')):
        index = read_name(answer, current_byte)
        current_byte = index+5
    for i in range(int.from_bytes(answer[6:8], byteorder='big')):
        a = parse_answer(answer, current_byte)
        ttls.append(a[0])
        current_byte = a[1]
    for i in range(int.from_bytes(answer[8:10], byteorder='big')):
        a = parse_answer(answer, current_byte)
        ttls.append(a[0])
        current_byte = a[1]
    for i in range(int.from_bytes(answer[10:12], byteorder='big')):
        a = parse_answer(answer, current_byte)
        ttls.append(a[0])
        current_byte = a[1]
    return max(ttls)

def update_cache(req: bytes, ans: bytes):
    request = parse_req(req)
    ttl = int.from_bytes(find_ttl(ans), byteorder='big') + time()
    cache.update({request: (ans, ttl)})

def make_cahe_ans(asked: bytes, request: bytes):
    new_id = asked[0:2]
    answer = new_id + cache[request][0][2:]
    return answer

def resolve(data: bytes):
    request = parse_req(data)
    if request in cache:
        received = make_cahe_ans(data, request)
        return received
    asker.sendto(data, yandex_dns)
    received, adrs = asker.recvfrom(512)
    update_cache(data, received)
    return received

def check_cache():
    global cache
    new_cache = {}
    for key, rec in cache.items():
        if time() <= cache[key][1]:
            new_cache[key] = rec
    cache = new_cache

def save_cache():
    with open(cache_filename, 'wb') as c:
            pickle.dump(cache, c)

def load_cache():
    with open(cache_filename, 'rb') as c:
        try:
            return pickle.dump(c)
        except Exception:
            return {}

def start():
    while True:
        data, client = server.recvfrom(512)
        check_cache()
        res = resolve(data)
        server.sendto(res, client)

if __name__=='__main__':
    try:
        start()
    except KeyboardInterrupt:
        save_cache()
        pass
