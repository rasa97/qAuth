from qAuth.nonEnt.zwdz import Prover

key = '101010110001101110011001'

s = Prover("Alice")
s.authenticate(key, "Bob")