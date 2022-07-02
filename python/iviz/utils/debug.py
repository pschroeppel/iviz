#!/usr/bin/env python3


def print_qtransform(m):
    print('type', m.type())
    print('%7.3f %7.3f %7.3f' % (m.m11(), m.m12(), m.m13()))
    print('%7.3f %7.3f %7.3f' % (m.m21(), m.m22(), m.m23()))
    print('%7.3f %7.3f %7.3f' % (m.m31(), m.m32(), m.m33()))
