import socket as skt
import sys
import pdb

# ------------- constantes et cetera ------------- #
ADDR = sys.argv[1]
PORT = int(sys.argv[2])
IPv = ''
BUFSZ = 512 # tamanho da mensagem a receber do servidor

def main():
  # checa se o IP é v4 ou v6
  try:
    skt.inet_pton(skt.AF_INET6, ADDR)
    IPv = 'v6'
  except:
    try:
      skt.inet_aton(ADDR)
      IPv = 'v4'
    except:
      print('endereço inválido')
      return

  with skt.socket(skt.AF_INET if IPv == 'v4' else skt.AF_INET6, skt.SOCK_STREAM) as s:
    s.connect((ADDR, PORT))
    msg = input()

    while (msg != 'kill'):
      b_msg = str.encode(msg + '\n')
      s.sendall(b_msg)
      response = s.recv(BUFSZ).decode()
      if response == 'invalid command\n':
        break

      print(f'{response}', end='')
      msg = input()

if __name__ == '__main__':
  main()