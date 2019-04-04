from qAuth.nonEnt.zwdz import Sender

key = '101010110001101110011001'

s = Sender("Alice")
s.authenticate(key, "Bob")