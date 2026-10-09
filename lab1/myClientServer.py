"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    book = {}


    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))
        self.book = dict(Bob = "0187", Rob = "0123")


    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    msg = data.decode("ascii")
                    msg_arr = msg.split(";")
                    if msg_arr[0] == 'Get':
                        name = msg_arr[1]
                        name = name.strip()
                        if name == "":
                            connection.send("Error;no name given".encode("ascii"))
                            self._logger.info("no name given")
                            break
                        if name not in self.book:
                            connection.send(("Error;invalid name").encode("ascii"))
                            self._logger.info("invalid name")
                            break
                        number = self.book.get(name)
                        connection.send(("Return;" + number).encode("ascii"))
                        self._logger.info("reply successfull")
                    if msg_arr[0] == "GetAll":
                        
                        msgOut = "ReturnAll;"
                        for key, value in self.book.items():
                            msgOut += key + "," + value + ';'   
                        connection.send(msgOut.encode("ascii"))
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def get(self, nameIn):
        self.call("Get;" + nameIn)

    def getAll(self):
        self.call("GetAll;")
        self.close()

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        msg_arr = msg_out.split(';')
        if msg_arr[0] == 'Return':
            print('Name: ' + msg_in.split(';')[1] + ' Number: ' + msg_arr[1])
        if msg_arr[0] == 'ReturnAll':
            for item in msg_arr[1:]:
                if item == "":
                    continue;
                item_arr = item.split(',')
                print('Name: ' + item_arr[0] + ' Number: ' + item_arr[1])
        if msg_arr[0] == "Error":
            print(msg_arr[1])
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def close(self):
        """ Close socket """
        self.sock.close()
