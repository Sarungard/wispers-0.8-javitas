import os
import sys

import tsim

tsim.configure(int(os.environ.get('TURN', tsim.BOOK_TURN)))
sys.modules[__name__] = tsim.sim
