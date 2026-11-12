import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
match me:
    case '1':
        address = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT2  # 1st task src
    case '2':
        address = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT3  # 2nd task src

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
pull_socket.bind(address)

print("{} started".format(me))

words = {}

def countWords(workload):
    workloadLowerCase = workload if isinstance(workload, int) else workload.lower()

    if workloadLowerCase not in words:
        words[workloadLowerCase] = 1
        return 'Reducer {} hat das Wort "{}" vom Mapper {} hinzugefügt.'.format(me, workload, src_id)
    else:
        words[workloadLowerCase] += 1
        count = words[workloadLowerCase]
        return 'Reducer {} hat das Wort "{}" vom Mapper {} aktualisiert. Neue Anzahl: {}'.format(me, workload, src_id, count)

while True:
    src_id, workload = pickle.loads(pull_socket.recv())
    result = countWords(workload)
    print(result)
    time.sleep(0.2)