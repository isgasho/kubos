#!/usr/bin/env python
# encoding: utf-8

import os

APPNAME = 'libcsp'
VERSION = '1.0'

top = '.'
out = 'build'

def options(ctx):
    # Load GCC options
    ctx.load('gcc')
    # Set CSP options
    ctx.add_option('--toolchain', default='', help='Set toolchain prefix')
    ctx.add_option('--conf-kernel', default=None, help='Set configuration file')
    ctx.add_option('--os', default='posix', help='Set operating system. Must be either \'posix\' or \'freertos\'')
    ctx.add_option('--cflags', default='', help='Add additional CFLAGS. Separate with comma')
    ctx.add_option('--includes', default='', help='Add additional include paths. Separate with comma')
    ctx.add_option('--with-can', default=None, metavar='CHIP', help='Enable CAN driver. CHIP must be either socketcan, at91sam7a1, at91sam7a3 or at90can128')
    ctx.add_option('--with-freertos', default='../../libgomspace/include', help='Set path to FreeRTOS header files')

def configure(ctx):
    # Validate.os
    if not ctx.options.os in ('posix', 'freertos'):
        ctx.fatal('ARCH must be either \'posix\' or \'freertos\'')

    # Validate CAN drivers
    if not ctx.options.with_can in (None, 'socketcan', 'at91sam7a1', 'at91sam7a3', 'at90can128'):
        ctx.fatal('CAN must be either \'socketcan\', \'at91sam7a1\', \'at91sam7a3\', \'at90can128\'')

    # Setup and validate toolchain
    ctx.env.CC = ctx.options.toolchain + 'gcc'
    ctx.env.AR = ctx.options.toolchain + 'ar'
    ctx.load('gcc')

    # Add default files
    ctx.env.append_unique('FILES_CSP', ['src/*.c','src/crypto/*.c','src/interfaces/csp_if_lo.c','src/transport/*.c','src/{0}/**/*.c'.format(ctx.options.os)])

    # Add FreeRTOS 
    if ctx.options.os == 'freertos':
        ctx.env.append_unique('INCLUDES_CSP', ctx.options.with_freertos)

    # Add CAN driver
    if ctx.options.with_can:
        ctx.env.append_unique('FILES_CSP', 'src/interfaces/csp_if_can.c')
        ctx.env.append_unique('FILES_CSP', 'src/interfaces/can/can_{0}.c'.format(ctx.options.with_can))

    if ctx.options.conf_kernel:
        ctx.define('CONF_KERNEL', os.path.abspath(ctx.options.conf_kernel))

def build(ctx):
    ctx.stlib(source=ctx.path.ant_glob(ctx.env.FILES_CSP),
              target='csp',
              includes='include',
              export_includes='include', 
              use='CSP',
              cflags = ['-Os','-Wall', '-g'] + ctx.options.cflags.split(','))
