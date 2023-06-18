import ast
import configparser
import os


# Program constants that users shouldn't modify Constants
#=======================================================================================================================
# Program name
u_PRG = 'Pod DL'

# Program version. Always leave a space between release version and release date because the first part will appear in
# run.sh for docker. So it looks nicer when that version number and the docker tag coincide.
u_VER = 'v1.1.dev 2022-10-24'

# Number of retries and delay between them for downloads
i_DL_RETRIES = 5
i_DL_RETRY_DELAY = 10

# Main configuration file
_u_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
s_TEST_DATA_ROOT = os.path.join(_u_ROOT, 'test', 'test_data')
_u_CFG_FILE = os.path.join(_u_ROOT, 'pod_dl.ini')

# Values that will indicate yes in an environment variable
_tu_ON_VALUES = ('yes', '1', 'on', 'true', 'y')


# Helper functions
#=======================================================================================================================
def _read_ini_cfg():
    """
    Function to initialize constants from configuration file

    :return: Nothing
    """
    global b_DEBUG
    global i_MAX_ARCH
    global i_MAX_SYNC
    global u_ARC_DIR
    global tu_POST_SCR
    global u_POST_SCR_MSG
    global u_TMP_DIR
    global b_TRANSC_SERV
    global b_TRANSC_FORC
    global i_TRANSC_FREQ
    global i_TRANSC_BITR

    o_config = configparser.RawConfigParser()
    o_config.read(_u_CFG_FILE)

    # Debug mode
    b_DEBUG = False
    if o_config['main']['debug'].lower() in _tu_ON_VALUES:
        b_DEBUG = True

    # Temporary dir
    u_TMP_DIR = o_config['main']['tmp_dir']

    # Archive dir
    u_ARC_DIR = o_config['main']['arc_dir']

    # Max files to download the first time
    i_MAX_SYNC = int(o_config['main']['max_sync'])

    # Max episodes to keep in the archive for each podcast
    i_MAX_ARCH = int(o_config['main']['max_arch'])

    # Transcode service
    b_TRANSC_SERV = False
    if o_config['transcode']['active'].lower() in _tu_ON_VALUES:
        b_TRANSC_SERV = True

    # Force transcode
    b_TRANSC_FORC = False
    if o_config['transcode']['force'].lower() in _tu_ON_VALUES:
        b_TRANSC_FORC = True

    # Transcode frequency
    i_TRANSC_FREQ = int(o_config['transcode']['frequency'])

    # Transcode bitrate
    i_TRANSC_BITR = int(o_config['transcode']['bitrate'])

    # Post download script
    u_cmd = o_config['post_script']['command']
    if u_cmd.strip():
        tu_POST_SCR = ast.literal_eval(u_cmd)

    # Post download message
    u_POST_SCR_MSG = o_config['post_script']['message']


def _read_env_cfg():
    """
    Function to initialise constants from environment variables. These variables will overwrite values included in the
    ini file.

    :return: Nothing
    """
    global b_DEBUG
    global i_MAX_ARCH
    global i_MAX_SYNC
    global u_ARC_DIR
    global tu_POST_SCR
    global u_POST_SCR_MSG
    global u_TMP_DIR
    global b_TRANSC_SERV
    global b_TRANSC_FORC
    global i_TRANSC_FREQ
    global i_TRANSC_BITR

    # Debug mode
    u_env_debug = os.getenv('POD_DL_DEBUG')
    if u_env_debug is not None:
        b_DEBUG = False
        if u_env_debug.lower() in _tu_ON_VALUES:
            b_DEBUG = True

    # Temporary download dir
    u_env_temp = os.getenv('POD_DL_TEMP')
    if u_env_temp is not None:
        u_TMP_DIR = u_env_temp

    # Archive dir
    u_env_arch = os.getenv('POD_DL_ARCH')
    if u_env_arch is not None:
        u_ARC_DIR = u_env_arch

    # Max sync episodes
    u_env_max_sync = os.getenv('POD_DL_MAX_SYNC')
    if u_env_max_sync is not None:
        i_MAX_SYNC = int(u_env_max_sync)

    # Max arch episodes
    u_env_max_arch = os.getenv('POD_DL_MAX_ARCH')
    if u_env_max_arch is not None:
        i_MAX_ARCH = int(u_env_max_arch)

    # Transcoding service
    u_env_transc_serv = os.getenv('POD_DL_TRANSC_SERV')
    if u_env_transc_serv is not None:
        b_TRANSC_SERV = False
        if u_env_transc_serv.lower() in _tu_ON_VALUES:
            b_TRANSC_SERV = True

    # Transcoding force
    u_env_transc_forc = os.getenv('POD_DL_TRANSC_FORC')
    if u_env_transc_forc is not None:
        b_TRANSC_FORC = False
        if u_env_transc_forc.lower() in _tu_ON_VALUES:
            b_TRANSC_FORC = True

    # Transcoding frequency
    u_env_transc_freq = os.getenv('POD_DL_TRANSC_FREQ')
    if u_env_transc_freq is not None:
        i_TRANSC_FREQ = int(u_env_transc_freq)

    # Transcoding bitrate
    u_env_transc_bitr = os.getenv('POD_DL_TRANSC_BITR')
    if u_env_transc_bitr is not None:
        i_TRANSC_BITR = int(u_env_transc_bitr)

    # Post-Script command
    u_env_scr_cmd = os.getenv('POD_DL_SCR_CMD')
    if u_env_scr_cmd is not None:
        tu_POST_SCR = ast.literal_eval(u_env_scr_cmd)

    # Post-Script message
    u_env_scr_msg = os.getenv('POD_DL_SCR_MSG')
    if u_env_scr_msg is not None:
        u_POST_SCR_MSG = u_env_scr_msg


def print_constants():
    print('- Constants')
    print('  - b_DEBUG:       ', b_DEBUG)
    print('  - u_TMP_DIR:     ', u_TMP_DIR)
    print('  - u_ARC_DIR:     ', u_ARC_DIR)
    print('  - i_MAX_SYNC:    ', i_MAX_SYNC)
    print('  - i_MAX_ARCH:    ', i_MAX_ARCH)
    print('  - tu_POST_SCR:   ', tu_POST_SCR)
    print('  - u_POST_SCR_MSG:', u_POST_SCR_MSG)
    print('')


# Main code
#=======================================================================================================================

# Default "empty" values of the constants (which will make the program NOT to work)
b_DEBUG = False        # In debug mode, the program will be more verbose

u_TMP_DIR = ''         # type: str  # Directory for temporary files
u_ARC_DIR = ''         # type: str  # Directory to long-term archive episodes
i_MAX_SYNC = 0         # type: int  # Max number of episodes to download on the first import
i_MAX_ARCH = 0         # type: int  # Max number of episodes in the archive for each podcast

b_TRANSC_SERV = False  # type: bool # Whether transcoding is active or not
b_TRANSC_FORC = False  # type: bool # When true, transcoded file will always be kept no matter if it's bigger or invalid
i_TRANSC_FREQ = 0      # type: int  # Frequency of the transcoded file
i_TRANSC_BITR = 0      # type: int  # Bitrate of the transcoded file

tu_POST_SCR = tuple()  # type: tuple[str] # Script or command to be executed after the download of each episode
u_POST_SCR_MSG = ''    # type: str        # Message to be printed after the execution of each episode

_read_ini_cfg()
_read_env_cfg()

u_SUBS = '%s/subs.txt' % u_ARC_DIR                 # type: str # File with podcast subscriptions
u_M3U = '%s/all podcast episodes.m3u' % u_ARC_DIR  # type: str # Playlist with all episodes
