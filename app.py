# -*- coding: utf-8 -*-
import logging
from backtrader_minimal_test import backtrader_minimal_test


# LOG = logging.getLogger()
# LOG.setLevel(logging.DEBUG)




def handler(event, context):

    # initiate whatever function you need here
    print('Made it to handler function of app.py file..')
    backtrader_minimal_test()
    # assert context
    # LOG.debug(event)
    # comment this out during testing. keep it in during deploying
    return {'status': 'success'}



# un comment to run tests, run: "python3 ./_src/app.py" from the terminal at the root directory of this project
# if __name__ == '__main__':
#     handler('event', 'context')
