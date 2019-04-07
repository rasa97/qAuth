from qAuth.nonEnt.pingPong import Authenticator

def main():

    key = '001001000100100111101110'

    s = Authenticator("Alice")
    k_prime = s.authenticate(key, "Bob")
    print("Alice k' = ", k_prime)

main()