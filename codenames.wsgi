#!/usr/bin/env python3

import sys

sys.path.insert(0, "/var/www/wsgi-scripts/codenames/")

from main import app as application

application.root_path = "/var/www/wsgi-scripts/codenames/"
