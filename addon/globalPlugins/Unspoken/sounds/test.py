from camlorn_audio import *
from glob import *
import random
import pdb

init_camlorn_audio()

list = glob('*.wav')
random.shuffle(list)
x = dict()
for i in list:
 x[i] = Sound3D(i)
 if x[i].get_length() <= 0:
  ptb.set_trace()
