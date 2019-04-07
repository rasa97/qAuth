from qAuth.nonEnt.zwdz import Authenticator

key = '101010110001101110011001'

r = Authenticator("Bob")

auth_result = r.authenticate(key)

if auth_result:
    print("Successful authentication!")
else:
    print("Unsuccessful authentication!")
