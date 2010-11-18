#!/bin/bash

produceMISOInput2.py --out-dir MISO_input *.exinc.xls
produceMISOInput2.py --add-readlength 36 --out-dir MISO_input_wrl *.exinc.xls

