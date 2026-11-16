import pickle 
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
port = ''
# port = str(int(constPipe.PORT2) + (int(me) - 1))

address1 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT1  # 1st task src
address2 = "tcp://" + constPipe.SRC2 + ":" + constPipe.PORT2
address3 = "tcp://" + constPipe.SRC2 + ":" + constPipe.PORT3

print('addr: ' + address2);

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
push_socket1 = context.socket(zmq.PUSH)  # create a push socket
push_socket2 = context.socket(zmq.PUSH)  # create a push socket

pull_socket.connect(address1)  # connect to task source 1
push_socket1.connect(address2)  # connect to task source 2
push_socket2.connect(address3)  # connect to task source 2

print("{} started".format(me))

while True:
    src_id, workload = pickle.loads(pull_socket.recv())  # receive work from a source (pickle: trusted peers only)
    print("{} received workload: \"{}\" from {}".format(me, workload, src_id))
    words = workload.split(' ')
    for word in words:
        if len(word) == 0:
            continue
        if len(word) % 2 == 0: 
            push_socket1.send(pickle.dumps((me, word)))
        else:
            push_socket2.send(pickle.dumps((me, word)))

    time.sleep(0.5)