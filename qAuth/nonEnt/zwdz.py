from cqc.pythonLib import CQCConnection, qubit
import hashlib

class Participants:

    def createHash(self, key, random_key):
        final_key = key + random_key
        hashcode = hashlib.sha256((final_key).encode('utf-8')).hexdigest()
        hash_binary = ""

        for i in hashcode:
            binary = format(int(i, 16), '04b')
            hash_binary = hash_binary + binary

        """
            In ideal settings, we can use the whole 256 bits of hash_binary for the authentication process.
            Here however, we use just a subset of 10 bits from the whole 256 bits. The value of starting index
            in the hash_binary for the subset_hash  is the decimal form of biary number produced by concatinating 
            the first 4 bits of key and last 4 bit of random_key.

            That is, if the first 4 bits of key is 1010 and the last 4 bits of random_key is 0101, the binary rep
            of concatenaion operation = 10100101 and corresponsing decimal value is 165. Therefore, subset_hash is
            hash_binary[165:174]
        """

        concat = key[0:4] + random_key[-4:]
        decimal_concat = int(concat, 2)

        if decimal_concat < 246:
            return hash_binary[decimal_concat : decimal_concat+10]
        else:
            return hash_binary[-10:]

class Sender(Participants):

    def __init__(self, name):
        self.name = name
    
    def authenticate(self, key, receiver):
        random_key = self.createRandom()
        hash_value = self.createHash(key, random_key)
        print(self.name, " hash_value : ", hash_value)
        self.sendRandom(random_key, receiver)
        self.encodeSend(hash_value, receiver)
    
    def createRandom(self):
        random_key = ''
        with CQCConnection(self.name) as User:
            for i in range(24):
                q = qubit(User)
                q.H()
                random_key = random_key + str(q.measure())
        return random_key

    
    def sendRandom(self, random_key, receiver):
        message = []
        i=0
        while i < len(random_key):
            if i+8 <= len(random_key):
                temp = random_key[i: i+8]
            else:
                temp = random_key[i: len(random_key)]
            message.append(temp)
            i=i+8
        for i in range(len(message)):
            message[i] = int(message[i], 2)

        with CQCConnection(self.name) as User:
            User.sendClassical(receiver, message)
    
    def encodeSend(self, hash_value, receiver):
        with CQCConnection(self.name) as User:
            for i in range(int(len(hash_value)/2)):
                qA = qubit(User)
                if hash_value[2*i + 1] == "1":
                    qA.X()
                if hash_value[2*i] == "1":
                    qA.H()
                User.sendQubit(qA, receiver)


class Receiver(Participants):

    def __init__(self, name):
        self.name = name

    def authenticate(self, key):
        random_key = self.recvRandom()
        hash_value = self.createHash(key, random_key)
        print(self.name, " hash_value : ", hash_value)
        auth_result = self.recvDecode(hash_value)
        return auth_result
    
    def recvRandom(self):
        with CQCConnection(self.name) as User:
            data = User.recvClassical()
            message = list(data)
            random_key = ""
            for i in message:
                temp = "{0:{fill}8b}".format(i, fill='0')
                random_key = random_key + temp
            return random_key

    def recvDecode(self, hash_value):
        with CQCConnection(self.name) as User:
            incoming_qubits = []
            decode = ""
            for i in range(int(len(hash_value)/2)):
                incoming_qubits.append(User.recvQubit())
            
            for i in range(int(len(hash_value)/2)):
                decode = decode + hash_value[2*i]
                if hash_value[2*i] == "1":
                    incoming_qubits[i].H()
                decode = decode + str(incoming_qubits[i].measure())

        return decode == hash_value           
