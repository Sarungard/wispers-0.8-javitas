import os
import sys

import h66sim

options = os.environ.get('H66', '').split(',')
h66sim.configure(stop_light_escalation='p2' in options,
                 deadly={o[len('deadly='):] for o in options if o.startswith('deadly=')})
sys.modules[__name__] = h66sim.sim
