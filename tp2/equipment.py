import socket as skt
from _thread import *
from struct import unpack
import sys
import re
import pdb

ADDR = sys.argv[1]
PORT = int(sys.argv[2])
BUFSZ = 512 # tamanho da mensagem a receber do servidor
equipments = {}

def unpack_res_add(msg):
  if not re.fullmatch('RES_ADD: \d+', msg):
    return ''
  
  id = re.findall('\d+', msg)[0]
  return id

# --------------------------------- execução do programa --------------------------------- #

def input_handler(s):
  while True:
    msg = input()
    s.sendall(str.encode(msg))

def main():
  # cria um socket com IPv4
  with skt.socket() as s:
    try:
      # conecta ao servidor solicitado
      s.connect((ADDR, PORT))
    except skt.error as e:
      print(str(e))
      return
    
    response = s.recv(BUFSZ).decode('utf-8')
    idEq = unpack_res_add(response)

    print(f"New ID: {idEq}")

    # thread para aguardar input do teclado
    start_new_thread(input_handler, (s, ))

    # aguardando mensagens do servidor
    while True:
      response = s.recv(BUFSZ)
      print(response.decode('utf-8'))

if __name__ == '__main__':
  main()