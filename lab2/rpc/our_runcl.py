import our_rpc as rpc
import logging
import time

from context import lab_logging

def print_callback(result):
    print("Result: {}".format(result.value))

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
result_list = cl.append('bar', base_list, print_callback)


for i in range(1,21,1):
    time.sleep(1)
    print(str(i) + ': Main Thread')


cl.stop()

