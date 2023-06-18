#!/usr/bin/env python3

import libs.constants as constants
import libs.podcasts as podcasts
import libs.subs as subs


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    if constants.b_DEBUG:
        u_prog_and_ver = '%s - %s' % (constants.s_PRG, constants.s_VER)
        print('%s\n%s' % (u_prog_and_ver, '=' * len(u_prog_and_ver)))
        constants.print_constants()

    lo_subs = subs.read_subs(constants.u_SUBS)

    b_any_dl = False
    for o_pod in lo_subs:
        o_pod.read_feed()
        b_pod_dl = o_pod.dl_episodes()
        if b_pod_dl:
            b_any_dl = True

    # Building the .m3u playlist with all episodes
    podcasts.build_playlist(b_any_dl)
