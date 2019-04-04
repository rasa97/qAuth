from qAuth.nonEnt.zwdz import Receiver

key = '101010110001101110011001'

r = Receiver("Bob")

auth_result = r.authenticate(key)

if auth_result:
    print("Successful authentication!")
else:
    print("Unsuccessful authentication!")
