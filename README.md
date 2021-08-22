# dexra

Web3 CLI tool for tracking the exchange rate of 2 crytocurrencies on Polygon via Quickswap and SushiSwap

# Setup
- Download the repository
- In the repository directory create an ```.env``` file and add the following information:
  
  ``` 
    INFURA_ADDRESS_POLYGON=your_infura_polygon_address
    MAINNET_POLYGON=https://rpc-mainnet.matic.network
  ```

- Next, create a new Python virtual environment using ```virtualenv```
  
  ``` virtualenv venv```

- Activate the virtual environment
  
  ``` source venv/bin/activate```

- Install the project requirements
  
  ``` python3 install -r requirements.txt```

- Start it up!

# CLI Overview

## Execution

```python3 dexra.py --fromToken STRING --tokenWant STRING --amt INT```

# Requirements
- Python3
- virtualenv

(program requirements can be found in ```requirements.txt```)

## CLI Arguments
- ```dexra.py```    | The Python3 CLI program
- ```--fromToken``` | (string) The token the user owns and would like to exchange
- ```--tokenWant``` | (string) The token the user wants in exchange for what they are offering
- ```--amt```       | The total amount being exchanged

# Example

## Command
```python3 dexra.py --fromToken matic --tokenWant dai --amt 10```

## Output
```
____________________
               dexra
             POLYGON
____________________
Swap         matic 1:1    dai 1:1    inputAmt    outputAmt
---------  -----------  ---------  ----------  -----------
quickswap            1    1.58933          10      15.8917
sushiswap            1    1.58299          10      15.5675
```

# Dex Information

## Exchanges
```
{
    "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
    "sushiswap": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"
}
```

## Contracts
```
{
    "matic": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
    "dai": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    "aave": "0xd6df932a45c0f255f85145f286ea0b292b21c90b",
    "uniswap": "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
    "curve": "0x172370d5cd63279efa6d502dab29171933a610af",
    "wbtc": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
    "curve": "0x172370d5cd63279efa6d502dab29171933a610af",
    "sushi": "0x0b3f868e0be5597d5db7feb59e1cadbb0fdda50a",
    "must": "0x9C78EE466D6Cb57A4d01Fd887D2b5dFb2D46288f"
}
```

# Future
- Clean up Ethereum example
- Made more modular, easier to check multiple blockchains
- Research other blockchain integration
