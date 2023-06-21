#!/usr/bin/env python3

### --------------------------------------------- ###
### Part of iViz                                  ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)           ###
### Creative Commons                              ###
### Attribution-NonCommercial-NoDerivatives       ###
### 4.0 International License.                    ###
### Commercial use an redistribution prohibited.  ###
### See https://github.com/eddy-ilg/iviz          ###
### --------------------------------------------- ###

def print_qtransform(m):
    print('type', m.type())
    print('%7.3f %7.3f %7.3f' % (m.m11(), m.m12(), m.m13()))
    print('%7.3f %7.3f %7.3f' % (m.m21(), m.m22(), m.m23()))
    print('%7.3f %7.3f %7.3f' % (m.m31(), m.m32(), m.m33()))
