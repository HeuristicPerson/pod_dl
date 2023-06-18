import datetime
import os
import unittest

import libs.constants as constants
import libs.files as files
import libs.podcasts as podcasts


@unittest.skip
class TestLibsPodcasts(unittest.TestCase):
    def test_process_file(self):
        u_input_file = 'test_data/2021-08-27 - Tocar 2.mp3'
        podcasts._process_file(u_input_file)
        self.assertTrue(True)


# Tests for the Episode class
#-----------------------------------------------------------------------------------------------------------------------
class TestLibsPodcastsClassEpisode(unittest.TestCase):
    """
    Class for the Episode class of podcasts library.
    """
    def test_fix_tags_unknown(self):
        # Creating and populating an episode instance
        #--------------------------------------------
        o_episode = podcasts.Episode()
        o_episode.u_title = 'Problematic Episode'
        o_episode.o_date_pub = datetime.datetime.now()
        o_episode.u_author = 'Topal Games'
        o_episode.u_url = 'http://foo.bar/this_file.mp4'

        #
        o_local_file = files.FilePath(constants.s_TEST_DATA_ROOT,
                                      'topalgamesplaystationshowcasezeldat-topalgamespodcast-ivoox109667718.mpga')

        # --- test code ---
        print(o_episode)
        # ------ end ------

        # Testing the fixing of tags
        #---------------------------
        o_episode.fix_tags(po_file=o_local_file,
                           po_podcast=None)


        self.assertEqual(True, False)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
