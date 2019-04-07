from cqc.pythonLib import CQCConnection, qubit

"""
    Module implementing Li-Barnum QIA with entangled particles
    Li, Xiaoyu, and Howard Barnum. "Quantum authentication using entangled states." 
    International Journal of Foundations of Computer Science 15.04 (2004): 609-617.
"""

class Participant:
    
    def createEnt(self, qubitA, qubitB, type):

        """
        Method that takes in two qubits and produce one
        of the four Bell states.

        Parameters
        ----------

        qubitA : Qubit Object
                 First Qubit to the EPR Pair.
        qubitB : Qubit object
                 Second Qubit to the EPR Pair.
        type   : int
                 The type of EPR Pair. 
                 Type1 : |phi+> 
                 Type2 : |phi->
                 Type3 : |psi+>
                 Type4 : |psi->
        
        Returns
        -------
        List
            List of two Quantum Objects that are entangled.
        """

        if type > 2:
            qubitB.X()
        if type%2 == 0:
            qubitA.X()
        qubitA.H()
        qubitA.cnot(qubitB) 
        return [qubitA, qubitB]


class Prover(Participant):

    def __init__(self, name):
        self.name = name
        self.idToken = []
        self.auxPairs = []
        self.number_tokens = 4
    
    def authenticate(self, receiver):

        """
        Method that takes care of prover's job.

        Parameters
        ----------

        receiver : str
                 Name of the Authenticator.
        
        Returns
        -------
        None
            Does not return anything.
        """

        with CQCConnection(self.name) as User:

            for i in range(self.number_tokens):

                # Create and distribute ID Tokens 
                self.idToken.append(self.createEnt(qubit(User), qubit(User), 2))
                User.sendQubit(self.idToken[i][1], receiver)

                # Create and store Aux Pairs
                self.auxPairs.append(self.createEnt(qubit(User), qubit(User), 2))

            # Apply CNOT Operation
            self.cnotS()

            # Send Auxiliary pairs to Authenticator
            for i in range(self.number_tokens):
                User.sendQubit(self.auxPairs[i][0], receiver)
                User.sendQubit(self.auxPairs[i][1], receiver)
    
    def cnotS(self):

        """
        Method that applies CNOT operation for the prover.

        Parameters
        ----------

        None
            Does not require any parameters.
        
        Returns
        -------
        None
            Does not return anything.
        """

        for i in range(self.number_tokens):
            self.auxPairs[i][0].cnot(self.idToken[i][0])

            
class Authenticator(Participant):

    def __init__(self, name):
        self.name = name
        self.idToken = []
        self.number_tokens = 4
        self.auxPairs = [] 

    def authenticate(self):

        """
        Method that takes care of authenticator's job.

        Parameters
        ----------

        None
            Does not require any parameters.
        
        Returns
        -------
        None
            Does not return anything.
        """

        with CQCConnection(self.name) as User:

            # Receive ID Token
            for i in range(self.number_tokens):
                self.idToken.append(User.recvQubit())

            # Receive Auxiliary Pairs
            for i in range(self.number_tokens):
                q1 = User.recvQubit()
                q2 = User.recvQubit()
                self.auxPairs.append([q1, q2])

            # Apply CNOT Operation
            self.cnotR()

            #Bell Measurement
            result = self.bellMeasure()

            #Check Authentication result
            flag = 0
            for i in result:
                if i != [0,0]:
                    flag = 1
                    break
        
        #Return Authentication result
        return flag == 0
            

    def cnotR(self):

        """
        Method that applies CNOT Operation with Aux Pairs and ID Token.

        Parameters
        ----------

        None
            Does not require any parameters.
        
        Returns
        -------
        None
            Does not return anything.
        """

        for i in range(self.number_tokens):
            self.auxPairs[i][1].cnot(self.idToken[i])
    
    def bellMeasure(self):

        """
        Method that does the Bell Measurement of Aux Particles.

        Parameters
        ----------

        None
            Does not require any parameters.
        
        Returns
        -------
        List
            List of Bell Measurement result.
        """

        measurement = []
        for i in range(self.number_tokens):
            self.auxPairs[i][0].cnot(self.auxPairs[i][1])
            self.auxPairs[i][0].H()
            m1 = self.auxPairs[i][0].measure()
            m2 = self.auxPairs[i][1].measure()
            measurement.append([m1, m2])
        
        return measurement
