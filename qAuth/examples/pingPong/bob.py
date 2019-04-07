from qAuth.nonEnt.pingPong import Prover

def main():

    key = '001001000100100111101110'
    
    r = Prover("Bob")
    k_prime = r.authenticate(key, "Alice")
    print("Bob's k' = ", k_prime)

main()