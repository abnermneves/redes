from _thread import *
import socket as skt
import pdb
import sys
import re

# ------------------------------------ constantes e afins ------------------------------------ #

PORT = int(sys.argv[1])
BUFSZ = 512 # tamanho da mensagem a receber do cliente
MAX_EQ = 15

# IDs dos tipos de mensagens
REQ_ADD = 1
REQ_REM = 2
RES_ADD = 3
RES_LIST = 4
REQ_INF = 5
RES_INF = 6
ERROR = 7
OK = 8

# tabela de erros
errors =  {
  1 : 'Equipment not found',
  2 : 'Source equipment not found',
  3 : 'Target equipment not found',
  4 : 'Equipment limit exceeded'
}

# tabela de OKs
success = {
  1 : 'Successful removal'
}

# lista e contador de equipamentos
eq_count = 0
equipments = {}

# -------------------------- extração de informações das mensagens -------------------------- #

# retorna o id do equipamento a ser removido
def unpack_req_rem(msg):
  id = re.findall('\d+', msg)[1]
  return int(id)

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

# ------------------------------------ ações do servidor ------------------------------------ #

# atende a solicitação de remoção de quipamento
def remove_equipment(id):
  # se o equipamento não existe, retorna erro
  if id not in equipments:
    return f'{ERROR} {errors[1]}'

  # se existe, remove e retorna ok
  del equipments[id]

  return f'{OK} {success[1]}'

# atende a solicitação de informação de um equipamento
def request_information(msg):
  id_source, id_target = unpack_req_inf(msg)

  # verificação de existência do equipamento de origem
  if id_source not in equipments:
    print(f'Equipment {id_source:0>2} not found')
    response = f'{ERROR} {errors[2]}'    
    return response, id_source

  # verificação de existência do equipamento de destino
  if id_target not in equipments:
    print(f'Equipment {id_target:0>2} not found')
    response = f'{ERROR} {errors[3]}'
    return response, id_source

  # se ambos existirem, repassa a mensagem para o equipamento de destino
  return msg, id_target

# tratamento da informação solicitada
def respond_information(msg):
  id_source, id_target, _ = unpack_res_inf(msg)

  # verificação de existência do equipamento de origem
  if id_source not in equipments:
    print(f'Equipment {id_source:0>2} not found')
    response = f'{ERROR} {errors[2]}'    
    return response, id_source

  # verificação de existência do equipamento de destino
  if id_target not in equipments:
    print(f'Equipment {id_target:0>2} not found')
    response = f'{ERROR} {errors[3]}'
    return response, id_target

  # se ambos existirem, repassa a informação ao destino
  return msg, id_target 

# -------------------------------------- funções úteis -------------------------------------- #

# retorna o id da mensagem, sempre contido no início
def get_id_msg(msg):
  id = re.findall('^\d+', msg)
  id = int(id[0]) if id else ''

  return id

# retorna a lista de equipamentos como uma string
def get_eq_list():
  return ' '.join([f'{id:0>2}' for id in equipments])

# realiza transmissão em broadcast
def broadcast(msg):
  for id, eq in equipments.items():
    try:
      eq.sendall(str.encode(msg))
    except skt.error as e:
      print(f'broadcast error to eq {id:0>2}: {e}')

# ---------------------------------- manipulação do cliente ---------------------------------- #

# manipula cada cliente em threads múltiplas
def client_handler(connection):
  global eq_count, errors, equipments, PORT, BUFSZ, MAX_EQ

  # recusa a conexão caso o máximo de equipamentos tenha sido atingido
  if eq_count >= MAX_EQ:
    connection.sendall(str.encode(f'{ERROR} {errors[4]}'))
    connection.close()
    return

  # obtém lista de equipamento antes de adicionar o novo, para enviar a ele
  eq_list = get_eq_list

  # define identificador e registra equipamento na base de dados
  eq_count += 1
  idEq = eq_count
  equipments[idEq] = connection
  print(f'Equipment {idEq:0>2} added')

  # broadcast de RES_ADD com id do novo equipamento
  broadcast(f'{RES_ADD} {idEq}')

  # envia lista de equipamentos já conectados para o novo equipamento
  res_list = f'{RES_LIST} {eq_list}'
  connection.sendall(str.encode(res_list))

  # escuta as mensagens do equipamento
  while True:
    request = connection.recv(BUFSZ).decode('utf-8')
    id_msg = get_id_msg(request)

    # identifica mensagem REQ_REM pelo seu id e realiza as ações
    if id_msg == REQ_REM:
      idEq = unpack_req_rem(request)
      response = remove_equipment(idEq)

      connection.sendall(str.encode(response))
      connection.close()

      print(f'Equipment {idEq:0>2} removed')
      broadcast(f'{REQ_REM} {idEq}')

      break
    
    # identifica mensagem REQ_INF pelo seu id e realiza as ações
    elif id_msg == REQ_INF:
      response, send_to = request_information(request)
      equipments[send_to].sendall(str.encode(response))

    # identifica mensagem RES_INF pelo seu id e realiza as ações
    elif id_msg == RES_INF:
      response, send_to = respond_information(request)
      equipments[send_to].sendall(str.encode(response))

    # if not request:
    #   break
    
  # connection.close()

# ----------------------------------- execução do programa ----------------------------------- #

def main():
  with skt.socket() as s:
    try:
      # associa o socket com todos os endereços disponíveis
      s.bind(('', PORT))
    except skt.error as e:
      print(str(e))

    # espera a conexão de algum cliente
    s.listen()

    # aceita conexões e cria nova thread para cada uma
    while True:
      client, address = s.accept()
      start_new_thread(client_handler, (client, ))
      # print('Conectado a: ' + address[0] + ' : ' + str(address[1]))

if __name__ == '__main__':
  main()
