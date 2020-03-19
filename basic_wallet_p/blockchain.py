'''
TO DO

1. Have ability to enter user like olympia -> INPUT 
2. Create user balance endpoint which sholud take in user and sum up all the transactions

'''
import requests

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

'''
UUID - unique user id- random # so big that it is extraordinarily improbable that a collision will happen. The probability it will be duplicated is not zero, but it is close enought o be 0 to be negligilbe. It's .00001% but it will happen eventually. Used as a unique address for this node. 

Flask- library for building APIs, app.route(/) is an endpoint

node_identifier not being used YET 


'''

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):
        """
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        #newest transaction go into next block 
        #w/e block we're working on is where the transaction goes 
        return self.last_block['index'] + 1 


    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            #TO DO
            'index': len(self.chain) +1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions - list of dicts, hash tables
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block 
        

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # sort_keys makes sure everything in dict is in order and in the same order every time
        string_block = json.dumps(block, sort_keys = True)

        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        #returns an object, but we want hexidecimal 
        raw_hash = hashlib.sha256(string_block.encode())

        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        hex_hash = raw_hash.hexdigest()

        # TODO: Create the block_string

        # TODO: Hash this string using sha256

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    #@ is called a decorator function, the property decorator specifically acts like a property, not a method (dont need to use parenthesis when you call this one and it'll give you the last block)
    #runtime complexity to retrieve last item in array is O(1)
    # BUT this is in a DB - still O(1) but memory its going to talk a LOT
    #even O(1) can scale and get problematic bc they interact w one another
    #if you have O(1) operation but lots of users and machines are hitting the endpoint it can still scale that way

    @property
    def last_block(self):
        return self.chain[-1]



    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO

        guess = f'{block_string}{proof}'.encode()
        #hexdigest makes it readable
        guess_hash = hashlib.sha256(guess).hexdigest()

        # return True or False
        # first three, otherwise takes 2-3 min to find a hash
        return guess_hash[:5] == "00000"



# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


"""
Create a new endpoint transactions/new
"""
@app.route('/transactions/new', methods=['POST'])
def receive_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        response = {'message': "Missing sender, recipient, or amount"}
        return jsonify(response), 400
    #this time sender is 
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/')
def api_up():
    return "Blockchain API is working!"

'''
Change to post
Use data = request.get_json() to get data
Check that proof and id are present - 
Return msg validating success or failure
A valid proof should fail for all senders except the first
'''
@app.route('/mine', methods=['POST'])
def mine():
     # Handle Non-JSON response - Parses the incoming JSON request data and returns it. 
    values = request.get_json()
    #breakpoint() to investigate what's in values 
    required = ["proof", "id"]

    # Check that proof and id are in POSTed data - for everything in a, check everything in b - nested for loop - O(2n) linear bc len of required will never change
    if not all(k in values for k in required):
        response = {'message': "Missing Values Error: Both proof and id must be supplied"}
        return jsonify(response), 400
    
    #get submitted proof from values dict
    submitted_proof = values['proof']

    #Get last block and test submitted proof
    block_string = json.dumps(blockchain.last_block, sort_keys = True)

    #return true or false if proof is valid 
    is_valid = blockchain.valid_proof(block_string, submitted_proof )
    # print('new is valid', is_valid)

    if is_valid is True: 
        #trasnaction
        blockchain.new_transaction('0',
            values['id'],
            1
        )

        #stringify last block 
        previous_hash = blockchain.hash(blockchain.last_block)
        forged_block = blockchain.new_block(submitted_proof, previous_hash)
        
        print("New block mined")
        #If they are in POSted data
        response = {
            "message": "New Block Forged",
            "forged_block": forged_block
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Error: Proof was invalid or already submitted"
        }
        return jsonify(response), 200


#if things are working, will this chain endpoint to anything? itll be empty but itll show up 
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200


#lask_block endpoint returns the last block in the chain
#no parentehesis needed for last_block bc a property decorator lets you access as property instead of method
@app.route('/last_block', methods=['GET'])
def return_last_block():
    response = {
        'last-block': blockchain.last_block 
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

