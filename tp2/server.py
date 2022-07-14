import socket as skt
from _thread import *
import sys
import pdb

PORT = int(sys.argv[1])
BUFSZ = 512 # tamanho da mensagem a receber do cliente
MAX_EQ = 15

errors =  {
  1 : 'Equipment not found',
  2 : 'Source equipment not found',
  3 : 'Target equipment not found',
  4 : 'Equipment limit exceeded'
}

eq_count = 0
equipments = {}

def broadcast(msg):
  for eq in equipments.values():
    eq.sendall(str.encode(msg))

def client_handler(connection):
  global eq_count, errors, equipments, PORT, BUFSZ, MAX_EQ
  if eq_count >= MAX_EQ:
    connection.sendall(str.encode(errors[4]))
    connection.close()
    return

  # define identificador e registra equipamento na base de dados
  eq_count += 1
  idEq = eq_count
  equipments[idEq] = connection
  print(f'Equipment {idEq} added')

  # envia RES_ADD com id do equipamento
  msg = str.encode(str(idEq))
  # connection.sendto(msg, ('255.255.255.255', PORT))
  # connection.sendall(str.encode(str(idEq)))
  broadcast(f'RES_ADD: {idEq}')

  # broadcast com novo id
  # to do

  while True:
    data = connection.recv(BUFSZ)
    reply = 'resposta: ' + data.decode('utf-8')

    if not data:
      break

    connection.sendall(str.encode(reply))

  connection.close()

def main():
  thread_count = 0

  with skt.socket() as s:
    try:
      # associa o socket com todos os endereços disponíveis
      s.bind(('', PORT))
    except skt.error as e:
      print(str(e))

    # espera a conexão de algum cliente
    s.listen()
    print('Aguardando conexão...')

    while True:
      client, address = s.accept()
      print('Conectado a: ' + address[0] + ' : ' + str(address[1]))
      start_new_thread(client_handler, (client, ))
      # pdb.set_trace()
      thread_count += 1
      # print('thread number: ' + str(thread_count))
      # pdb.set_trace()

if __name__ == '__main__':
  main()