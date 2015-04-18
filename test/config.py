# -*- coding: utf-8 -*-
"""
test.config
~~~~~~~~~~~

Sample config for running tests on the package.

:license: MIT and BSD
"""

import os

DATABASE_URI = 'sqlite:///:memory:'

test_dir = os.path.dirname(__file__)
DATA_PATH = os.path.join(test_dir, 'data')
