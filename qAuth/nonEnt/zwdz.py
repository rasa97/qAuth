from cqc.pythonLib import CQCConnection, qubit
import hashlib

"""
    Module implementing Zawadzki Hash Protocol
    
    Zawadzki, Piotr. "Quantum identity authentication without entanglement." 
    Quantum Information Processing 18.1 (2019): 7.
"""

class Participants:

    def createHash(self, key, random_key):

        """
        Method that takes in key and random_key
        to produce 64 bit hex hash value.

        Parameters
        ----------

        key        : str
                     Secret Key Shared by two parties.
        random_key : str
                     Random key generated for this 
                     iteration for authentication.
        
        Returns
        -------
        str
            64 bit hex hash value.
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

    def __init__(self, name):
        self.name = name
    
    def authenticate(self, key, receiver):

        """
        Method that takes care of prover's job.

        Parameters
        ----------

        key        : str
                     Secret Key Shared by two parties.
        receiver : str
                     Authenticator's name.
        
        Returns
        -------
        None
            Does not return anything.
        """
        
        random_key = self.createRandom()
        hash_value = self.createHash(key, random_key)
        self.sendRandom(random_key, receiver)
        self.encodeSend(hash_value, receiver)
    
    def createRandom(self):

        """
        Method that creates the random key for the
        iteration. Uses randomness of Quantum 
        Mechanics to produce the required string

        Parameters
        ----------

        None
            Does not require any parameters.
        
        Returns
        -------
        str
            Returns 24 bit random bit string.
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

        Parameters
        ----------

        random_key : str
                     Random key generated for this 
                     iteration for authentication.
        receiver   : str
                     Authenticator's name

        
        Returns
        -------
        None
            Does not return anything.
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

        Parameters
        ----------

        hash_value : str
                     Hash value produced by key
                     and random_key.
        receiver   : str
                     Authenticator's name

        
        Returns
        -------
        None
            Does not return anything.
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

    def __init__(self, name):
        self.name = name

    def authenticate(self, key):

        """
        Method that takes care of authenticator's job.

        Parameters
        ----------

        key        : str
                     Secret Key Shared by two parties.
        
        Returns
        -------
        Boolean
            Result of authentication check.
        """

        random_key = self.recvRandom()
        hash_value = self.createHash(key, random_key)
        print(self.name, " hash_value : ", hash_value)
        auth_result = self.recvDecode(hash_value)
        return auth_result
    
    def recvRandom(self):

        """
        Method that receives the random
        number sent by prover.

        Parameters
        ----------

        None
            Does not need any paramenters.
        
        Returns
        -------
        string
            Returns random key.
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
        Method that receives the qubits,
        decodes it and checks for auth.

        Parameters
        ----------

        hash_value : str
                     Hash value produced by key
                     and random_key.

        
        Returns
        -------
        None
            Result of authentcation.
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
