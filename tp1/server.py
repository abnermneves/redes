import socket as skt
import re
import random
import sys
import pdb

# ------------- algumas funções úteis ------------- #
def unpack_int(lista):
  return ' '.join([f'{el:0>2}' for el in lista]) if lista else ''

def unpack_float(lista):
  return ' '.join([f'{el:.2f}' for el in lista]) if lista else ''

def qtd_sensores():
  qtd_sensores = 0
  for _, sensores in equipamentos.items():
    qtd_sensores += len(sensores)
  return qtd_sensores

def equipamento_invalido(id):
  return id < 1 or id > 4

def sensores_invalidos(sensores):
  return any([s < 1 or s > 4 for s in sensores])


# ------------- funções para a central ------------- #
def adicionar_sensores(sensores, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensores_invalidos(sensores):
    return 'invalid sensor'
    
  sensores_ja_existentes = [s for s in sensores if s in equipamentos[idEquipamento]]

  # assumindo que precisa caber todos os sensores ou nenhum será adicionado
  if qtd_sensores() + len(sensores) > MAX_SENSORS:
    return 'limit exceeded'
  if sensores_ja_existentes:
    return f'sensor {unpack_int(sensores_ja_existentes)} already exists in {idEquipamento:0>2}'
  
  equipamentos[idEquipamento] += sensores

  return f'sensor {unpack_int(sensores)} added'

def remover_sensor(sensor, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensor < 1 or sensor > 4:
    return 'invalid sensor'
  if sensor not in equipamentos[idEquipamento]:
    return f'sensor {sensor:0>2} does not exist in {idEquipamento:0>2}'

  equipamentos[idEquipamento].remove(sensor)

  return f'sensor {sensor:0>2} removed'

def consultar_equipamento(idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if not equipamentos[idEquipamento]:
    return 'none'

  return f'{unpack_int(equipamentos[idEquipamento])}'

def consultar_variaveis(sensores, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensores_invalidos(sensores):
    return 'invalid sensor'
    
  sensores_nao_instalados = [s for s in sensores if s not in equipamentos[idEquipamento]]

  if sensores_nao_instalados:
    return f'sensor(s) {unpack_int(sensores_nao_instalados)} not installed'

  valores = [] 
  for _ in range(len(sensores)):
    valores.append(random.randint(0, 1000) / 100)

  return unpack_float(valores)

# ------------- constantes e afins ------------- #
IPv = sys.argv[1]
PORT = int(sys.argv[2])
HOST = ''
# HOSTv4 = '127.0.0.1'
# HOSTv6 = '::1'
PORT = 51511
BUFSZ = 512 # tamanho da mensagem a receber do cliente
MAX_SENSORS = 15

# dicionário de pares equipamento : sensores
equipamentos = {
  1: [],
  2: [],
  3: [],
  4: []
}

def main():
  with skt.socket(skt.AF_INET if IPv == 'v4' else skt.AF_INET6, skt.SOCK_STREAM) as s:
    # associa o socket com todos os endereços disponíveis
    # e espera a conexão de algum cliente
    s.bind(('', PORT))
    s.listen()

    # aceita uma conexão e retorna um objeto de conexão e um endereço
    # conn é um objeto socket distinto do listening socket
    conn, addr = s.accept()

    with conn:
      print(f'Conectado em {addr}')
    
      while True:
        data = conn.recv(BUFSZ)
        if not data:
          break

        msg = data.decode()
        print(msg, end='')
        response = ''

        if re.fullmatch('add sensor (\d+ )+in \d+\n', msg):
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensores = ids[:-1]
          response = adicionar_sensores(sensores, idEquipamento)

        elif re.fullmatch('remove sensor \d+ in \d+\n', msg):
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensor = ids[0]
          response = remover_sensor(sensor, idEquipamento)

        elif re.fullmatch('list sensors in \d+\n', msg):
          ids = re.findall('\d+', msg)
          idEquipamento = int(ids[0])
          response = consultar_equipamento(idEquipamento)

        elif re.fullmatch('read (\d+ )+in \d+\n', msg):
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensores = ids[:-1]
          response = consultar_variaveis(sensores, idEquipamento)

        else:
          conn.sendall(str.encode('invalid command\n'))
          conn.close()
          break

        print(equipamentos)
        conn.sendall(str.encode(response + '\n'))

if __name__ == '__main__':
  main()