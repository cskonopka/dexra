import os
from dotenv import load_dotenv
import json
import time
import argparse
from tabulate import tabulate
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy, fast_gas_price_strategy, slow_gas_price_strategy
from web3.gas_strategies.time_based import construct_time_based_gas_price_strategy
from web3.gas_strategies.rpc import rpc_gas_price_strategy

load_dotenv()

INFURA_ADDRESS = os.getenv('INFURA_ADDRESS_POLYGON')
SELECTED_MAINNET = os.getenv('MAINNET_POLYGON')

## ARGPARSE
# https://docs.python.org/3/library/argparse.html
parser = argparse.ArgumentParser(description='Web3 exchange rates for a swap')
parser.add_argument('--fromToken', help='the token contract address that we want to swap', dest='fromTokenArg', type=str, required=True)
parser.add_argument('--tokenWant', help='the token contract address that we want to buy', dest='tokenWantArg', type=str, required=True)
parser.add_argument('--amt', help='emount of ether for initial trade, expressed in ether', dest='amtArg', required=True)
args = parser.parse_args()

working_directory = os.getcwd()

with open(str(working_directory)+'/docs/abi/erc20_abi.json') as f:
  inputABI = json.load(f)
exchangeABI = inputABI

with open(str(working_directory)+'/docs/abi/abi_dex_quickswap.json') as f:
  inputDexABI = json.load(f)
routerABI = inputDexABI

with open(str(working_directory)+'/docs/contracts/contracts_polygon.json') as f:
  inputContracts = json.load(f)
contracts = inputContracts

with open(str(working_directory)+'/docs/routers/routers_polygon.json') as f:
  inputRouters = json.load(f)
routers = inputRouters

# TRANSACTION DEADLINE
dline = (int(time.time()) + 10000)  
# TRANSACTION NODE
ethNodeURL = INFURA_ADDRESS
# TRANSACTION RPC
web3 = Web3(Web3.HTTPProvider(SELECTED_MAINNET))
# HOW MUCH DO I WANT TO SWAP?????
swapAmount=web3.toWei(args.amtArg, 'ether') 

def setupPrint():
    print("____________________")

    table_data = [
        ["dexra"],
        ["POLYGON"]
    ]
    for row in table_data:
        print("{: >20}".format(*row))

    print("____________________")


def theExchange():
    dex1=fromA2BStatic(contracts[str(args.fromTokenArg)], contracts[str(args.tokenWantArg)], 'quickswap')
    table1 = [["quickswap",dex1['inputExchangeRateAmt'],dex1['outputExchangeRateAmt'], dex1['inputTokenAmount'], dex1['outputTokenAmount']]]
    dex2=fromA2BStatic(contracts[str(args.fromTokenArg)], contracts[str(args.tokenWantArg)], 'sushiswap')
    table2 = [["sushiswap",dex2['inputExchangeRateAmt'],dex2['outputExchangeRateAmt'], dex2['inputTokenAmount'], dex2['outputTokenAmount']]]

    fullTable = table1 + table2 
    print(tabulate(fullTable, headers=["Swap",args.fromTokenArg +' 1:1', args.tokenWantArg+' 1:1', 'inputAmt', 'outputAmt']))
    print()
    time.sleep(1)


def fromA2BStatic(origin, toToken, router):
    universalRouter = web3.toChecksumAddress(routers[router]) 
    universalRouterCon = web3.eth.contract(address=universalRouter, abi=routerABI)        

    fromToken = web3.toChecksumAddress(origin)
    fromTokenCon = web3.eth.contract(address=fromToken, abi=exchangeABI)
    fromTokenName = fromTokenCon.functions.name().call()
    
    # WHAT DO I WANT TO SWAP FOR?
    tokenWant = web3.toChecksumAddress(toToken)
    tokenWantCon = web3.eth.contract(address=tokenWant, abi=exchangeABI)
    tokenWantName = tokenWantCon.functions.name().call()
    
    # EXCHANGE RATES
    path_AtoB = [fromToken, tokenWant]
    getAmtsOut = universalRouterCon.functions.getAmountsOut(swapAmount, path_AtoB).call()
    inputTokenAmount=getAmtsOut[0]*0.000000000000000001
    outputTokenAmount=getAmtsOut[1]*0.000000000000000001
    # EXCHANGE RATE OF SWAP
    getExchangeAmtOut = universalRouterCon.functions.getAmountsOut(1000000000000000000, path_AtoB).call()
    inputExchangeRateAmt=getExchangeAmtOut[0]*0.000000000000000001
    outputExchangeRateAmt=getExchangeAmtOut[1]*0.000000000000000001
    
    # APPLY RATE TO SWAP
    amountFromSwap=outputTokenAmount*int(swapAmount)

    # PRINTING COLUMNS OF DATA
    table_data2 = [
        [str(fromTokenName), "", str(tokenWantName), str(inputExchangeRateAmt),str(outputExchangeRateAmt),"", str(inputTokenAmount),
    (outputTokenAmount),""]
    ]

    d = dict();
    d['inputExchangeRateAmt']       = str(inputExchangeRateAmt)
    d['outputExchangeRateAmt']      = str(outputExchangeRateAmt)
    d['inputTokenAmount']           = str(inputTokenAmount)
    d['outputTokenAmount']          = str(outputTokenAmount)
    return d

def main():
    setupPrint()
    start=1
    while start:
        theExchange()

if __name__ == "__main__":
    main()