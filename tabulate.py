#!/usr/bin/env python

import optparse
import os

def __line(f='', s=''):
    return '\033['+ f + s + '\033[0m'

def green(s=''):
    return __line('32m', s)


def strip(s=""):
    while s.endswith("/"):
        s = s[:-1]
    return s


def dir_and_opts():
    parser = optparse.OptionParser("usage: %prog /some/directory")
    parser.add_option("--color",
                      dest="color",
                      default=False,
                      action="store_true",
                      help="add color in stdout")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit()

    return strip(args[0]), options


def results(directory="", dummy="files"):
    assert directory

    out = {}

    os.system("find %s | grep txt > %s" % (directory, dummy))
    files = open(dummy)

    for fileName in files:
        fileName = fileName.replace("\n", "")
        var = fileName
        if "yields.txt" in fileName:
            continue

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


def rearraged(s=""):
    fields = s[0].split("_")
    if all([4 <= len(fields),
            fields[0] == "BDT",
            len(fields[1]) == 4,
            fields[1][0] == "H",
            fields[1][3] == "0",
            ]):
        return "_".join(fields[2:] + [fields[1]])
    else:
        return s


def print_formatted(d={}, color=True, nLeft=40):
    masses = range(260, 360, 10)
    h = "analysis".ljust(nLeft) + "   ".join([str(i) for i in sorted(masses)])
    print h
    print "-" * len(h)

    for var, dct in sorted(d.iteritems(), key=rearraged):
        line = var.ljust(nLeft - 3)
        for mass in masses:
            if mass in dct:
                this = "%6.2f" % dct[mass]
                if color and (str(mass) in var):
                    this = green(this)
                line += this
            else:
                line += " " * 6
        print line


if __name__ == "__main__":
    inputDir, opts = dir_and_opts()
    print_formatted(results(inputDir), color=opts.color)
