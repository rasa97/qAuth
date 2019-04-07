from cqc.pythonLib import CQCConnection, qubit

class Participant:
    
    def createEnt(self, qubitA, qubitB, type):

        """
        Parameters:

        qubitA : First Qubit to the EPR Pair.
        qubitB : Second Qubit to the EPR Pair.
        type   : The type of EPR Pair. 
                 Type1 : |phi+> 
                 Type2 : |phi->
                 Type3 : |psi+>
                 Type4 : |psi->
        """

        if type > 2:
            qubitB.X()
        if type%2 == 0:
            qubitA.X()
        qubitA.H()
        qubitA.cnot(qubitB) 
        return [qubitA, qubitB]

            

class Sender(Participant):

    def __init__(self, name):
        self.name = name
        self.idToken = []
        self.auxPairs = []
        self.number_tokens = 4
    
    def authenticate(self, receiver):
        with CQCConnection(self.name) as User:

            for i in range(self.number_tokens):
                self.idToken.append(self.createEnt(qubit(User), qubit(User), 2))
                User.sendQubit(self.idToken[i][1], receiver)
                self.auxPairs.append(self.createEnt(qubit(User), qubit(User), 2))

            self.cnotS()

            for i in range(self.number_tokens):
                User.sendQubit(self.auxPairs[i][0], receiver)
                User.sendQubit(self.auxPairs[i][1], receiver)
            
    
    def displayID(self):
        
        for i in range(self.number_tokens):
            print("Sender ", i, " : ", self.idToken[i][0].measure())
    
    def cnotS(self):

        for i in range(self.number_tokens):
            self.auxPairs[i][0].cnot(self.idToken[i][0])

            
class Receiver(Participant):

    def __init__(self, name):
        self.name = name
        self.idToken = []
        self.number_tokens = 4
        self.auxPairs = [] 

    def authenticate(self):

        with CQCConnection(self.name) as User:

            for i in range(self.number_tokens):
                self.idToken.append(User.recvQubit())

            for i in range(self.number_tokens):
                q1 = User.recvQubit()
                q2 = User.recvQubit()
                self.auxPairs.append([q1, q2])

            self.cnotR()
            self.bellMeasure()

    
    def displayID(self):

        for i in range(self.number_tokens):
            print("Receiver " , i, " : ", self.idToken[i].measure())

    def cnotR(self):

        for i in range(self.number_tokens):
            self.auxPairs[i][1].cnot(self.idToken[i])
    
    def bellMeasure(self):

        measurement = []
        for i in range(self.number_tokens):
            self.auxPairs[i][0].cnot(self.auxPairs[i][1])
            self.auxPairs[i][0].H()
            m1 = self.auxPairs[i][0].measure()
            m2 = self.auxPairs[i][1].measure()
            measurement.append([m1, m2])
        
        print(measurement)
