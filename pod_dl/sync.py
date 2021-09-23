#!/usr/bin/env python3

import libs.constants as constants
import libs.subs as subs

# Constants
#=======================================================================================================================
u_TEST_FEED = 'https://www.spreaker.com/show/1432098/episodes/feed'


# Classes
#=======================================================================================================================


# Helper functions
#=======================================================================================================================


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    if constants.b_DEBUG:
        u_prog_and_ver = '%s - %s' % (constants.u_PRG, constants.u_VER)
        print('%s\n%s' % (u_prog_and_ver, '=' * len(constants.u_PRG)))
        constants.print_constants()

    lo_subs = subs.read_subs(constants.u_SUBS)

    for o_pod in lo_subs:
        o_pod.read_feed()
        o_pod.dl_episodes()
