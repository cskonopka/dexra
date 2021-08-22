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

## ARGPARSE
# https://docs.python.org/3/library/argparse.html
parser = argparse.ArgumentParser(description='Web3 exchange rates for a swap')
parser.add_argument('--fromToken', help='the token contract address that we want to swap', dest='fromTokenArg', type=str, required=True)
parser.add_argument('--tokenWant', help='the token contract address that we want to buy', dest='tokenWantArg', type=str, required=True)
parser.add_argument('--amt', help='emount of ether for initial trade, expressed in ether', dest='amtArg', required=True)
args = parser.parse_args()

## ABI Templates 
ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')
uniabi = json.loads('[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]')

# CONTRACTS
contracts = {"matic": '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270', 
          "dai": '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063', 
          "aave": '0xd6df932a45c0f255f85145f286ea0b292b21c90b',
          "uniswap": '0xb33eaad8d922b1083446dc23f610c2567fb5180f',
          "usdc": '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
          "curve": '0x172370d5cd63279efa6d502dab29171933a610af',
          "wbtc": '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',
          "curve": '0x831753dd7087cac61ab5644b308642cc1c33dc13',
          "sushi": '0x0b3f868e0be5597d5db7feb59e1cadbb0fdda50a',
          "must": '0x9C78EE466D6Cb57A4d01Fd887D2b5dFb2D46288f'}

routers = {"quickswap": '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff', 
            "cometh": '0xc168e40227e4ebd8c1cae80f7a55a4f0e6d66c97',
            "sushiswap": '0x1b02da8cb0d097eb8d57a175b88c7d8b47997506',
            "kyber": '0x1c954e8fe737f99f68fa1ccda3e51ebdb291948c',
            "firebird": '0x39D736D2b254eE30796f43Ec665143010b558F82'}

# TRANSACTION DEADLINE
dline = (int(time.time()) + 10000)  
# TRANSACTION NODE
# ethNodeURL = f'https://polygon.infura.io/v3/14f8d25612be43e6a6376a9b2d1eacc0'
ethNodeURL = INFURA_ADDRESS
# TRANSACTION RPC
web3 = Web3(Web3.HTTPProvider('https://rpc-mainnet.matic.network'))
# HOW MUCH DO I WANT TO SWAP?????
swapAmount=web3.toWei(args.amtArg, 'ether') 
# WHAT ROUTER?
# universalRouter = web3.toChecksumAddress(routers['quickswap']) 
routerArgg = " "

def setupPrint(router):
    print("____________________")
    print()

    table_data = [
        ["dexra"],
        ["POLYGON"],
        [routerArgg]
    ]
    for row in table_data:
        print("{: >20}".format(*row))

    print("____________________")


def theExchange(router):
    a=fromA2BStatic(contracts[str(args.fromTokenArg)], contracts[str(args.tokenWantArg)], 'quickswap')
    b=fromA2BStatic(contracts[str(args.fromTokenArg)], contracts[str(args.tokenWantArg)], 'sushiswap')
    table = [["quickswap",a['inputExchangeRateAmt'],a['outputExchangeRateAmt'], a['inputTokenAmount'], a['outputTokenAmount']], ["sushiswap",b['inputExchangeRateAmt'],b['outputExchangeRateAmt'], b['inputTokenAmount'], b['outputTokenAmount']]]
    print()
    print(tabulate(table, headers=["Swap",args.fromTokenArg +' 1:1', args.tokenWantArg+' 1:1', 'inputAmt', 'outputAmt']))
    time.sleep(1)

def fromA2BStatic(origin, toToken, router):
    universalRouter = web3.toChecksumAddress(routers[router]) 
    universalRouterCon = web3.eth.contract(address=universalRouter, abi=uniabi)        
    fromToken = web3.toChecksumAddress(origin)
    
    # fromToken = web3.toChecksumAddress(contracts['matic'])
    fromTokenCon = web3.eth.contract(address=fromToken, abi=ERC20_ABI)
    fromTokenName = fromTokenCon.functions.name().call()
    
    # WHAT DO I WANT TO SWAP FOR?
    tokenWant = web3.toChecksumAddress(toToken)
    tokenWantCon = web3.eth.contract(address=tokenWant, abi=ERC20_ABI)
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
    d['inputExchangeRateAmt'] = str(inputExchangeRateAmt)
    d['outputExchangeRateAmt']   = str(outputExchangeRateAmt)
    d['inputTokenAmount']   = str(inputTokenAmount)
    d['outputTokenAmount']   = str(outputTokenAmount)
    return d

def main():
    setupPrint(routerArgg)
    # setupPrint(routers[str(args.routerArg)])
    start=1
    while start:
        # theExchange(routers[str(args.routerArg)])
        theExchange(routerArgg)

if __name__ == "__main__":
    main()