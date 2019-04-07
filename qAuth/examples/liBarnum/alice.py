from qAuth.ent.liBarnum import Prover

def main():
    s = Prover("Alice")
    s.authenticate("Bob")

main()