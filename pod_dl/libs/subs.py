import codecs

from . import podcasts


def read_subs(pu_file):
    """
    Function to read the subscriptions from a file.
    :param pu_file: Path of the file with subscriptions
    :type pu_file: unicode

    :return: List of podcast subscriptions
    :rtype list[podcasts.Podcast]
    """
    lo_subs = []

    try:
        with codecs.open(pu_file, 'r', 'utf8') as o_file:
            for u_line in o_file:
                u_line = u_line.strip()
                if u_line and not u_line.startswith('#'):
                    u_title, _, u_url = u_line.partition(';')

                    o_podcast = podcasts.Podcast()
                    o_podcast.u_name = u_title
                    o_podcast.u_feed = u_url

                    lo_subs.append(o_podcast)

    except FileNotFoundError:
        pass

    return lo_subs