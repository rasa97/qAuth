from cqc.pythonLib import CQCConnection, qubit
import random

"""
    Module implementing Ping Pong without Entanglement Protocol
    Yuan, Hao, et al. "Quantum identity authentication based on ping-pong technique without entanglements." 
    Quantum information processing 13.11 (2014): 2535-2549.
"""

class Participant:

    """
        Class which defines common functions.
        Prover and Authenticator inherit this class.
    """

    def prepareSequence(self, key, receiver):

        """
        Method that prepares the qubits
        according to the protocol and 
        sends it to the receiver.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param receiver: Authenticator's name.
        :type receiver: str
        """

        with CQCConnection(self.name) as User:
            self.randomChoice = []
            for i in range(1, len(key), 2):
                q=qubit(User)
                r = random.randint(0,1)
                self.randomChoice.append(r)
                if(key[i] == '0'):
                    if(r):
                        q.X()
                else:
                    if(r):
                        q.X()
                    q.H()                    
                User.sendQubit(q, receiver)
    
    def encodeQubits(self, qubit_list, key):

        """
        Method that encodes the qubits
        according to the protocol.

        :param qubit_list: List of qubits to encode.
        :type qubit_list: list of Qubit Objects
        :param key: Secret Key Shared by two parties.
        :type key: str
        """

        for i in range(0, len(key)-1, 2):
            if(key[i] != key[i+1]):
                qubit_list[int(i/2)].X()
                qubit_list[int(i/2)].Z()
    
    def update_key(self, qubit_list, key):

        """
        Method that updates the key.

        :param qubit_list: List of qubits to encode.
        :type qubit_list: list of Qubit Objects
        :param key: Secret Key Shared by two parties.
        :type key: str

        :return: Updated Key
        :rtype: String
        """

        k_temp = ["*"]*int(len(key))
        for i in range(1, len(key), 2):
            if(key[i] == '1'):
                qubit_list[int((i-1)/2)].H()
            q_result = qubit_list[int((i-1)/2)].measure()

            k_temp[i] = str(q_result)
            k_temp[i-1] = str(int(key[i-1])^int(key[i])^int(k_temp[i]))
            k_prime = ''.join(k_temp)
        return k_prime


class Authenticator(Participant):

    """
        Class for Authenticator
    """

    def __init__(self, name):

        """
            Creates a Authenticator by providing a name
        """

        self.name = name

    def authenticate(self, key, receiver):

        """
        Method that takes care of authenticator's job.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param receiver: Prover's name.
        :type receiver: str

        :return: Result of authentication check and updated key.
        :rtype: Tuple
        """

        self.prepareSequence(key, receiver)
        self.recvEncoded(key)
        check_kprime = self.checkAuth(key)
        return (check_kprime == self.k_prime, self.k_prime)
    
    def recvEncoded(self, key):

        """
        Method that receives the encoded qubits.

        :param key: Secret Key Shared by two parties.
        :type key: str
        """

        with CQCConnection(self.name) as User:
            incoming_qubits = []
            for i in range(int(len(key)/2)):
                incoming_qubits.append(User.recvQubit())
            self.k_prime = self.update_key(incoming_qubits, key)
    
    def checkAuth(self, key):

        """
        Method that authenticates the prover.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :return: Updated Key
        :rtype: String
        """

        with CQCConnection(self.name) as User:
            qubit_list = []
            for i in range(1, len(key), 2):
                q=qubit(User)
                r = self.randomChoice[int((i-1)/2)]
                if(key[i] == '0'):
                    if(r):
                        q.X()
                else:
                    if(r):
                        q.X()
                    q.H()                    
                qubit_list.append(q)
            
            self.encodeQubits(qubit_list, key)
            check_kprime = self.update_key(qubit_list, key)
            return check_kprime

class Prover(Participant):

    """
        Class for Prover
    """

    def __init__(self, name):

        """
            Creates a Prover by providing a name
        """

        self.name = name
    
    def authenticate(self, key, sender):

        """
        Method that takes care of prover's job.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param sender: Authenticator's name.
        :type sender: str

        :return: Updated Key.
        :rtype: String
        """

        self.recvSequence(key, sender)
        return self.k_prime
    
    def recvSequence(self, key, name):

        """
        Method that receives ping pong particles
        from authenticator.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param name: Authenticator's name.
        :type name: str
        """

        with CQCConnection(self.name) as User:

            incoming_qubits = []
            for i in range(int(len(key)/2)):
                incoming_qubits.append(User.recvQubit())
            
            self.encodeQubits(incoming_qubits, key)
            self.k_prime = self.update_key(incoming_qubits, key)            
        self.sendEncoded(key, name)
    
    def sendEncoded(self, key, receiver):

        """
        Method that encodes ping pong particles
        and send it to the authenticator.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param receiver: Authenticator's name.
        :type receiver: str
        """

        with CQCConnection(self.name) as User:

            for i in range(1, len(key), 2):
                q = qubit(User)
                
                if self.k_prime[i] == '1' and key[i] == '0':
                    q.X()
                    q.Z()
                
                if self.k_prime[i] == '0' and key[i] == '1':
                    q.X()
                    q.H()
                    q.X()
                    q.Z()
                
                if self.k_prime[i] == '1' and key[i] == '1':
                    q.X()
                    q.H()

                User.sendQubit(q, receiver)

