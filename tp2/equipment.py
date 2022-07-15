import socket as skt
from _thread import *
from struct import unpack
import sys
import re
import random
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
  id = re.findall('\d+', msg)[1]

  return int(id)

def unpack_req_rem(msg):
  # segundo id da mensagem
  id = re.findall('\d+', msg)[1]

  return int(id)

def unpack_res_list(msg):
  ids = re.findall('\d+', msg)
  ids = [int(id) for id in ids[1:]]
  return ids

def unpack_req_inf(msg):
  # id source e id target
  ids = re.findall('\d+', msg)[1:3]
  return [int(id) for id in ids]
  
def unpack_res_inf(msg):
  # retorna id_source, id_target e info
  numbers = msg.split(' ')
  values = [int(n) for n in numbers[1:3]]
  values.append(float(numbers[3]))

  return values

def unpack_error(error):
  stripped_error = re.sub(f'^\d+ ', '', error)

  return stripped_error

def unpack_ok(ok):
  stripped_ok = re.sub(f'^\d+ ', '', ok)

  return stripped_ok

def get_id_msg(msg):
  id = re.findall('^\d+', msg)
  id = int(id[0]) if id else ''

  return id

def get_eq_list():
  # global equipments
  return ' '.join([f'{id:0>2}' for id in equipments])

# --------------------------------- execução do programa --------------------------------- #

def input_handler(s, idEq):
  while True:
    msg = input()
    
    if msg == 'close connection':
      msg = f'{REQ_REM} {idEq}'
    
    elif msg == 'list equipment':
      list_eq = get_eq_list()
      print(list_eq)

    elif re.fullmatch('request information from \d+', msg):
      id = re.findall('\d+', msg)[0]
      msg = f'{REQ_INF} {idEq} {id}'
      
    s.sendall(str.encode(msg))

def main():
  global equipments
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
      print('outra mensagem recebida antes da confirmação de conexão RES_ADD')

    idEq = unpack_res_add(response)

    print(f"New ID: {idEq}")
      
    # thread para aguardar input do teclado
    start_new_thread(input_handler, (s, idEq))

    # aguardando mensagens do servidor
    while True:
      response = s.recv(BUFSZ).decode('utf-8')
      id_msg = get_id_msg(response)

      if id_msg == RES_ADD:
        idEq = unpack_res_add(response)
        equipments.append(idEq)
        print(f'Equipment {idEq} added')

      if id_msg == REQ_REM:
        id_rem = unpack_req_rem(response)
        equipments.remove(id_rem)
        print(f'Equipment {id_rem} removed')

      elif id_msg == RES_LIST:
        equipments = unpack_res_list(response)
        # pdb.set_trace()

      elif id_msg == REQ_INF:
        print('requested information')
        info = random.randint(0, 1000) / 100
        id_source, id_target = unpack_req_inf(response)
        requested_info = f'{RES_INF} {id_target} {id_source} {info}'
        s.sendall(str.encode(requested_info))

      elif id_msg == RES_INF:
        id_source, id_target, payload = unpack_res_inf(response)
        print(f'Value from {id_source}: {payload}')

      elif id_msg == ERROR:
        error = unpack_error(response)
        print(error)

      elif id_msg == OK:
        ok = unpack_ok(response)
        print(ok)
        break

if __name__ == '__main__':
  main()