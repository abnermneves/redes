import socket as skt

HOST = '127.0.0.1'
PORT = 51511
BUFSZ = 1024

# skt.AF_INET é para IPv4. ver como faz para aceitar também IPv6
with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
  s.bind((HOST, PORT)) # associa o socket com o endereço e a porta
  s.listen() # espera a conexão de algum cliente

  # aceita uma conexão e retorna um objeto de conexão e um endereço
  # conn é um objeto socket distinto do listening socket
  conn, addr = s.accept()

  with conn:
    print(f'Connected by {addr}')
  
    while True:
      data = conn.recv(BUFSZ)
      if not data:
        break
      conn.sendall(data)