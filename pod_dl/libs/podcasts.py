import copy
import datetime
import html
import io
import logging
import time

import urllib.error
from urllib.request import urlopen
import urllib.request as request
import urllib.parse
import lxml.etree
import eyed3
import youtube_dl

from . import constants
from . import files
from . import post_script
from . import shell
from . import timestamps


# Classes
#=======================================================================================================================
class Podcast(object):
    """
    :ivar u_name: unicode
    :ivar u_feed: unicode
    :ivar lo_eps: list[Episode]
    :ivar _o_post_script: Union[None, post_script.PostScript]
    """
    def __init__(self):
        self.u_name = ''            # Name of the podcast
        self.u_feed = ''            # URL of the feed
        self.lo_eps = []            # List with episode objects

        self._o_post_script = None  # PostScript with action to be performed after the download of episodes

    def __str__(self):
        u_out = '<Podcast>\n'
        u_out += '  .u_name: %s\n' % self.u_name
        u_out += '  .u_feed:  %s\n' % self.u_feed

        if not self.lo_eps:
            u_out += '  .lo_eps:\n'
        else:
            for i_episode, o_episode in enumerate(self.lo_eps):
                if i_episode == 0:
                    u_out += '  .lo_eps:  %s\n' % o_episode.str_oneline()
                else:
                    u_out += '            %s\n' % o_episode.str_oneline()
        return u_out

    def read_feed(self):
        """
        Method to read a feed and populate the episodes of the Podcast.

        :return: Nothing
        """
        # TODO: If any problem is found when parsing the feeds, print the error and jump to the next feed.

        # First we try to read the episodes contained in a regular podcast feed (containing .mp3 episodes and so on).
        self.read_feed_podcast()
        self.read_feed_youtube()

    def read_feed_youtube(self):
        """
        Method to identify all the episodes (videos) included in a channel rss feed.
        :return: Nothing
        """
        for i_try in range(constants.i_DL_RETRIES):
            try:
                o_file = urlopen(self.u_feed)
                o_parser = lxml.etree.XMLParser(recover=True)
                x_root = lxml.etree.fromstring(text=o_file.read(),
                                               parser=o_parser)

                x_root = _remove_namespaces_qname(x_root)

                lo_elems = x_root.findall('entry')
                for o_elem in lo_elems:
                    o_episode = Episode(po_xml=o_elem)
                    self.lo_eps.append(o_episode)

                break

            # TODO: Be more specific with the except similarly to what we do with podcast feeds
            except:
                pass

    def read_feed_podcast(self):
        """
        Method to identify all the episodes included in a podcast rss feed.
        :return: Nothing
        """
        for i_try in range(constants.i_DL_RETRIES):
            try:
                o_file = urlopen(self.u_feed)
                o_parser = lxml.etree.XMLParser(recover=True)
                x_root = lxml.etree.fromstring(text=o_file.read(),
                                               parser=o_parser)

                for o_elem in x_root.findall('channel/item'):
                    o_episode = Episode(po_xml=o_elem)
                    self.lo_eps.append(o_episode)

                # Some podcasts put the latest episodes at the end of the feed while others put them at the beginning,
                # so we will sort the list of episodes by date, keeping the newest ones at the beginning.
                self.lo_eps.sort(key=lambda o_ep: o_ep.o_date_pub, reverse=True)

                break

            # If the feed didn't download properly
            except urllib.error.URLError:
                time.sleep(constants.i_DL_RETRY_DELAY)

            # If any of the entries in the feed didn't contain all required data
            except FeedFormatError:
                time.sleep(constants.i_DL_RETRY_DELAY)

        # This code below is only reached when the for loop is completed => the max number of tries was reached
        # without success.
        else:
            u_msg = ''
            u_msg += 'Error reading feed for podcast "%s":\n' % self.u_name
            u_msg += '  %s' % self.u_feed
            print(u_msg)

    def dl_episodes(self):
        """
        Method to download episodes of the podcast

        :return: True if at least one episode was downloaded
        :rtype bool
        """

        b_eps_dl = False

        o_last_update = timestamps.read_timestamp(self._get_o_timestamp())

        # Obtaining filtered list of episodes by date and limiting by desired number
        lo_eps_to_dl = self._filter_episodes(po_after=o_last_update)
        lo_eps_to_dl = lo_eps_to_dl[:constants.i_MAX_SYNC]

        # Because the way we save the timestamps after EACH episode is downloaded (to avoid downloaded it again), we
        # must download episodes starting from the oldest one; otherwise, any failure after downloading the first
        # episode (the latest) will make impossible to re-download the previous ones.
        lo_eps_to_dl = lo_eps_to_dl[::-1]

        if lo_eps_to_dl or constants.b_DEBUG:
            # Text for maximum number of podcasts to download
            if constants.i_MAX_SYNC == 0:
                u_max = 'all available'
            else:
                u_max = '%s latest' % constants.i_MAX_SYNC

            # Text for starting date
            if o_last_update is None:
                u_since = ''
            else:
                u_since = 'since %s' % o_last_update

            print('- %s' % self.u_name)
            print('  - Downloading %s episode(s) %s' % (u_max, u_since))

        # Process for each episode
        #-------------------------
        # TODO: Retry the downloading of any file a couple of times, and if any of them fail, stop the process so we
        # can continue the download the next time.
        for i_eps, o_eps in enumerate(lo_eps_to_dl, start=1):
            u_msg = '  - [%i/%i] %s %s...' % (i_eps,
                                              len(lo_eps_to_dl),
                                              o_eps.o_date_pub.strftime('%Y-%m-%d'),
                                              o_eps.u_title)

            # [1/?] Downloading of the episode
            print(u_msg, end=' ')
            o_local_file = o_eps.download(self._tmp_dir())

            if o_local_file is None:
                u_msg = 'ERROR! file couldn\'t be downloaded, interrupting process for this podcast'
                print(u_msg)
                break
            else:
                u_msg = 'DONE! (%s)' % o_local_file.u_size
                print(u_msg)

            # [2/?] Fixing ID3 tags of the episode
            # TODO: Not sure if process should be a method of podcasts or episodes. For example, if I wanted to use the
            # podcast cover as the audio file cover in case it doesn't contain any, it should be a Pocast method. So,
            # that seems to be the way to go in the long term.
            print('    - Fixing ID3 tags...', end=' ')
            o_eps.fix_tags(o_local_file, po_podcast=self)
            print('DONE!')

            # [2/?] Transcoding of the episode
            if constants.b_TRANSC_SERV:
                u_msg = '    - Transcoding to .ogg at %s Hz and %s kbps...' % (constants.i_TRANSC_FREQ,
                                                                               constants.i_TRANSC_BITR)
                print(u_msg, end=' ')
                o_local_file_trans = _transcode_file(o_local_file,
                                                     pi_freq=constants.i_TRANSC_FREQ,
                                                     pi_bitrate=constants.i_TRANSC_BITR)
                print('DONE! (%s)' % o_local_file_trans.u_size)

                # keeping smallest version (respecting force transcode option)
                # TODO: Make code below robust by checking every operation was successful
                o_keep_file, o_del_file = _identify_smallest_episode(o_local_file, o_local_file_trans)
                if o_keep_file == o_local_file:
                    u_keep = 'original'
                else:
                    u_keep = 'transcoded'

                u_msg = '    - Keeping %s file' % u_keep
                print(u_msg, end=' ')

                shell.cmd_run(('rm', '-f', o_del_file.u_path))
                o_local_file = o_keep_file
                print('DONE!')

            # [3/?] Moving the file to the final archive location
            print('    - Moving file to archive location...', end=' ')
            shell.cmd_run(('mkdir', self._arc_dir().u_path))
            shell.cmd_run(('mv', o_local_file.u_path, self._arc_dir().u_path))
            timestamps.save_timestamp(self._get_o_timestamp(), o_eps.o_date_pub)
            b_eps_dl = True
            print('DONE!')

            # [3/?] Run post script
            o_final_destination = files.FilePath(self._arc_dir().u_path, o_local_file.u_file)
            self._build_post_script(o_eps, o_final_destination)
            if self._o_post_script is not None:
                print('    - %s...' % self._o_post_script.u_msg, end=' ')

                b_success = self._o_post_script.run()
                du_success = {False: 'ERROR!',
                              True: 'DONE!'}
                print(du_success[b_success])

        self._tidy_up_archive()

        return b_eps_dl

    def _filter_episodes(self, po_after=None):
        """
        Method to filter out episodes before a specific date (including it).

        :param po_after:
        :type po_after: datetime.datetime.Datetime

        :return: A list of episodes within the given datetime range.
        :rtype List[Episode]
        """
        lo_eps_within = []

        for o_eps in self.lo_eps:
            b_include = True
            if (po_after is not None) and o_eps.o_date_pub <= po_after:
                b_include = False

            if b_include:
                lo_eps_within.append(o_eps)

        return lo_eps_within

    @staticmethod
    def _tmp_dir():
        """
        Method to build the temporary directory to download episodes

        :return: The filepath of the temporary download directory
        :rtype files.FilePath
        """
        o_dir = files.FilePath(constants.u_TMP_DIR)
        return o_dir

    def _arc_dir(self):
        """
        Method to build the FilePath of the archive directory to store episodes.

        :return: The filepathpath of the final archive directory
        :rtype files.FilePath
        """
        o_dir = files.FilePath(constants.u_ARC_DIR, self.u_name)
        return o_dir

    def _get_o_timestamp(self):
        """
        Method to return the FilePath object of the timestamp file; a file that contains the date of the last episode
        fully downloaded (downloaded and processed) so it won't be downloaded again in the future.

        :return:
        :rtype files.FilePath
        """
        o_tms_file = files.FilePath(self._arc_dir().u_path, 'last_download.txt')
        return o_tms_file

    def _build_post_script(self, po_episode, po_file):
        """
        Method to run the post script.

        :param po_episode: Episode to run the post-script for
        :type po_episode: Episode

        :param po_file: Actual file archived
        :type po_file: files.FilePath

        :return: Nothing
        """
        # Preparing the post-script object
        o_post_scr = post_script.PostScript()
        o_post_scr.u_pod_name = self.u_name
        o_post_scr.u_ep_title = po_episode.u_title
        o_post_scr.u_ep_hsize = po_file.u_size
        o_post_scr.u_ep_isize = '%s' % po_file.i_size
        # TODO: final file can be an .ogg and eyed3 is not compatible. We can get duration from po_episode if we parsed
        # the non standard itunes duration tag from the feed
        o_post_scr.u_ep_durat = '00:00:00'
        o_post_scr.u_ep_path = po_file.u_path
        if constants.u_POST_SCR_MSG:
            o_post_scr.u_msg_tpl = constants.u_POST_SCR_MSG
        else:
            o_post_scr.u_msg_tpl = 'Running post script'
        o_post_scr.tu_cmd_tpl = constants.tu_POST_SCR

        if constants.tu_POST_SCR:
            self._o_post_script = o_post_scr

    def _tidy_up_archive(self):
        """
        Method to tidy up the archive directory limiting the number of episodes stored.

        :return: Nothing
        """
        lo_files = self._arc_dir().listdir(pu_type='f')
        lo_files = [o_file for o_file in lo_files if o_file.has_ext('mp3', 'ogg')]
        # because file name contains the date in iso format, we can sort them alphabetically to get them in
        # chronological order
        lo_files = sorted(lo_files, key=lambda o_file: o_file.u_name, reverse=True)
        lo_files_to_delete = lo_files[constants.i_MAX_ARCH:]

        if lo_files_to_delete:
            print('    - Deleting old episodes:')
            for i_file, o_file in enumerate(lo_files_to_delete, start=1):
                u_msg = '      - [%i/%i] %s' % (i_file, len(lo_files_to_delete), o_file.u_file)
                print(u_msg, end=' ')
                o_result = shell.cmd_run(('rm', '-f', o_file.u_path))

                if o_result.i_rcode == 0:
                    u_msg = 'DONE!'
                else:
                    # TODO: Get return code and indicate errors
                    u_msg = 'ERROR!'

                print(u_msg)


