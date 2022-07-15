import socket as skt
from _thread import *
from struct import unpack
import sys
import re
import pdb

ADDR = sys.argv[1]
PORT = int(sys.argv[2])
BUFSZ = 512 # tamanho da mensagem a receber do servidor
equipments = []

REQ_ADD = 1
REQ_REM = 2
RES_ADD = 3
RES_LIST = 4
REQ_INF = 5
RES_INF = 6
ERROR = 7
OK = 8

def unpack_res_add(msg):
  stripped_msg = re.sub(f'^\d+ ', '', msg)
  
  id = re.findall('\d+', stripped_msg)[0]

  return int(id)

def unpack_res_list(msg):
  ids = re.findall('\d+', msg)
  ids = [int(id) for id in ids[1:]]
  return ids

def unpack_error(error):
  stripped_error = re.sub(f'^\d+ ', '', error)

  return stripped_error

def get_id_msg(msg):
  id = re.findall('^\d+', msg)
  id = int(id[0]) if id else ''

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

    id_msg = get_id_msg(response)

    if id_msg == ERROR:
      error = unpack_error(response)
      print(error)
      return

    elif id_msg != RES_ADD:
      print('id msg diferente de res add')
      pdb.set_trace()

    idEq = unpack_res_add(response)

    print(f"New ID: {idEq}")
      
    # thread para aguardar input do teclado
    start_new_thread(input_handler, (s, ))

    # aguardando mensagens do servidor
    while True:
      response = s.recv(BUFSZ).decode('utf-8')
      id_msg = get_id_msg(response)

      if id_msg == RES_ADD:
        idEq = unpack_res_add(response)
        equipments.append(idEq)
        print(f'Equipment {idEq} added')
      
      elif id_msg == RES_LIST:
        equipments = unpack_res_list(response)
        # pdb.set_trace()
      elif id_msg == RES_INF:
        pass
      elif id_msg == ERROR:
        error = unpack_error(response)
        print(error)

      elif id_msg == OK:
        pass

      print(f'equipamentos: {equipments}')


if __name__ == '__main__':
  main()