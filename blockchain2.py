import sys

sys.path.append('.\\Lib\\site-packages')

import datetime

import hashlib

import json

import requests

from uuid         import uuid4

from flask        import Flask, jsonify, request

from urllib.parse import urlparse

from flask_ngrok  import run_with_ngrok



class Blockchain:



  def __init__(self):

    """ Конструктор класса. """



    self.chain = []

    self.transactions = []

    self.create_block(proof = 1, previous_hash = '0')

    self.nodes = set()



  def create_block(self, proof, previous_hash):

    """ Создание нового блока.



      Аргументы:

        - proof: "Nounce" текущего блока. (proof != hash)

        - previous_hash: хеш предыдущего блока.



      Возврат:

        - block: Новый созданный блок.

      """



    block = { 'index'         : len(self.chain)+1,

              'timestamp'     : str(datetime.datetime.now()),

              'proof'         : proof,

              'previous_hash' : previous_hash,

              'transactions'  : self.transactions}

    self.transactions = []

    self.chain.append(block)

    return block



  def get_previous_block(self):

    """ Получение предыдущего блока из Блокчейна .



      Возврат:

        - Последний блока из блокчейна. """



    return self.chain[-1]



  def proof_of_work(self, previous_proof):

    """ Протокол консенсуса Proof of Work (PoW) (Доказательство работы).



      Аргументы:

        - previous_proof: "Nounce" предыдущего блока.



      Возврат:

        - new_proof: Возврат нового "Nounce", полученного с помощью PoW. """



    new_proof = 1

    check_proof = False

    while check_proof is False:

        hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

        if hash_operation[:4] == '0000':

            check_proof = True

        else:

            new_proof += 1

    return new_proof



  def hash(self, block):

    """ Вычисление хеша блока.



    Аргументы:

        - block: Идентифицирует блок блокчейна..



    Возврат:

        - hash_block: Возвращает хэш блока """



    encoded_block = json.dumps(block, sort_keys = True).encode()

    hash_block = hashlib.sha256(encoded_block).hexdigest()

    return hash_block



  def is_chain_valid(self, chain):

    """ Определяет действителен ли блокчейн.



    Аргументы:

        - chain: Блокчейн, содержащий всю информацию о транзакциях.



    Возврат:

        - True/False: Возвращает логическое значение на основе достоверности блокчейна. (True = Правильный, False = Неправильный) """



    previous_block = chain[0]

    block_index = 1

    while block_index < len(chain):

        block = chain[block_index]

        if block['previous_hash'] != self.hash(previous_block):

            return False

        previous_proof = previous_block['proof']

        proof = block['proof']

        hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()

        if hash_operation[:4] != '0000':

            return False

        previous_block = block

        block_index += 1

    return True



  def add_transaction(self, sender, receiver, amount):

    """ Добавление новой транзакции.



    Аргументы:

        - sender: Лицо отправляющее крипто монеты

        - receiver: Лицо, принимающее транзакцию

        - amount: Количество отправленной криптовалюты



    Возврат:

        - Возврат индекса выше последнего блока

    """



    self.transactions.append({'sender'  : sender,

                              'receiver': receiver,

                              'amount'  : amount})

    previous_block = self.get_previous_block()

    return previous_block['index'] + 1



  def add_node(self, address):

    """ Добавление нового нода/узла в блокчейн.



      Аргументы:

        - address: Адрес нового узла

    """



    parsed_url = urlparse(address)

    self.nodes.add(parsed_url.netloc)



  def replace_chain(self):

    """ Замена цепочки самой длинной цепочкой блоков, если она действительна/правильная. """



    network = self.nodes

    longest_chain = None

    max_length = len(self.chain)

    for node in network:

        response = requests.get(f'http://{node}/get_chain')

        if response.status_code == 200:

            length = response.json()['length']

            chain = response.json()['chain']

            if length > max_length and self.is_chain_valid(chain):

                max_length = length

                longest_chain = chain

    if longest_chain:

        self.chain = longest_chain

        return True

    return False



# Создание программы web

app = Flask(__name__)

run_with_ngrok(app)



