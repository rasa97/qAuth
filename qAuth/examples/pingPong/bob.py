from qAuth.nonEnt.pingPong import Receiver

key = '001001000100100111101110'

r = Receiver("Bob")
k_prime = r.authenticate(key, "Alice")
print("Bob's k' = ", k_prime)