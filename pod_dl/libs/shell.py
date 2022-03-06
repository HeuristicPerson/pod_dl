import subprocess

import charset_normalizer


# Classes
#=======================================================================================================================
class CmdResult:
    """
    Class to store the output of a shell command.

    :ivar i_rcode: Union[int, None]
    :ivar u_cmd: Union[str, None]
    :ivar u_stderr: Union[str, None]
    :ivar u_stdout: Union[str, None]
    """

    def __init__(self):
        self.i_rcode = None   # Return code of the command
        self.u_cmd = None     # Command line executed
        self.u_stdout = None  # Stdout output of the command
        self.u_stderr = None  # Stderr output of the command

    def nice_format(self):
        u_out = ''
        u_out += 'cmd:    %s\n' % self.u_cmd
        u_out += 'rcode:  %s\n' % self.i_rcode

        for i_line, u_line in enumerate(self.u_stdout.splitlines()):
            if i_line == 0:
                u_out += 'stdout: %s\n' % u_line
            else:
                u_out += '        %s\n' % u_line

        for i_line, u_line in enumerate(self.u_stderr.splitlines()):
            if i_line == 0:
                u_out += 'stderr: %s\n' % u_line
            else:
                u_out += '        %s\n' % u_line

        return u_out


def cmd_run(plu_cmd):
    """
    Function to run shell commands and capture stdout and stderr

    :param plu_cmd
    :type plu_cmd: Unite[Tuple[unicode], List[unicode]]
    """
    o_process = subprocess.Popen(plu_cmd,
                                 bufsize=0,
                                 # universal_newlines=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

    # The output will be a bytes string (I believe)
    b_stdout, b_stderr = o_process.communicate()

    i_return_code = o_process.returncode

    o_result = CmdResult()
    o_result.i_rcode = i_return_code
    o_result.u_cmd = u' '.join(plu_cmd)
    try:
        o_result.u_stdout = b_stdout.decode('utf8')
    except UnicodeDecodeError:
        o_result.u_stdout = charset_normalizer.from_bytes(b_stdout).best()

    try:
        o_result.u_stderr = b_stderr.decode('utf8')
    except UnicodeDecodeError:
        o_result.u_stderr = charset_normalizer.from_bytes(b_stderr).best()

    return o_result
