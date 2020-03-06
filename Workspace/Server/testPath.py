import os
from common import *

if __name__ == '__main__':
    CUR_PATH = os.path.dirname(os.path.abspath(__file__))
    asdf = os.path.join(os.path.dirname(CUR_PATH), 'data')
    print(CONFIG_FILE_PATH)
    print(asdf)
