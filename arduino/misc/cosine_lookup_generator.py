from math import *

#print "{",
for n in range(256):
  print "case " + str(n) + ": return "  + str(int(cos((n/256.0)*2*pi)*32767)) + ";"

#print "};"