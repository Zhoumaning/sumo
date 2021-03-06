#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2019 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    rebuildConstants.py
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @date    2009-07-24
# @version $Id$

"""
This script extracts definitions from <SUMO>/src/libsumo/TraCIConstants.h
 and builds an according constants definition python file "constants.py".
 For Python just call the script without options, for Java:
 tools/traci/rebuildConstants.py -j de.tudresden.sumo.config.Constants
  -o tools/contributed/traas/src/de/tudresden/sumo/config/Constants.java
"""

from __future__ import print_function
from __future__ import absolute_import
import os
import datetime
import argparse
import re

dirname = os.path.dirname(__file__)
argParser = argparse.ArgumentParser()
argParser.add_argument("-j", "--java",
                       help="generate Java output as static members of the given class", metavar="CLASS")
argParser.add_argument("-o", "--output", default=os.path.join(dirname, "constants.py"),
                       help="File to save constants into", metavar="FILE")
options = argParser.parse_args()


fdo = open(options.output, "w")
if options.java:
    print("/**", file=fdo)
print("""# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2019 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    %s
# @author  generated by "%s"
# @date    %s
# @version $Id$

\"\"\"
This script contains TraCI constant definitions from <SUMO_HOME>/src/libsumo/TraCIConstants.h.\
""" % (os.path.basename(options.output), os.path.basename(__file__), datetime.datetime.now()), file=fdo)

if options.java:
    print("*/\n", file=fdo)
    className = options.java
    if "." in className:
        package, className = className.rsplit(".", 1)
        fdo.write("package %s;\n" % package)
    fdo.write("public class %s {" % className)
else:
    print('"""\n', file=fdo)


def translateFile(filePath, fdo, start, item, end, item_parser):
    comment_marker = "//" if options.java else "#"
    with open(filePath) as fdi:
        started = False
        for line in fdi:
            if started:
                line = line.strip()
                if line.find(end) >= 0:
                    started = False
                    continue
                if options.java:
                    line = line.replace("//", "    //")
                else:
                    line = line.replace("///", "#").lstrip(" ")
                    line = line.replace("//", "# ").lstrip(" ")
                if line.find(item) >= 0 and comment_marker not in line:
                    (ctype, cname, cvalue) = item_parser(line)
                    if options.java:
                        line = "    public static final {} {} = {};".format(ctype, cname, cvalue)
                    else:
                        line = "{} = {}".format(cname, cvalue)

                print(line, file=fdo)
            if line.find(start) >= 0:
                started = True


def parseTraciConstant(line):
    match = re.search('(\S+) ([A-Z0-9_]+) = (\S+);', line)
    if match:
        return match.group(1, 2, 3)
    else:
        return None


def parseLaneChangeAction(line):
    line = line.rstrip(',')
    match = re.search('([A-Z0-9_]+) = (.+)', line)
    if match:
        return ('int', match.group(1), match.group(2))
    else:
        return None


srcDir = os.path.join(dirname, "..", "..", "src")
translateFile(os.path.join(srcDir, "libsumo", "TraCIConstants.h"),
              fdo, "namespace libsumo {", "TRACI_CONST ", "} // namespace libsumo", parseTraciConstant)

translateFile(os.path.join(srcDir, "utils", "xml", "SUMOXMLDefinitions.h"),
              fdo, "enum LaneChangeAction {", "LCA_", "};", parseLaneChangeAction)
if options.java:
    fdo.write("}")
fdo.close()
