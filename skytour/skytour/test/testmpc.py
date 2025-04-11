import pandas as pd
from skyfield.api import load
from skyfield.data import mpc

MPCFILE = 'data/MPCORB.DAT'

def locate_asteroid_row(name):
    columns = [('designation', (166, 194)), ]
    names, colspecs = zip(*columns)
    with load.open(MPCFILE) as f:
        mps = mpc.load_mpcorb_dataframe(f)
    mps = mps.set_index('designation', drop=False)
    mps['rowno'] = range(len(mps))
    try:
       row = mps.loc[name]
       print("FOUND ROW: ", row)
    except:
       row = None


def lookup_asteroid_object(name):
   with load.open('data/MPCORB.DAT') as f:
      mps = mpc.load_mpcorb_dataframe(f)
   mps = mps.set_index('designation', drop=False)
   try:
      row = mps.loc[name]
   except:
      return None   
   return row