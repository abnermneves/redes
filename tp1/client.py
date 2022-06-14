import socket as skt

HOST = '127.0.0.1'
PORT = 51511
BUFSZ = 512 # tamanho da mensagem a receber do servidor

with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
  s.connect((HOST, PORT))

  msg = input()

  while (msg != 'kill'):
    b_msg = str.encode(msg)
    s.sendall(b_msg)
    data = s.recv(BUFSZ)
    print(f'Received {data!r}')
    msg = input()
