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



### Building environments with pip and venv (virtual environment)
then also install those dependencies into the default location of your 
```sudo apt-get install python3-venv
```python3 -m venv my_new_venv
source ./venv_backtrader_zappa/bin/activate (where venv_backtrader is your virtual env name)
pip3 install -r requirements.txt
```

helpful pip3 command to install specific version of an app:
```
pip3 install 'xkcdpass==1.2.5' --force-reinstall
```

to export packages of a current virtual env:
```pip3 freeze > requirements.txt```
then take that requirements.txt file and re-install all those packages into a new virtual env with a specific argument to save them into a kappa-supported directory via:



this shouldnt be necessary
```
pip3 install --target=./_src/venv_backtrader_kappa/lib/python3.8/site-packages -r requirements.txt 
```


# un comment to run tests, run: "python3 ./_src/app.py" from the terminal at the root directory of this project


where the long path is the path to the root folder of your project
this will install all the versions


### packages that were accidentally uninstalled:
```
WARNING: Skipping alpaca-backtrader-api as it is not installed.
WARNING: Skipping alpaca-trade-api as it is not installed.
WARNING: Skipping backtrader as it is not installed.
Found existing installation: certifi 2019.11.28
Not uninstalling certifi at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'certifi'. No files were found to uninstall.
Found existing installation: chardet 3.0.4
Not uninstalling chardet at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'chardet'. No files were found to uninstall.
WARNING: Skipping cycler as it is not installed.
Found existing installation: idna 2.8
Not uninstalling idna at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'idna'. No files were found to uninstall.
WARNING: Skipping kiwisolver as it is not installed.
WARNING: Skipping matplotlib as it is not installed.
WARNING: Skipping numpy as it is not installed.
WARNING: Skipping pandas as it is not installed.
Found existing installation: Pillow 7.0.0
Not uninstalling pillow at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'Pillow'. No files were found to uninstall.
WARNING: Skipping pyparsing as it is not installed.
Found existing installation: python-dateutil 2.7.3
Not uninstalling python-dateutil at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'python-dateutil'. No files were found to uninstall.
WARNING: Skipping python-decouple as it is not installed.
Found existing installation: pytz 2019.3
Not uninstalling pytz at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'pytz'. No files were found to uninstall.
Found existing installation: requests 2.22.0
Not uninstalling requests at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'requests'. No files were found to uninstall.
Found existing installation: six 1.14.0
Not uninstalling six at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'six'. No files were found to uninstall.
WARNING: Skipping toolz as it is not installed.
WARNING: Skipping trading-calendars as it is not installed.
Found existing installation: urllib3 1.25.8
Not uninstalling urllib3 at /usr/lib/python3/dist-packages, outside environment /usr
Can't uninstall 'urllib3'. No files were found to uninstall.
WARNING: Skipping websocket-client as it is not installed.
WARNING: Skipping websockets as it is not installed.
```
