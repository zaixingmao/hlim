#!/usr/bin/env python

import optparse
import os

def __line(f='', s=''):
    return '\033['+ f + s + '\033[0m'

def green(s=''):
    return __line('32m', s)


def dir_and_opts():
    parser = optparse.OptionParser("usage: %prog /some/directory")
    parser.add_option("--no-color",
                      dest="noColor",
                      default=False,
                      action="store_true",
                      help="disable color in stdout")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit()

    return args[0], options


def results(directory="", dummy="files"):
    assert directory

    out = {}

    os.system("find %s | grep txt > %s" % (directory, dummy))
    files = open(dummy)

    for fileName in files:
        fileName = fileName.replace("\n", "")
        var = fileName
        for item in ["tt_ggHTohh-limit.txt", "%s/" % directory, "/"]:
            var = var.replace(item, "")

        f = open(fileName)
        for iLine, line in enumerate(f):
            fields = line.split()
            if len(fields) <= 3:
                print "skpping line %d of %s" % (1 + iLine, fileName)
                continue
            elif fields[0] == "#":
                continue
            else:
                if var not in out:
                    out[var] = {}

                x = int(fields[0])
                limit = float(fields[3])
                out[var][x] = limit
        f.close()

    files.close()
    os.remove(dummy)
    return out


def print_formatted(d={}, color=True, nLeft=40):
    masses = [dct.keys() for dct in d.values()][0]  # take first
    h = "analysis".ljust(nLeft) + "   ".join([str(i) for i in sorted(masses)])
    print h
    print "-" * len(h)

    for var, dct in sorted(d.iteritems()):
        line = var.ljust(nLeft - 3)
        for mass, limit in sorted(dct.iteritems()):
            this = "%6.2f" % limit
            if color and (str(mass) in var):
                this = green(this)
            line += this
        print line


if __name__ == "__main__":
    inputDir, opts = dir_and_opts()
    print_formatted(results(inputDir), color=not opts.noColor)
