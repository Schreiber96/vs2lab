import pickle
import random
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])

host = constPipe.SRC1
port = constPipe.PORT1


context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = "tcp://" + host + ":" + port  # how and where to bind
push_socket.bind(address)  # bind socket to address

time.sleep(1)  # give all workers time to connect (needed for an even distribution)

# Read Text
with open('text.txt', 'r') as file:
    content = file.read()

textArr = content.split('.')

for i in range(len(textArr)):
    workload = textArr[i]
    push_socket.send(pickle.dumps((me, workload)))  # send workload to worker (pickle: trusted peers only)