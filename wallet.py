# wallet.py
#
# @author Juan Arias
#
# Classes for E-Wallet Model

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import Hash, SHA256

# Wallet class hold a balance in U.S. currency for the users,
# it uses AES256 encryption to send and receive money tokens to other Wallets
# or receive an Electronic Money Draft(EMD) from the bank
class Wallet:

    # Class for U.S. currency
    class Balance:

        # Construct balance with given dollars and cents
        def __init__(self, dollars = 0):
            self.__dollars = dollars

        # Return string
        def __str__(self):
            return '${}.00'.format(self.__dollars)

        # Compare greator or equal with number
        def __ge__(self, num):
            return self.__dollars >= num

        # Deposit given amount
        def deposit(self, dollars):
            if (dollars and Wallet.isValid(dollars)):
                self.__dollars += dollars

        # Withdraw given amount
        def withdraw(self, dollars):
            sufficient = False
            if (Wallet.isValid(dollars) and dollars <= self.__dollars):
                self.__dollars -= dollars
                sufficient = True
            return sufficient

    # Same key is defined for whole class
    BANK_KEY = 'F25D58A0E3E4436EC646B58B1C194C6B505AB1CB6B9DE66C894599222F07B893'

    # Encoding for plaintxt to byte conversion for SHA
    ENCODING = 'ascii'

    # Char for padding
    PAD_CHAR = '0'

    # MAX digit length of amount for funds
    INFO_LEN = 3

    # Length of MAX padding for each section of info in Wallet to Wallet funds
    MAX_FUND_PAD = 8

    # Length of MIN padding for each section of info in Wallet to Wallet funds
    MIN_FUND_PAD = 5

    # MAX length for a plaintxt msg
    MSG_LEN = 32

    # Info sections per plaintxt msg from other Wallet
    INFO_PER_MSG = 4

    # Range for padding plaintxt in a loop
    PLAINTXT_RANGE = range(MIN_FUND_PAD, MSG_LEN, MAX_FUND_PAD)

    # Max amount to trasnfer or receive
    MAX_AMOUNT = 999

    # Counter and amount for synchronization
    SYNC = 0

    # Tell user about error in decryption
    INVALID_INPUT = 'ERROR: check input formats, your balance and synched Wallets\n'

    # Wallet str() printing
    STR = 'wallet{}: {}'

    # Successful sync from processing token
    SYN_MSG = 'now synced with wallet{}'

    # Successful funds transfer from processing token
    FUND_MSG = 'wallet{} has deposited ${}'

    # Parse select digits from full ID
    @staticmethod
    def parseID(ID):
        return ID[-Wallet.INFO_LEN:]

    # Return true if info from plaintxt is valid
    @staticmethod
    def isValid(info):
        try:
            valid = 0 <= int(info) <= Wallet.MAX_AMOUNT
        except(ValueError):
            valid = False
        return valid

    # SHA256 message digest of given plaintext
    @staticmethod
    def hash(plaintxt):
        digest = Hash(SHA256(), default_backend())
        digest.update(bytes(plaintxt, Wallet.ENCODING))
        return digest.finalize().hex().upper()

    # Full padding for EMD plaintxt
    @staticmethod
    def padEMD(plaintxt):
        padLen = Wallet.MSG_LEN - len(plaintxt)
        prePadding = ''.join([Wallet.PAD_CHAR for _ in range(padLen)])
        return prePadding + plaintxt

    # AES-256, CBC mode, PKCS7 padding
    @staticmethod
    def AES(key):
        return Cipher(algorithms.AES(bytes.fromhex(key)), modes.ECB(), default_backend())

    # Encryption with AES for Wallet class
    @staticmethod
    def encrypt(plaintxt, key, EMD = False):
        if (len(plaintxt) == Wallet.MSG_LEN or (EMD and Wallet.isValid(plaintxt))):
            plaintxt = Wallet.padEMD(plaintxt) if (EMD) else plaintxt
            encryptor = Wallet.AES(key).encryptor()
            try:
                ciphertxt = encryptor.update(bytes.fromhex(plaintxt)) + encryptor.finalize()
                ciphertxt = ciphertxt.hex().upper()
            except(ValueError):
                ciphertxt = Wallet.INVALID_INPUT
        else:
            ciphertxt = Wallet.INVALID_INPUT
        return ciphertxt

    # Decryption with AES for Wallet class
    @staticmethod
    def decrypt(ciphertxt, key):
        decryptor = Wallet.AES(key).decryptor()
        try:
            plaintxt = decryptor.update(bytes.fromhex(ciphertxt)) + decryptor.finalize()
            plaintxt =  plaintxt.hex().upper()
        except (ValueError):
            plaintxt = None
        return plaintxt

    # Pad info to be packed into from plaintxt
    @staticmethod
    def pad(info):
        return info.zfill(Wallet.MAX_FUND_PAD)

    # Unpad info parsed from plaintxt
    @staticmethod
    def unpad(info):
        return info.lstrip(Wallet.PAD_CHAR)

    # Pack info into a plaintxt string to be encrypted
    @staticmethod
    def pack(infoList):
        return ''.join(Wallet.pad(str(each)) for each in infoList)

    # Parse info from decrypted token aka plaintxt
    @staticmethod
    def unpack(plaintxt):
        return [Wallet.unpad(plaintxt[i: i + Wallet.INFO_LEN]) for i in Wallet.PLAINTXT_RANGE]

    # Safely convert ctr
    @staticmethod
    def safeCtr(ctr):
        return Wallet.SYNC if (ctr == '') else int(ctr)

    # Construct Wallet with given ID
    def __init__(self, ID):
        self.__ID = Wallet.parseID(ID)
        self.__key = Wallet.hash(ID)
        self.__table = {}
        self.__balance = Wallet.Balance()

    # Return balance as string
    def __str__(self):
        return Wallet.STR.format(self.__ID, self.__balance)

    # Deposit given amount
    def __deposit(self, amount):
            self.__balance.deposit(int(amount))

    # Deposit given amount
    def __withdraw(self, amount):
        return self.__balance.withdraw(int(amount))

    # Update walletID, sequenceNo table
    def __updateTable(self, otherID):
        self.__table[otherID] = self.__getCtr(otherID, True) + 1

    # Return the correct counter value for the given WalletID
    def __getCtr(self, otherID, num = False):
        ctr = self.__table[otherID] if (otherID in self.__table) else Wallet.SYNC
        return ctr if num else str(ctr)

    # Return True if given info resembles a sync
    def __isSync(self, otherID, ctr):
        return otherID not in self.__table and ctr == Wallet.SYNC

    # Return True if given info is valid for a funds transfer
    def __inTable(self, otherID, ctr):
        return otherID in self.__table and ctr == self.__table[otherID]

    # Process transaction info from decrypted token aka plaintxt
    def __process(self, otherID, thisID, amount, ctr):
        msg = Wallet.INVALID_INPUT
        if (otherID != self.__ID and thisID == self.__ID):
            if (self.__isSync(otherID, ctr)):
                self.__updateTable(otherID)
                msg = Wallet.SYN_MSG.format(otherID)
            elif (self.__inTable(otherID, ctr)):
                self.__deposit(amount)
                self.__updateTable(otherID)
                msg = Wallet.FUND_MSG.format(otherID, amount)
        print(msg)

    # Return true if ID and amount are valid to generate a token with
    def __canGen(self, otherID, amount):
        return self.__ID != otherID and Wallet.isValid(otherID) and Wallet.isValid(amount) and \
               self.__withdraw(amount)

    # Process a given EMD token from bank
    def processEMD(self, token):
        amount = Wallet.decrypt(token, self.__key)
        processed = False
        if (amount):
            amount = Wallet.unpad(amount)
            if (Wallet.isValid(amount)):
                self.__deposit(amount)
                processed = True
        if (not processed):
            print(Wallet.INVALID_INPUT)
        return processed

    # Return WalletID
    def getID(self):
        return self.__ID

    # Synchronize with Wallet with given ID
    def sync(self, otherID):
        token = Wallet.INVALID_INPUT
        if (otherID not in self.__table):
            token = self.generateToken(otherID, Wallet.SYNC)
        return token

    # Generate token for depositing the given amount to the walletID
    def generateToken(self, otherID, amount):
        token = Wallet.INVALID_INPUT
        ctr = self.__getCtr(otherID, True)
        if ((ctr != Wallet.SYNC or amount == Wallet.SYNC) and self.__canGen(otherID, amount)):
            plaintxt = Wallet.pack([self.__ID, otherID, amount, ctr])
            token = Wallet.encrypt(plaintxt, Wallet.BANK_KEY)
            self.__updateTable(otherID)
        return token

    # Process token generated by other Wallet
    def processToken(self, token):
        plaintxt = Wallet.decrypt(token, Wallet.BANK_KEY)
        if (plaintxt):
            infoList = Wallet.unpack(plaintxt)
            infoList[-1] = Wallet.safeCtr(infoList[-1])
            self.__process(*infoList)
        else:
            print(Wallet.INVALID_INPUT)