# main.py
#
# @author Juan Arias
#
# Run the main function to use E-Wallets
#

from wallet import Wallet
from enum import Enum, IntEnum

TEST_EMDS = ('38FA8A457C688A3DCCA14EF70AF41200',
'5A7F7121C2B6A33AC5CC0A8A8D164D85',
'B7F6D20D26F158656ADA4B9B1F6AC76B',
'656C4E35D9AC045786C52710D926CDF8',
'7DDD4D75622AD4140EBE1FF5BC332319',
'506DA7C817847036740DDAF5924DBFCB',
'F27FBB631394F6A1D47046B77C81C0FD',
'8F59485FAA90FAD494B52646B3FA2BF2',
'62E4FEF3AA705C6DE2BD91028AEFDC62',
'EBBB632DA3240F6277C20830D6774213',
'DFF663AFB11C4E8450033D1E90DC8F18',
'9DC4B037A1772850022EBA2C45648F2F',
'2712213D11C79BEE5688CC44E9BDEF2A',
'EA3D8344E6D28F253B150A0C374AC7D0',
'8487D3DFACD1DDCF5E8DCB915865C8C8',
'1A8016A14B1FF899A8C929DE946976F7',
'9F65661B3F0AE52B60286E70C10831AC')

# Enums for prompts
class PROMPT(Enum):

    # Return string of value
    def __str__(self):
        return self.value

    CMD = 'Choose from the following commands\n1) process EMD token\n2) sync with a Wallet\n' \
          '3) process Wallet token\n4) generate a token\n5) process all EMDs from canvas\n' \
          '0) exit\n'
    ID = 'Enter your ID: '
    FIX = 'Invalid input, try again\n'
    EMD = 'Enter EMD token to process: '
    SYNC = 'Enter WalletID to sync: '
    PROC = 'Enter Wallet-generated token to process: '
    GEN = 'Enter WalletID and amount to generate token: '
    PRINT_TOKEN = 'token: {}'

# Enums for user commands
class CMD(IntEnum):

    EMD  = 1
    SYNC  = 2
    PROC = 3
    GEN  = 4
    ALL_EMD = 5

# Print token
def printToken(token):
    print(str(PROMPT.PRINT_TOKEN).format(token))

# Process user command
def process(cmd, myWallet):
    if (cmd == CMD.EMD):
        myWallet.processEMD(input(PROMPT.EMD))
    elif (cmd == CMD.SYNC):
        token = myWallet.sync(input(PROMPT.SYNC))
        printToken(token)
    elif (cmd == CMD.PROC):
        myWallet.processToken(input(PROMPT.PROC))
    elif (cmd == CMD.GEN):
        token = myWallet.generateToken(*parseInput())
        printToken(token)
    elif (cmd == CMD.ALL_EMD):
        for EMD in TEST_EMDS:
            printToken(EMD)
            if (myWallet.processEMD(EMD)):
                print(myWallet)
                print()
    print(myWallet)
    print()

# Prompts user for correctly parsed input for EMD1test
def parseInput():
    userInput = input(PROMPT.GEN)
    while (' ' not in userInput):
        print(PROMPT.FIX)
        userInput = input(PROMPT.GEN)
    ID, amount = userInput.split(' ')[:2]
    if (invalid(ID) or invalid(amount)):
        print(PROMPT.FIX)
        ID, amount = parseInput()
    return ID, amount

# Return true if input invalid
def invalid(info):
    try:
        int(info)
        return False
    except(ValueError):
        return  True

# Validate input
def getCMD():
    cmd = input(PROMPT.CMD)
    while (invalid(cmd)):
        print(PROMPT.FIX)
        cmd = input(PROMPT.CMD)
    return int(cmd)

# Test program
def main():
    myWallet = Wallet(input(PROMPT.ID))
    cmd = getCMD()
    while (cmd):
        process(cmd, myWallet)
        cmd = getCMD()

# Run program
main()