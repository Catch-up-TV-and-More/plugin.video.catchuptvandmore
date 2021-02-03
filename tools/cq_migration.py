#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2016-2020 Team Catch-up TV & More
    This file is part of Catch-up TV & More.
    SPDX-License-Identifier: GPL-2.0-or-later
"""

import sys

filepath = sys.argv[1]

print('Work on %s file' % filepath)

lines = []

with open(filepath, "r") as f:
    for line in f:
        lines.append(line)

new_lines = []

modules = []
for i in range(len(lines)):
    add_line = True
    if "'callback':" in lines[i]:
        lines[i] = lines[i].replace("'callback':", "'resolver':")

    if "'module':" in lines[i]:
        module = lines[i].split("module': '")[1].split("',")[0]
        module = module.replace('.', '/')
        modules.append(module)
        add_line = False

    if add_line:
        new_lines.append(lines[i])

cnt = 0
for i in range(len(new_lines)):
    add_line = True
    if "'resolver':" in new_lines[i]:
        new_lines[i] = new_lines[i].replace("live_bridge", '/' + modules[cnt] + ':get_live_url')
        cnt = cnt + 1

with open(filepath, 'w') as f:
    for line in new_lines:
        f.write(line)
