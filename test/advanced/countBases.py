#!/usr/bin/env python

import os

BASE = os.getenv("FROF_JOB_PARAM")

print(BASE + " = " + str(len([i for i in open("DNA.txt", "r").read() if i == BASE])))

