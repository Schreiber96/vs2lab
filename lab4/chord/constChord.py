LOOKUP_REQ = '1'  # request for the successor of a key
LOOKUP_REP = '2'  # reply to a lookup request
JOIN = '3'  # a node announces itself to the other nodes of the ring
LEAVE = '4'  # a node leaves the ring (handled by ChordNode, not sent in this example)
ANNOUNCE = '5'  # not used in this example
STOP = '6'  # a node is requested to shut down
