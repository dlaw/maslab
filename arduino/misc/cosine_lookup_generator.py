from math import *

#print "{",
for n in range(4096):
  print str(int(cos((n/4096.0)*2*pi)*32767)) + ","

#print "};"