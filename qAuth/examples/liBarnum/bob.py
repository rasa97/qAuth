from qAuth.ent.liBarnum import Authenticator

r = Authenticator("Bob")
result = r.authenticate()

if result:
    print("Successful Authentication!")
else:
    print("Unsuccessful Authentcation!")