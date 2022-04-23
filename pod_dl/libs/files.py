import datetime
import os


# Constant
#=======================================================================================================================
u_TYPE_FILE = 'f'
u_TYPE_DIR = 'd'
u_TYPE_ALL = 'a'


# Classes
#=======================================================================================================================
class FilePath(object):
    def __init__(self, *pu_path):
        """

        :param pu_path:
        :type pu_path: unicode
        """
        self._u_path = os.path.join(*pu_path)

    def __eq__(self, po_other):
        """
        Method to check the equality between two FilePath objects.

        :param po_other:
        :type po_other: FilePath
        :return:
        """
        b_equal = False
        if (po_other is not None) and (self.u_path == po_other.u_path):
            b_equal = True

        return b_equal

    def __hash__(self):
        """
        Method to compute the hash of the object so it can be used, for example, when building unique sets.
        :return:
        """
        return hash(self.u_path)

    def __str__(self):
        u_out = '<FilePath>\n'
        u_out += '  .b_isdir:  %s\n' % self.b_isdir
        u_out += '  .b_isfile: %s\n' % self.b_isfile
        u_out += '  .i_size:   %s\n' % self.i_size
        u_out += '  .f_mtime:  %s\n' % self.f_mtime
        u_out += '  .o_mtime:  %s\n' % self.o_mtime
        u_out += '  .u_dir:    %s\n' % self.u_dir
        u_out += '  .u_file:   %s\n' % self.u_file
        u_out += '  .u_name:   %s\n' % self.u_name
        u_out += '  .u_path:   %s\n' % self.u_path
        u_out += '  .u_ext:    %s\n' % self.u_ext
        u_out += '  .u_size:   %s\n' % self.u_size
        return u_out

    def has_ext(self, *pu_exts):
        """
        Method to check whether the file path has certain extensions.

        :param pu_exts:
        :type pu_exts: unicode

        :return: True if the extension of the FilePath is in the provided list (case insensitive).
        :rtype bool
        """
        lu_exts = [u_ext.lower() for u_ext in pu_exts]
        b_has_ext = False
        if self.u_ext.lower() in lu_exts:
            b_has_ext = True
        return b_has_ext

    def listdir(self, pu_type='a'):
        """
        Method to mimic os.listdir behaviour.

        :param pu_type =
        :type pu_type: unicode

        :return:
        :rtype  list[FilePath]
        """
        lo_elems = []
        try:
            for u_elem in os.listdir(self.u_path):
                o_elem = FilePath(self.u_path, u_elem)
                b_valid = False

                if pu_type == u_TYPE_ALL:
                    b_valid = True
                elif (pu_type == u_TYPE_DIR) and o_elem.b_isdir:
                    b_valid = True
                elif (pu_type == u_TYPE_FILE) and o_elem.b_isfile:
                    b_valid = True

                if b_valid:
                    lo_elems.append(o_elem)
        except FileNotFoundError:
            pass

        return lo_elems

    def _get_b_isdir(self):
        """
        Method to return true if the FilePath object is a dir
        :return:
        :rtype bool
        """
        return os.path.isdir(self.u_path)

    def _get_b_isfile(self):
        """
        Method to return true if the FilePath object is a dir
        :return:
        :rtype bool
        """
        return os.path.isfile(self.u_path)

    def _get_f_mtime(self):
        """
        Function that returns the number of seconds from epoch until the file was last modified.
        :return:
        """
        try:
            f_mtime = os.path.getmtime(self.u_path)
        except FileNotFoundError:
            f_mtime = None

        return f_mtime

    def _get_i_size(self):
        try:
            i_size = os.path.getsize(self._get_u_path())
        except IOError:
            i_size = None

        return i_size

    def _get_o_mtime(self):
        o_mtime = None

        f_mtime = self._get_f_mtime()
        if f_mtime is not None:
            o_mtime = datetime.datetime.fromtimestamp(self._get_f_mtime())

        return o_mtime

    def _get_tu_elems(self):
        """
        Imagine you have a path which is /aaa/bbb/ccc/foo.bar (it could be a file or a directory). This method will
        return a list of its elements in the form of ('aaa', 'bbb', 'ccc', 'foo.bar') so you can extract and manimpulate
        the path easily.

        :return:
        :rtype tuple[unicode]
        """
        # Not sure why, but I obtain a first empty string (probably because since my paths start with /, there is an
        # empty character before (!?). So, I remove it.
        lu_chunks = os.path.normpath(self.u_path).split(os.path.sep)
        if lu_chunks[0] == '':
            lu_chunks = lu_chunks[1:]
        return tuple(lu_chunks)

    def _get_u_dir(self):
        return os.path.dirname(self._get_u_path())

    def _get_u_file(self):
        return os.path.basename(self._get_u_path())

    def _get_u_name(self):
        return self._get_u_file().rpartition('.')[0]

    def _get_u_path(self):
        return os.path.normpath(os.path.abspath(self._u_path))

    def _get_u_ext(self):
        return self._get_u_file().rpartition('.')[2]

    def _get_u_size(self):
        try:
            u_size = human_size(self._get_i_size())
        except TypeError:
            u_size = 'None'
        return u_size

    b_isdir = property(fget=_get_b_isdir, fset=None)
    b_isfile = property(fget=_get_b_isfile, fset=None)
    f_mtime = property(fget=_get_f_mtime, fset=None)
    i_size = property(fget=_get_i_size, fset=None)
    o_mtime = property(fget=_get_o_mtime, fset=None)
    u_dir = property(fget=_get_u_dir, fset=None)
    u_file = property(fget=_get_u_file, fset=None)
    u_name = property(fget=_get_u_name, fset=None)
    u_path = property(fget=_get_u_path, fset=None)
    u_ext = property(fget=_get_u_ext, fset=None)
    u_size = property(fget=_get_u_size, fset=None)
    tu_elems = property(fget=_get_tu_elems, fset=None)


