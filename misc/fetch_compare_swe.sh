#!/bin/bash

python3 /home/jehayes/sh_final/SWEet-InSAR/misc/cslc_download.py

sleep 2

python3 /home/jehayes/sh_final/SWEet-InSAR/misc/ifg_swe_comp.py
