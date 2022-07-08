import sys

sys.path.append('.\\Lib\\site-packages')

import datetime

import hashlib

import json

from flask import Flask, jsonify

from flask_ngrok import run_with_ngrok

 

# Создание блокчейна

class Blockchain:

   

  def __init__(self):

    """ Конструктор класса Blockchain. """

 

    self.chain = []

    self.create_block(proof = 1, previous_hash = '0')

     

 

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

              'previous_hash' : previous_hash}

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

 

# Создание программы web

app = Flask(__name__)

run_with_ngrok(app)  

 

# Если в ответ получаете ошибку 500, обновите flask и запустите эту линию

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

 

# Создание Blockchain

blockchain = Blockchain()

 

@app.route('/mine_block', methods=['GET'])

def mine_block():

  """ Майнинг нового блока """

 

  previous_block  = blockchain.get_previous_block()

  previous_proof  = previous_block['proof']

  proof           = blockchain.proof_of_work(previous_proof)

  previous_hash   = blockchain.hash(previous_block)

  block           = blockchain.create_block(proof, previous_hash)

  response = {'message'       : 'Поздравляем, вы добыли новый блок!',

              'index'         : block['index'],

              'timestamp'     : block['timestamp'],

              'proof'         : block['proof'],

              'previous_hash' : block['previous_hash']}

  return jsonify(response), 200

 

@app.route('/get_chain', methods=['GET'])

def get_chain():

  """ Получение блокчейна """

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

      response = {'message' : 'Цепочка блоков НЕ правильная!'}

  return jsonify(response), 200  

 

# Запуск программы

app.run()
 

# Проверка запросами:

# Calls: http://localhost:5000/mine_block

# Calls: http://localhost:5000/get_chain

# Calls: http://localhost:5000/is_valid