class Episode(object):
    def __init__(self, po_xml=None):
        self.u_title = ''
        self.o_date_pub = None
        self.u_author = ''
        self.u_url = ''

        if po_xml is not None:
            self._parse_xml(po_xml)

    def __str__(self):
        u_out = '<Episode>\n'
        u_out += '  .u_name:      %s\n' % self.u_title
        u_out += '  .u_mod_title: %s\n' % self.u_mod_title
        u_out += '  .u_url:       %s\n' % self.u_url
        u_out += '  .o_date:      %s\n' % self.o_date_pub
        return u_out

    def download(self, po_dir):
        """
        Method to download the episode to a dir.

        :param po_dir: FilePath of the dir where the episode will be downloaded to.
        :type po_dir: files.FilePath

        :return: The local path of the downloaded file.
        :rtype Union[unicode, None]
        """
        u_filename = '%s - %s' % (self.o_date_pub.strftime('%Y-%m-%d'), self.u_title)
        o_local_file = None

        for i_retry in range(constants.i_DL_RETRIES):
            try:
                if self.u_url.startswith('https://www.youtube.com/'):
                    o_local_file = self._download_yt_audio(po_dir, u_filename)
                    break
                else:
                    o_local_file = self._download_file(po_dir, u_filename)
                    break

            # TODO: Remove the debug print once the code is able to ignore common exceptions
            except Exception as o_exception:
                if type(o_exception).__name__ == 'DownloadError':
                    pass
                else:
                    u_msg = 'An exception of type %s occurred. Arguments:\n%s' % (type(o_exception).__name__,
                                                                                  o_exception.args)
                    print(u_msg)

                time.sleep(constants.i_DL_RETRY_DELAY)

        return o_local_file

    def _download_file(self, po_dir, pu_name):
        """
        Method to download a remote file when we have it's full URL. e.g. http://jonh.com/file.mp3

        :param po_dir: Directory where the file should be saved.
        :type po_dir: files.FilePath

        :param pu_name: Local name of the file to be saved
        :type pu_name: Str

        :return The local file FilePath object.
        :rtype files.FilePath
        """
        # Sometimes, the URL doesn't just contain the file name but also some parameters. e.g. ".mp3?d=1646904795" so we
        # need to remove them. I don't know if the dot is a valid character in the URL
        u_clean_url = urllib.parse.urljoin(self.u_url, urllib.parse.urlparse(self.u_url).path)
        u_ext = u_clean_url.rpartition('.')[2]

        # After we get the clean extension, we can download the file
        o_local_file = _dl_file(self.u_url, po_dir, pu_name='%s.%s' % (pu_name, u_ext))
        return o_local_file

    def _download_yt_audio(self, po_dir, pu_name):
        """
        Method to download the audio from a Youtube video to a local file.

        :param po_dir: Directory where the file should be saved.
        :type po_dir: files.FilePath

        :param pu_name: Local name of the file to be saved
        :type pu_name: Str

        :return The local file FilePath object.
        :rtype files.FilePath
        """
        o_local_file = files.FilePath(po_dir.u_path, '%s.mp3' % pu_name)

        # For the output file name we won't use a template but a final name. So, if we were downloading multiple files,
        # all of them would have the same name and just one file would be created and overwritten multiple times. In
        # reality, we will only use the Youtube downloader to download a single file each time, making this approach not
        # a problem at all.

        u_tmp_file_name = '%s/%s.%%(ext)s' % (po_dir.u_path, pu_name)

        dx_dl_options = {
            'format': 'bestaudio/best',
            'only_audio': True,
            'quiet': True,
            'outtmpl': u_tmp_file_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(dx_dl_options) as o_yt_downloader:
            o_yt_downloader.download([self.u_url])

        # Probably there is a better way of detecting an error during the download but I'll check whether the file
        # exists (because the extension is just .part until the download and post-processing is completed)

        if not o_local_file.b_isfile:
            o_local_file = None

        return o_local_file

    def str_oneline(self):
        """
        Method to produce a one-line summary text of the object to be use in debug.
        :return:
        :rtype unicode
        """
        u_out = '<Episode> %s %s' % (self.o_date_pub, self.u_title)
        return u_out

    def _get_u_mod_title(self):
        """
        Method to build a modified title for the episodes including the release date in it. That way, audio players that
        don't support sorting files by date tag, only by title, will show the episodes in the right order.
        :return:
        """
        u_mod_title = '%s - %s' % (self.o_date_pub.strftime('%y-%m-%d'), self.u_title)
        return u_mod_title

    def _parse_xml(self, po_xml):
        """
        Parent method to call other child-parsers depending on the format of the xml chunk to read.
        :param po_xml:
        :return:
        """
        # Youtube elements are contained within 'entry' tags
        if po_xml.tag == 'entry':
            self._parse_youtube_xml(po_xml)
        # While regular podcast RSS episodes are enclosed by 'item' tags
        elif po_xml.tag == 'item':
            self._parse_podcast_xml(po_xml)

    def _parse_youtube_xml(self, po_xml):
        """
        Method to populate the episode from a Youtube RSS xml.

        :param po_xml:
        :type po_xml: lxml.etree.ElementTree

        :return: Nothing
        """
        self.u_title = po_xml.find('title').text
        self.u_url = po_xml.find('link').attrib['href']

        u_date_pub = po_xml.find('published').text
        u_date_pat = '%Y-%m-%dT%H:%M:%S%z'
        self.o_date_pub = datetime.datetime.strptime(u_date_pub, u_date_pat)

    def _parse_podcast_xml(self, po_xml):
        # TODO: Any problem in the RSS will make the parsing to fail and the program to crash.
        # Make the program robust to those failures, if a RSS feed produces errors, print a descriptive error and jump
        # to the next feed.

        # In theory, the title field in the xml file should be encoded to avoid xml entities, so we have to decode them
        # to regular unicode characters
        self.u_title = html.unescape(po_xml.find('title').text)
        self.u_url = po_xml.find('enclosure').get('url')

        # trying to catch a problem with some feeds missing the pubDate tag
        try:
            u_date_pub = po_xml.find('pubDate').text
        except AttributeError:
            raise FeedFormatError(pu_short_msg='ERROR: missing publication date in episode entry.',
                                  pu_long_msg=lxml.etree.tostring(po_xml))

        u_date_pat = '%a, %d %b %Y %H:%M:%S %z'
        self.o_date_pub = datetime.datetime.strptime(u_date_pub, u_date_pat)

    def fix_tags(self, po_file, po_podcast=None):
        """
        Method to fix ID3 tags of a downloaded .mp3 file

        :param po_file: Filepath of the file to be tagged.
        :type po_file: files.FilePath

        :param po_podcast: Parent podcast of the episode to use some of its information in the fixing
        :type po_podcast: Podcast

        :return: Nothing
        """

        # Workaround to catch eye3D errors printed to stdout found at:
        #
        #     https://stackoverflow.com/questions/36636063/python-eyed3-lame-tag-crc-check-failed

        # Preparation to catch eyeD3 errors
        #----------------------------------
        o_log_stream = io.StringIO()
        logging.basicConfig(stream=o_log_stream, level=logging.INFO)
        # --- end ---

        o_audiofile = eyed3.load(po_file.u_path)

        # Some episodes could not have tags at all, so we have to initialise them first
        if o_audiofile.tag is None:
            o_audiofile.initTag()

        # The title will contain a unique alphabetic tag at the beginning so audio programs without support for podcasts
        # (e.g. jellyfin) will have proper order of episodes when sorting episodes alphabetically by title.
        o_audiofile.tag.title = self.u_mod_title

        # Not sure how many date fields are available for different versions of ID3 tags and whether they accept full
        # dates, but I'll set the three below to the date of the episode in the feed.
        o_audiofile.tag.original_release_date = self.o_date_pub.strftime('%Y-%m-%d')
        o_audiofile.tag.recording_date = self.o_date_pub.strftime('%Y-%m-%d')
        o_audiofile.tag.release_date = self.o_date_pub.strftime('%Y-%m-%d')

        # I've seen some podcasts without genre or with "vocal" one... so
        o_audiofile.tag.genre = 'Podcast'

        # Sometimes, podcasts are not very consistent when adding numbering to their episodes, so I prefer to remove
        # track numbers and rely on podcast title (which now will include the date at the beginning) to have proper
        # sorting
        o_audiofile.tag.track_num = (None, None)

        # ...and a bit less common, but some podcasts add disc number.
        o_audiofile.tag.disc_num = (None, None)

        # TODO: Use proper album artist = podcast title. By now I leave the tag empty
        # Again... lack of consistency on album artist and jellyfin sorting episodes in a weird order so I decided to
        # replace album artist tag with the podcast name.
        u_artist = ''
        if po_podcast is not None:
            u_artist = po_podcast.u_name

        o_audiofile.tag.album_artist = u_artist
        o_audiofile.tag.artist = u_artist

        u_album = ''
        if po_podcast is not None:
            u_album = po_podcast.u_name

        o_audiofile.tag.album = u_album

        o_audiofile.tag.save(encoding='utf-8')

        # Finally, we can read the errors and act depending on their type
        #----------------------------------------------------------------
        u_log = o_log_stream.getvalue()

        if u_log:
            # deal here with the error message in u_log
            # and then purge the o_log_stream to reuse it for next eye3d call
            o_log_stream.truncate(0)
        # all this code can be improved : enclose it in a try-catch, etc.
        # --- end ---

    u_mod_title = property(fget=_get_u_mod_title, fset=None)


# Exceptions
#=======================================================================================================================
class FeedFormatError(Exception):
    """
    Exception raised when the format of an XML feed is wrong.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, pu_short_msg='', pu_long_msg=''):
        self.u_short_msg = pu_short_msg
        self.u_long_msg = pu_long_msg
        super().__init__(self.u_short_msg)

    def nice_format(self):
        """
        Method to generate a nice format string to be printed in screen or saved to human-readable files.
        :return: The human-readable description of the Exception
        :rtype Str
        """
        u_out = '------\n'
        u_out += '%s\n' % self.u_short_msg
        u_out += '%s' % self.u_long_msg
        u_out = '------'
        return u_out


# Helper Functions
#=======================================================================================================================
def _remove_namespaces_qname(po_xml, lu_namespaces=None):
    """
    Function to remove namespaces from an ElementTree object. Code obtained from: https://code-examples.net/en/q/1151675

    :param po_xml: XML element to be modified.
    :type po_xml: lxml.etree.ElementTree

    :param lu_namespaces: List of namespaces to be removed
    :type lu_namespaces: List[Str]

    :return: A modified XML element without the desired namespaces.
    :rtype lxml.etree.ElementTree
    """
    o_new_xml = copy.deepcopy(po_xml)

    for o_elem in o_new_xml.getiterator():

        # clean tag
        q = lxml.etree.QName(o_elem.tag)
        if q is not None:
            if lu_namespaces is not None:
                if q.namespace in lu_namespaces:
                    o_elem.tag = q.localname
            else:
                o_elem.tag = q.localname

            # clean attributes
            for a, v in o_elem.items():
                q = lxml.etree.QName(a)
                if q is not None:
                    if lu_namespaces is not None:
                        if q.namespace in lu_namespaces:
                            del o_elem.attrib[a]
                            o_elem.attrib[q.localname] = v
                    else:
                        del o_elem.attrib[a]
                        o_elem.attrib[q.localname] = v
    return o_new_xml


def _number_to_base(pi_number, pi_base):
    if pi_number == 0:
        return [0]
    li_digits = []
    while pi_number:
        li_digits.append(int(pi_number % pi_base))
        pi_number //= pi_base
    return li_digits[::-1]


def _dl_file(pu_url, po_dir, pu_name=None):
    """

    :param pu_url: URL of the file to be downloaded
    :type pu_url: str

    :param po_dir:
    :type po_dir: files.FilePath

    :param pu_name: Local name for the file to be downloaded
    :type pu_name: str

    :return: The path of the downloaded file or None if the DL failed.
    :rtype str
    """
    if pu_name is None:
        u_file = files.FilePath(files.FilePath(pu_url).u_file)
    else:
        u_file = pu_name

    o_local_file = files.FilePath(po_dir.u_path, u_file)
    request.urlretrieve(pu_url, o_local_file.u_path)

    return o_local_file


def _transcode_file(po_src_file, pi_freq=22050, pi_bitrate=64):
    """
    Function to transcode audio files to .ogg
    :param po_src_file:
    :type po_src_file: files.FilePath

    :param pi_freq:
    :type pi_freq: int

    :param pi_bitrate:
    :type pi_bitrate: int

    :return: The output file object
    :rtype libs.files.File
    """

    o_dst_file = files.FilePath(po_src_file.u_dir, '%s_transcoded.%s' % (po_src_file.u_name, 'ogg'))

    lu_cmd = ['ffmpeg',
              '-i', po_src_file.u_path,
              '-ab', '%sk' % pi_bitrate,
              # Disabling video (sometimes people add images as video!?) and data
              '-vn', '-dn',
              '-ar', '%s' % pi_freq,
              '-acodec', 'libvorbis',
              '-hide_banner',
              o_dst_file.u_path]

    o_result = shell.cmd_run(lu_cmd)

    if o_result.i_rcode != 0:
        pass

    return o_dst_file


def _identify_smallest_episode(po_orig, po_trans):
    """
    Function to identify the local episode to keep and the one to remove based on the configuration (transcoding force
    option).

    :param po_orig: Original episode Filepath (without transcoding)
    :type po_orig: files.FilepPath

    :param po_trans: Transcoded episode Filepath
    :type po_trans: files.FilePath

    :return: Filepath to keep
    :rtype Tuple[files.Filepath]
    """

    if constants.b_TRANSC_FORC:
        o_keep = po_trans
        o_del = po_orig

    else:
        # If both files are valid
        if (po_trans.i_size > 0) and po_trans.i_size < po_orig.i_size:
            o_keep = po_trans
            o_del = po_orig

        else:
            o_keep = po_orig
            o_del = po_trans

    return o_keep, o_del


# Main functions
#=======================================================================================================================
def build_playlist(pb_changes):
    """
    Function to build a m3u playlist with all episodes.

    :param pb_changes:
    :type pb_changes: Bool
    """
    # First we build a list with all episodes
    #----------------------------------------
    o_eps_root = files.FilePath(constants.u_ARC_DIR)
    lo_pod_dirs = o_eps_root.listdir(pu_type='d')
    lo_files = []
    for o_pod_dir in lo_pod_dirs:
        lo_files += o_pod_dir.listdir(pu_type='f')

    lo_eps = [o_file for o_file in lo_files if o_file.has_ext('ogg', 'mp3')]
    lo_eps.sort(key=lambda o_eps: o_eps.u_name, reverse=True)

    # Then we build the relative path of each of the episodes
    #--------------------------------------------------------
    lu_rel_paths = []
    for o_eps in lo_eps:
        tu_rel_chunks = o_eps.tu_elems[-2:]
        u_rel_path = '/'.join(tu_rel_chunks)
        lu_rel_paths.append(u_rel_path)

    # Finally, we pack everything into the .m3u playlist
    #---------------------------------------------------
    o_fp_m3u = files.FilePath(constants.u_M3U)
    if pb_changes or not o_fp_m3u.b_isfile:
        u_msg = '- Generating playlist "%s"... ' % constants.u_M3U
        print(u_msg, end='')
        with open(constants.u_M3U, 'w') as o_file:
            for u_rel_path in lu_rel_paths:
                o_file.write('%s\n' % u_rel_path)
        print('DONE!')
