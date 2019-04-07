from qAuth.nonEnt.pingPong import Sender

key = '001001000100100111101110'

s = Sender("Alice")
k_prime = s.authenticate(key, "Bob")
print("Alice k' = ", k_prime)