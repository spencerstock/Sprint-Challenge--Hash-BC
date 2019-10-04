import hashlib
import requests
import json
import sys

from random import randint
from uuid import uuid4
from timeit import default_timer as timer
from flask import Flask, jsonify, request

saved_hashes = {}


def proof_of_work(last_proof):
    start = timer()

    print("Searching for next proof")
    proof = randint(0, 110000000)
    last_hash = hashlib.sha256(str(last_proof).encode()).hexdigest()
    #checking dictionary for a previously stored solution
    if last_hash[-6:] in saved_hashes.keys(): 
        proof = saved_hashes[last_hash[-6:]]
    else:
        while valid_proof(last_hash, proof) == False:
            proof += 1
    return proof

    print("Proof found: " + str(proof) + " in " + str(timer() - start))
    return proof


def valid_proof(last_hash, proof):

    guess = str(proof).encode()

    myhash = hashlib.sha256(guess).hexdigest()
    #saving every hash into the dictionary for future use
    saved_hashes[myhash[:6]] = guess 

    return myhash[:6] == last_hash[-6:]



if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "https://lambda-coin.herokuapp.com/api"

    coins_mined = 0

    # Load or create ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()


    if id == 'NONAME\n':
        print("ERROR: You must change your name in `my_id.txt`!")
        exit()
    # Run forever until interrupted
    while True:
        # Get the last proof from the server
        r = requests.get(url=node + "/last_proof")
        data = r.json()
        new_proof = proof_of_work(data.get('proof'))

        post_data = {"proof": new_proof,
                     "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()
        if data.get('message') == None:
            coins_mined += 1
            print("Total coins mined: " + str(coins_mined))
        else:
            print(data.get('message'))
