#!/usr/bin/python2.7

import cv, pickle

def process(key, trackbars, filename):
    if key==1048603 or key==1048689: #escape, q(uit)
        print "Quitting"
        exit()
    elif key==1048680: #h(elp)
        print "Help: commands are h(elp), q(uit), s(ave), l(oad), and p(rint)\n"
    elif key==1048691: #s(ave)
        print "Enter a filename, or press enter to accept the default"
        s = raw_input("<{0}>: ".format(filename))
        if s == "":
            s = filename
        d = {}
        for t in trackbars:
            d[t[0]] = (t[0], t[1], cv.GetTrackbarPos(t[0], t[1]))
        f = open(s, "wb")
        pickle.dump(d, f)
        f.close()
        print "Saved to %s\n" % s
    elif key==1048684: #l(oad)
        print "Enter a filename, or press enter to accept the default"
        s = raw_input("<{0}>: ".format(filename))
        if s == "":
            s = filename
        f = open(s, "rb")
        d = pickle.load(f)
        f.close()
        for k in d:
            name, window, pos = d[k]
            cv.SetTrackbarPos(name, window, pos)
        print "Loaded from %s\n" % s
    elif key==1048688: #p(rint)
        print "Current variables:"
        for t in trackbars:
            print "%s = %s" % (t[0], cv.GetTrackbarPos(t[0], t[1]))
        print "Done (%d variables total)\n" % len(trackbars)

