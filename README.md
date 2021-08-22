# dexra

Web3 CLI tool for tracking the exchange rate of 2 crytocurrencies on Polygon via Quickswap and SushiSwap


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

# Future
- Clean up Ethereum example
- Made more modular, easier to check multiple blockchains
- Research other blockchain integration
