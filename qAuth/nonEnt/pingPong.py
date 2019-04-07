from cqc.pythonLib import CQCConnection, qubit
import random

class Participant:

    def prepareSequence(self, key, receiver):
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
        for i in range(0, len(key)-1, 2):
            if(key[i] != key[i+1]):
                qubit_list[int(i/2)].X()
                qubit_list[int(i/2)].Z()
    
    def update_key(self, qubit_list, key):
        k_temp = ["*"]*int(len(key))
        for i in range(1, len(key), 2):
            if(key[i] == '1'):
                qubit_list[int((i-1)/2)].H()
            q_result = qubit_list[int((i-1)/2)].measure()

            k_temp[i] = str(q_result)
            k_temp[i-1] = str(int(key[i-1])^int(key[i])^int(k_temp[i]))
            k_prime = ''.join(k_temp)
        return k_prime


class Sender(Participant):

    def __init__(self, name):
        self.name = name

    def authenticate(self, key, receiver):
        self.prepareSequence(key, receiver)
        self.recvEncoded(key)
        check_kprime = self.checkAuth(key)
        return (check_kprime == self.k_prime, self.k_prime)
    
    def recvEncoded(self, key):
        with CQCConnection(self.name) as User:
            incoming_qubits = []
            for i in range(int(len(key)/2)):
                incoming_qubits.append(User.recvQubit())
            self.k_prime = self.update_key(incoming_qubits, key)
    
    def checkAuth(self, key):
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

class Receiver(Participant):

    def __init__(self, name):
        self.name = name
    
    def authenticate(self, key, sender):
        self.recvSequence(key, sender)
        return self.k_prime
    
    def recvSequence(self, key, name):
        with CQCConnection(self.name) as User:

            incoming_qubits = []
            for i in range(int(len(key)/2)):
                incoming_qubits.append(User.recvQubit())
            
            self.encodeQubits(incoming_qubits, key)
            self.k_prime = self.update_key(incoming_qubits, key)            
        self.sendEncoded(key, name)
    
    def sendEncoded(self, key, receiver):
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

