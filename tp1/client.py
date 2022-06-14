import socket as skt

HOST = '127.0.0.1'
PORT = 51511
BUFSZ = 1024

with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  s.sendall(b'hey girl hey')
  data = s.recv(BUFSZ)

print(f'Received {data!r}')
