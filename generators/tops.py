import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import db_handler

def iter0alphas():
    for line in open('iter0alphas'):
        yield line

def uncorr_top():
    db = db_handler.DBHandler()
    return list(db.iterate_over_top_alpha('top_for_generators'))

