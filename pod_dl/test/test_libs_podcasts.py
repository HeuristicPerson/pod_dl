import unittest

import libs.podcasts as podcasts


class TestLibsPodcasts(unittest.TestCase):
    def test_process_file(self):
        u_input_file = '../test_data/2021-08-27 - Tocar 2.mp3'
        podcasts._process_file(u_input_file)
        self.assertTrue(True)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()