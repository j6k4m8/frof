#!/usr/bin/env python

import random

print("".join(random.choice("ATGC") for _ in range(100)))
