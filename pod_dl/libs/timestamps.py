import codecs
import datetime

# Constants
#=======================================================================================================================
_u_FORMAT = '%Y-%m-%d %H:%M:%S %z'


# Functions
#=======================================================================================================================
def read_timestamp(po_file):
    """
    Method to read a timestamp from a file
    :param po_file:
    :type po_file: .files.FilePath

    :return:
    :rtype Union[datetime.Datetime, None]
    """
    try:
        with codecs.open(po_file.u_path, 'r', 'utf8') as o_file:
            u_date = o_file.read().strip()
            o_datetime = datetime.datetime.strptime(u_date, _u_FORMAT)

    except (FileNotFoundError, NotADirectoryError):
        o_datetime = None

    return o_datetime


def save_timestamp(po_file, po_datetime):
    """
    Method to save a timestamp to a file.

    :param po_datetime:
    :type po_datetime: Union[datetime.DateTime, None]

    :param po_file:
    :type po_file: files.FilePath

    :return: Nothing
    """
    o_saved_datetime = read_timestamp(po_file)

    b_save = False
    if None not in (o_saved_datetime, po_datetime):
        if po_datetime > o_saved_datetime:
            b_save = True

    elif po_datetime is not None:
        b_save = True

    if b_save:
        with codecs.open(po_file.u_path, 'w', 'utf8') as o_file:
            o_file.write(po_datetime.strftime(_u_FORMAT))
