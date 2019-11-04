#!/usr/bin/env python

import os

BASE = os.getenv("FROF_JOB_PARAM")
PLAN_ID = os.getenv("FROF_PLAN_ID")

print(
    BASE
    + " = "
    + str(len([i for i in open(PLAN_ID + "-DNA.txt", "r").read() if i == BASE]))
)

