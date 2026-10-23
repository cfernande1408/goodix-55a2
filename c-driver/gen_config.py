#!/usr/bin/env python3
"""Genera gx55a2_config.c desde config_win.hex. Uso: gen_config.py in.hex out.c"""
import sys
data = bytes.fromhex(open(sys.argv[1]).read().split('#')[0].strip())
with open(sys.argv[2], 'w') as f:
    f.write('#include "goodix_55a2.h"\n')
    f.write('const uint8_t gx55a2_device_config[%d] = {\n' % len(data))
    for i in range(0, len(data), 12):
        f.write('  ' + ','.join('0x%02x' % b for b in data[i:i+12]) + ',\n')
    f.write('};\n')