# Functions
#=======================================================================================================================
def compare_lists_of_files(plo_files_a, plo_files_b):
    """
    Function to compare to lists of FilePaths.

    :param plo_files_a:
    :type plo_files_a: list[FilePath]

    :param plo_files_b:
    :type plo_files_b: list[FilePath]

    :return: Three list of filepaths, just in A, just in B, common filepaths
    :rtype list[list[FilePath]]
    """
    lo_common_filepaths = []
    lo_just_a_filepaths = []
    lo_just_b_filepaths = []

    for o_file_a in plo_files_a:
        if o_file_a in plo_files_b:
            lo_common_filepaths.append(o_file_a)
        else:
            lo_just_a_filepaths.append(o_file_a)

    for o_file_b in plo_files_b:
        if o_file_b in plo_files_a:
            lo_common_filepaths.append(o_file_b)
        else:
            lo_just_b_filepaths.append(o_file_b)

    return list(set(lo_just_a_filepaths)), list(set(lo_just_b_filepaths)), list(set(lo_common_filepaths))


def find_smallest_and_largest(*po_file):
    """
    Function to find the largest and smallest files in a set. In case you have multiple files with the same size,
    results will be ANY of them.

    :param po_file: File object(s) to compare.
    :type po_file: FilePath

    :return: Largest and Smallest FilePath objects. In case you have several files with same size, any of them will be
             use.
    :rtype FilePath, FilePath
    """
    # TODO: Make this function work when one of the files is None. Ignore the None files?

    lo_files = []
    for o_file in list(po_file):
        if o_file is not None:
            lo_files.append(o_file)

    lo_files = sorted(lo_files, key=lambda o_file: o_file.i_size)
    o_file_smallest = lo_files[0]
    o_file_largest = lo_files[-1]

    return o_file_smallest, o_file_largest


def human_size(pi_bytes, pu_suffix='B'):
    """
    Function to produce a human-readable size text from a number of bytes.

    :param pi_bytes:
    :type pi_bytes: int

    :param pu_suffix:
    :type pu_suffix: unicode

    :return:
    :rtype unicode
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(pi_bytes) < 1024.0:
            return "%3.1f %s%s" % (pi_bytes, unit, pu_suffix)
        pi_bytes /= 1024.0
    return '%.1f %s%s' % (pi_bytes, 'Yi', pu_suffix)