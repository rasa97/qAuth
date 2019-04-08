from cqc.pythonLib import CQCConnection, qubit
import hashlib

"""
    Module implementing Zawadzki Hash Protocol
    
    Zawadzki, Piotr. "Quantum identity authentication without entanglement." 
    Quantum Information Processing 18.1 (2019): 7.
"""

class Participants:

    """
        Class which defines common functions.
        Prover and Authenticator inherit this class.
    """

    def createHash(self, key, random_key):

        """
        Method that takes in key and random_key
        to produce 64 bit hex hash value.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param random_key: Random key generated for this iteration for authentication.
        :type random_key: str

        :return: 64 bit hex hash value.
        :rtype: str
        
        """

        final_key = key + random_key
        hashcode = hashlib.sha256((final_key).encode('utf-8')).hexdigest()
        hash_binary = ""

        for i in hashcode:
            binary = format(int(i, 16), '04b')
            hash_binary = hash_binary + binary

        
            """In ideal settings, we can use the whole 256 bits of hash_binary for the authentication process.
            Here however, we use just a subset of 10 bits from the whole 256 bits. The value of starting index
            in the hash_binary for the subset_hash  is the decimal form of biary number produced by concatinating 
            the first 4 bits of key and last 4 bit of random_key.

            That is, if the first 4 bits of key is 1010 and the last 4 bits of random_key is 0101, the binary rep
            of concatenaion operation = 10100101 and corresponsing decimal value is 165. Therefore, subset_hash is
            hash_binary[165:174]"""
        

        concat = key[0:4] + random_key[-4:]
        decimal_concat = int(concat, 2)

        if decimal_concat < 246:
            return hash_binary[decimal_concat : decimal_concat+10]
        else:
            return hash_binary[-10:]

class Prover(Participants):

    """
        Class for Prover
    """

    def __init__(self, name):

        """
            Creates a Prover by providing a name
        """

        self.name = name
    
    def authenticate(self, key, receiver):

        """
        Method that takes care of prover's job.

        :param key: Secret Key Shared by two parties.
        :type key: str
        :param receiver: Authenticator's name.
        :type receiver: str
        """
        
        random_key = self.createRandom()
        hash_value = self.createHash(key, random_key)
        self.sendRandom(random_key, receiver)
        self.encodeSend(hash_value, receiver)
    
    def createRandom(self):

        """
        Method that creates the random key for the
        iteration. Uses randomness of Quantum 
        Mechanics to produce the required string.

        :return: Random key.
        :rtype: String
        """
        
        random_key = ''
        with CQCConnection(self.name) as User:
            for i in range(24):
                q = qubit(User)
                q.H()
                random_key = random_key + str(q.measure())
        return random_key

    
    def sendRandom(self, random_key, receiver):

        """
        Method that sends the random_key generated
        before. It convert the string type to 
        suitable type so that we can send through
        the classical server provided by SimulaQron.

        :param random_key: Random key generated for this iteration for authentication.
        :type random_key: str
        :param receiver: Authenticator's name.
        :type receiver: str
        """

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

        """
        Method that encodes the hash key in Qubits.

        :param hash_value: Hash value produced by key and random_key.
        :type hash_value: str
        :param receiver: Authenticator's name.
        :type receiver: str
        """

        with CQCConnection(self.name) as User:
            for i in range(int(len(hash_value)/2)):
                qA = qubit(User)
                if hash_value[2*i + 1] == "1":
                    qA.X()
                if hash_value[2*i] == "1":
                    qA.H()
                User.sendQubit(qA, receiver)


class Authenticator(Participants):

    """
        Class for Authenticator
    """

    def __init__(self, name):

        """
            Creates a Authenticator by providing a name
        """

        self.name = name

    def authenticate(self, key):

        """
        Method that takes care of authenticator's job.

        :param key: Secret Key Shared by two parties.
        :type key: str

        :return: Result of authentication check.
        :rtype: Boolean
        """

        random_key = self.recvRandom()
        hash_value = self.createHash(key, random_key)
        print(self.name, " hash_value : ", hash_value)
        auth_result = self.recvDecode(hash_value)
        return auth_result
    
    def recvRandom(self):

        """
        Method that receives the random number sent by prover.

        :return: Returns random key.
        :rtype: String
        """

        with CQCConnection(self.name) as User:
            data = User.recvClassical()
            message = list(data)
            random_key = ""
            for i in message:
                temp = "{0:{fill}8b}".format(i, fill='0')
                random_key = random_key + temp
            return random_key

    def recvDecode(self, hash_value):

        """
        Method that receives the qubits, decodes it and checks for auth.

        :param hash_value: Hash value produced by key and random_key.
        :type hash_value: str

        :return: Result of authentication check.
        :rtype: Boolean
        """

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
