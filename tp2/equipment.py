from _thread import *
import socket as skt
import random
import pdb
import sys
import re

# ------------------------------------ constantes e afins ------------------------------------ #

ADDR = sys.argv[1]
PORT = int(sys.argv[2])
BUFSZ = 512 # tamanho da mensagem a receber do servidor

# IDs dos tipos de mensagens
REQ_ADD = 1
REQ_REM = 2
RES_ADD = 3
RES_LIST = 4
REQ_INF = 5
RES_INF = 6
ERROR = 7
OK = 8

# lista de equipamentos
equipments = []

# -------------------------- extração de informações das mensagens -------------------------- #

# retorna id gerado pelo servidor para o equipamento
def unpack_res_add(msg):
  id = re.findall('\d+', msg)[1]
  return int(id)

# retorna o id do equipamento a ser removido
def unpack_req_rem(msg):
  id = re.findall('\d+', msg)[1]
  return int(id)

# retorna lista de ids dos equipamentos instalados
def unpack_res_list(msg):
  ids = re.findall('\d+', msg)
  ids = [int(id) for id in ids[1:]]
  return ids

# retorna id source e id target do request information
def unpack_req_inf(msg):
  ids = re.findall('\d+', msg)[1:3]
  return [int(id) for id in ids]
  
# retorna id_source, id_target e o valor da informação solicitada
def unpack_res_inf(msg):
  # identifica números na mensagem
  numbers = msg.split(' ')

  # remove o id da mensagem e retorna os outros
  values = [int(n) for n in numbers[1:3]]
  values.append(float(numbers[3]))

  return values

# remove o id do erro e retorna a mensagem
def unpack_error(error):
  stripped_error = re.sub(f'^\d+ ', '', error)
  return stripped_error

# remove id do ok e retorna a mensagem
def unpack_ok(ok):
  stripped_ok = re.sub(f'^\d+ ', '', ok)
  return stripped_ok

# retorna o id da mensagem, sempre contido no início
def get_id_msg(msg):
  id = re.findall('^\d+', msg)
  id = int(id[0]) if id else ''

  return id

# retorna a lista de equipamentos como uma string
def get_eq_list():
  return ' '.join([f'{id:0>2}' for id in equipments])

# ------------------------------ manipulação da entrada padrão ------------------------------ #

# manipula a entrada padrão em threads múltiplas
def input_handler(s, idEq):
  # aguarda mensagem
  while True:
    msg = input()
    
    # identifica requisição de fechamento de conexão
    if msg == 'close connection':
      msg = f'{REQ_REM} {idEq}'
    
    # identifica requisição de listagem de equipamentos
    elif msg == 'list equipment':
      list_eq = get_eq_list()
      print(list_eq)

    # identifica requisição de informação
    elif re.fullmatch('request information from \d+', msg):
      id = re.findall('\d+', msg)[0]
      msg = f'{REQ_INF} {idEq} {id}'

    # envia mensagem no formato adequado      
    s.sendall(str.encode(msg))

# ----------------------------------- execução do programa ----------------------------------- #

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
    
    # aguarda resposta de conexão do servidor
    response = s.recv(BUFSZ).decode('utf-8')

    # identifica o tipo de mensagem
    id_msg = get_id_msg(response)

    # identifica se é erro
    if id_msg == ERROR:
      error = unpack_error(response)
      print(error)
      return

    # verifica se é algum outro tipo inesperado de mensagem
    elif id_msg != RES_ADD:
      print('outra mensagem recebida antes da confirmação de conexão RES_ADD')
      return

    # extrai id gerado pelo servidor
    idEq = unpack_res_add(response)
    print(f"New ID: {idEq:0>2}")
      
    # cria nova thread para aguardar input do teclado
    start_new_thread(input_handler, (s, idEq))

    # aguarda mensagens do servidor
    while True:
      response = s.recv(BUFSZ).decode('utf-8')
      id_msg = get_id_msg(response)

      # identifica mensagem do tipo REQ_REM e realiza ações
      if id_msg == REQ_REM:
        id_rem = unpack_req_rem(response)
        equipments.remove(id_rem)
        print(f'Equipment {id_rem:0>2} removed')

      # identifica mensagem do tipo RES_ADD e realiza ações
      elif id_msg == RES_ADD:
        idEq = unpack_res_add(response)
        equipments.append(idEq)
        print(f'Equipment {idEq:0>2} added')

      # identifica mensagem do tipo RES_LIST e realiza ações
      elif id_msg == RES_LIST:
        equipments = unpack_res_list(response)

      # # identifica mensagem do tipo REQ_INF e realiza ações
      elif id_msg == REQ_INF:
        print('requested information')
        info = random.randint(0, 1000) / 100
        id_source, id_target = unpack_req_inf(response)
        requested_info = f'{RES_INF} {id_target} {id_source} {info}'
        s.sendall(str.encode(requested_info))

      # identifica mensagem do tipo RES_INF e realiza ações
      elif id_msg == RES_INF:
        id_source, id_target, payload = unpack_res_inf(response)
        print(f'Value from {id_source:0>2}: {payload:.2f}')

      # identifica erros e escreve a mensagem na tela
      elif id_msg == ERROR:
        error = unpack_error(response)
        print(error)

      # identifica ok, escreve mensagem na tela e termina conexão
      elif id_msg == OK:
        ok = unpack_ok(response)
        print(ok)
        break

if __name__ == '__main__':
  main()
