import sys
import os
cur_dir = os.path.dirname(os.path.realpath(__file__))
par_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
print(par_dir)
sys.path.append(par_dir)
print(__path__)