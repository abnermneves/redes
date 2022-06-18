import socket as skt
import sys
import pdb

# definir como parametro na execução
IP = sys.argv[1]
PORT = int(sys.argv[2])
IPv = sys.argv[3]
# HOSTv4 = '127.0.0.1'
# HOSTv6 = '::1'
# PORT = 51511
BUFSZ = 512 # tamanho da mensagem a receber do servidor

def main():
  with skt.socket(skt.AF_INET if IPv == 'v4' else skt.AF_INET6, skt.SOCK_STREAM) as s:
    s.connect((IP, PORT))
    msg = input()

    while (msg != 'kill'):
      b_msg = str.encode(msg)
      s.sendall(b_msg)
      response = s.recv(BUFSZ)
      
      if response.decode() == 'invalid command':
        break

      print(f'{response.decode()}')
      msg = input()

if __name__ == '__main__':
  main()