# Если в ответ получаете ошибку 500, обновите flask и запустите эту линию

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False



# Создаём адрес ноды и открываем работу на порте 5000

node_address = str(uuid4()).replace('-', '')



# Создание Blockchain

blockchain = Blockchain()


@app.route('/check_balance', methods=['GET'])

def check_balance():
    res = {}
    for i in range(len(blockchain.transactions)):
        try:
            res[blockchain.transactions[i]['receiver']] += int(blockchain.transactions[i]['amount'])
            res[blockchain.transactions[i]['sender']] -= int(blockchain.transactions[i]['amount'])
        except:
            res[blockchain.transactions[i]['receiver']] = int(blockchain.transactions[i]['amount'])
            res[blockchain.transactions[i]['sender']] = - int(blockchain.transactions[i]['amount'])
    return jsonify(res), 200


@app.route('/mine_block', methods=['GET'])

def mine_block():

  """ Майнинг нового блока """



  previous_block = blockchain.get_previous_block()

  previous_proof = previous_block['proof']

  proof = blockchain.proof_of_work(previous_proof)

  previous_hash = blockchain.hash(previous_block)

  blockchain.add_transaction(sender = node_address, receiver = "Anton Polenyaka", amount = 10)

  block = blockchain.create_block(proof, previous_hash)

  response = {'message'       : 'Поздравляем, вы добыли новый блок!',

              'index'         : block['index'],

              'timestamp'     : block['timestamp'],

              'proof'         : block['proof'],

              'previous_hash' : block['previous_hash'],

              'transactions'  : block['transactions']}

  return jsonify(response), 200



@app.route('/get_chain', methods=['GET'])

def get_chain():

  """ Получение всей цепочки блоков """



  response = {'chain'   : blockchain.chain,

              'length'  : len(blockchain.chain)}

  return jsonify(response), 200



@app.route('/is_valid', methods = ['GET'])

def is_valid():

  """ Проверка правильности блокчейна """



  is_valid = blockchain.is_chain_valid(blockchain.chain)

  if is_valid:

      response = {'message' : 'Цепочка блоков правильная!'}

  else:

      response = {'message' : 'Цепочка блоков НЕправильная!'}

  return jsonify(response), 200



@app.route('/add_transaction', methods = ['POST'])

def add_transaction():

  """ Добавить новую транзакцию в блокчейн """



  json = request.get_json()

  transaction_keys = ['sender', 'receiver', 'amount']

  if not all(key in json for key in transaction_keys):

      return 'Отсутствуют некоторые элементы транзакции', 400

  index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])

  response = {'message': f'Транзакция будет добавлена в блок {index}'}

  return jsonify(response), 201

@app.route('/add_test_transaction', methods = ['GET'])

def add_test_transaction():

    index = blockchain.add_transaction("ANTON", "MARINA", 5)

    response = {'message': f'Транзакция будет добавлена в блок {index}'}

    return jsonify(response), 201



# Децентрализация блокчейна



# Подключить новые узлы

@app.route('/connect_node', methods = ['POST'])

def connect_node():

  json = request.get_json()

  nodes = json.get('nodes')

  if nodes is None:

      return 'Нет узлов для добавления', 400

  for node in nodes:

      blockchain.add_node(node)

  response = {'message'     : 'Все узлы подключены. Блокчейн FortaCoins теперь содержит следующие узлы: ',

              'total_nodes' : list(blockchain.nodes)}

  return jsonify(response), 201



@app.route('/replace_chain', methods = ['GET'])

def replace_chain():

  """ Замените цепочку блоков на самую длинную (при необходимости) """



  is_chain_replaced = blockchain.replace_chain()

  if is_chain_replaced:

      response = {'message' : 'Узлы имеют разные цепочки блоков, поэтому цепочка данного узла заменена на самую длинную из цепочек блоков.',

                  'new_chain': blockchain.chain}

  else:

      response = {'message'       : 'Всё хорошо. Цепочка блоков на всех узлах уже самая длинная.',

                  'actual_chain'  : blockchain.chain}

  return jsonify(response), 200



# Запуск программы

app.run()
