import socket as skt
import random
import sys
import re

# --------------------------------- algumas funções úteis --------------------------------- #

# converte lista de números para string com espaço como separador
def unpack_int(lista):
  return ' '.join([f'{el:0>2}' for el in lista]) if lista else ''

# converte lista de números para string com duas casas decimais
def unpack_float(lista):
  return ' '.join([f'{el:.2f}' for el in lista]) if lista else ''

# quantidade de sensores já instalados em todos os equipamentos
def qtd_sensores():
  qtd_sensores = 0
  for _, sensores in equipamentos.items():
    qtd_sensores += len(sensores)
  return qtd_sensores

# true, se o equipamento não for da Tabela I
def equipamento_invalido(id):
  return id < 1 or id > 4

# true, se há algum sensor inválido na lista
def sensores_invalidos(sensores):
  return any([s < 1 or s > 4 for s in sensores])


# --------------------------------- funções para a central --------------------------------- #

def adicionar_sensores(sensores, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensores_invalidos(sensores):
    return 'invalid sensor'
  
  # encontra sensores solicitados que já foram instalados antes
  sensores_ja_existentes = [s for s in sensores if s in equipamentos[idEquipamento]]

  # verifica se os sensores não ultrapassam o limite,
  # assumindo que precisa caber todos os sensores solicitados ou nenhum será adicionado
  if qtd_sensores() + len(sensores) > MAX_SENSORS:
    return 'limit exceeded'
  if sensores_ja_existentes:
    return f'sensor {unpack_int(sensores_ja_existentes)} already exists in {idEquipamento:0>2}'
  
  # adiciona os sensores
  equipamentos[idEquipamento] += sensores

  return f'sensor {unpack_int(sensores)} added'

def remover_sensor(sensor, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensor < 1 or sensor > 4:
    return 'invalid sensor'
  if sensor not in equipamentos[idEquipamento]:
    return f'sensor {sensor:0>2} does not exist in {idEquipamento:0>2}'

  # remove o sensor, se não for inválido ou não instalado
  equipamentos[idEquipamento].remove(sensor)

  return f'sensor {sensor:0>2} removed'

def consultar_equipamento(idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if not equipamentos[idEquipamento]:
    return 'none'

  # retorna uma lista com os sensores instalados
  return f'{unpack_int(equipamentos[idEquipamento])}'

def consultar_variaveis(sensores, idEquipamento):
  if equipamento_invalido(idEquipamento):
    return 'invalid equipment'
  if sensores_invalidos(sensores):
    return 'invalid sensor'
    
  # verifica se algum sensor solicitado ainda não foi instalado
  sensores_nao_instalados = [s for s in sensores if s not in equipamentos[idEquipamento]]
  if sensores_nao_instalados:
    return f'sensor(s) {unpack_int(sensores_nao_instalados)} not installed'

  # gera números aleatórios como leitura dos sensores solicitados
  valores = [] 
  for _ in range(len(sensores)):
    valores.append(random.randint(0, 1000) / 100)

  return unpack_float(valores)

# --------------------------------- constantes e afins --------------------------------- #

IPv = sys.argv[1]
PORT = int(sys.argv[2])
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

# --------------------------------- execução do programa --------------------------------- #

def main():
  # cria o socket com AF_INET ou AF_INET6, dependendo da versão solicitada
  with skt.socket(skt.AF_INET if IPv == 'v4' else skt.AF_INET6, skt.SOCK_STREAM) as s:
    # associa o socket com todos os endereços disponíveis
    s.bind(('', PORT))

    # espera a conexão de algum cliente
    s.listen()

    # aceita uma conexão com um cliente e retorna um objeto de conexão e um endereço
    # conn é um objeto socket distinto do listening socket
    conn, addr = s.accept()

    with conn:
      print(f'Conectado em {addr}')
    
      while True:
        # recebe mensagem do cliente
        data = conn.recv(BUFSZ)
        if not data:
          break

        msg = data.decode()
        print(msg, end='')
        response = ''

        # identifica mensagem para adicionar sensor
        if re.fullmatch('add sensor (\d+ )+in \d+\n', msg):
          # encontra todos os IDs na mensagem
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensores = ids[:-1]

          # executa a ação solicitada, se possível, e recebe mensagem como response
          response = adicionar_sensores(sensores, idEquipamento)

        # identifica mensagem para remover sensor
        elif re.fullmatch('remove sensor \d+ in \d+\n', msg):
          # encontra todos os IDs na mensagem
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensor = ids[0]

          # executa a ação solicitada, se possível, e recebe mensagem como response
          response = remover_sensor(sensor, idEquipamento)

        # identifica mensagem para consultar equipamento
        elif re.fullmatch('list sensors in \d+\n', msg):
          # encontra ID do equipamento
          ids = re.findall('\d+', msg)
          idEquipamento = int(ids[0])

          # executa a ação, se possível, e recebe mensagem como response
          response = consultar_equipamento(idEquipamento)

        # identifica mensagem para consultar os sensores
        elif re.fullmatch('read (\d+ )+in \d+\n', msg):
          # encontra todos os IDs na mensagem
          ids = re.findall('\d+', msg)
          ids = [int(id) for id in ids]
          idEquipamento = ids[-1]
          sensores = ids[:-1]

          # executa a ação, se possível, e recebe mensagem como response
          response = consultar_variaveis(sensores, idEquipamento)

        # tratamento para comando inválido, que é enviado ao cliente e encerra conexão
        else:
          conn.sendall(str.encode('invalid command\n'))
          conn.close()
          break

        # print(equipamentos)

        # envia a resposta da ação solicitada para o cliente,
        # indicando se houve sucesso ou falha
        conn.sendall(str.encode(response + '\n'))

if __name__ == '__main__':
  main()