Place for collaborating on backtesting scripts

### instructions for alpaca backtrader scripts:
- Setup Alpaca premium account
- Get your API token
- In a new python virtual environment (or your preferred existing one) use pip3 to install the required dependencies: 
  - ```pip3 install -r requirements.txt```

- In terminal, navigate to the directory with this file.
- In the file "alpaca_test_strategy.py", substitute in your own Alpaca creds for the following variables:
  - ALPACA_API_KEY = ""
  - ALPACA_SECRET_KEY = ""
  - ALPACA_PAPER = True ( Keep this 'True' so you're only trading in your paper account, not your live account )
- To test the current strategy, run ```python3 ./alpaca-test-strategy.py``` from this directory in terminal

