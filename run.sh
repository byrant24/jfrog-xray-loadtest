#!/bin/bash
locust -f locustfile.py --headless -u 10 -r 2 -t 1m --csv=reports/report
