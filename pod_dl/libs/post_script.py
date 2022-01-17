from . import shell


class PostScript(object):
    """
    Class to store information to be sent to the pos-downloading script.
    """
    def __init__(self):
        self.u_pod_name = ''  # Podcast name
        self.u_ep_title = ''  # Episode title
        self.u_ep_hsize = ''  # Size of the episode (human text format)
        self.u_ep_isize = ''  # Size of the episode (bytes)
        self.u_ep_durat = ''  # Duration of the episode (HH:MM:SS format)
        self.u_ep_path = ''   # Path of the episode
        self.u_msg_tpl = ''   # Message to be printed to screen, using same template variables as the script itself

        self.tu_cmd_tpl = ''  # Command line to be executed with template variables

    def _prepare_command(self):
        """
        Method to replace placeholders in the command template with actual values.

        :return: The full command ready to be executed
        :rtype Tuple[]unicode]
        """
        du_replaces = self._get_replaces_dict()

        lu_command = []
        for u_chunk in self.tu_cmd_tpl:
            for u_tag, u_value in du_replaces.items():
                u_chunk = u_chunk.replace(u_tag, u_value)

            lu_command.append(u_chunk)

        return tuple(lu_command)

    def _get_replaces_dict(self):
        du_replaces = {'%pod_name%': self.u_pod_name,
                       '%ep_title%': self.u_ep_title,
                       '%ep_hsize%': self.u_ep_hsize,
                       '%ep_isize%': self.u_ep_isize,
                       '%ep_durat%': self.u_ep_durat,
                       '%ep_path%':  self.u_ep_path}
        return du_replaces

    def _get_u_msg(self):
        """
        Method to replace placeholders in the command template with actual values.
        :return:
        """
        # Same replaces as in _prepare_command but they can't be a class constant since I'm using self.
        du_replaces = {'%pod_name%': self.u_pod_name,
                       '%ep_title%': self.u_ep_title,
                       '%ep_hsize%': self.u_ep_hsize,
                       '%ep_isize%': self.u_ep_isize,
                       '%ep_durat%': self.u_ep_durat,
                       '%ep_path%':  self.u_ep_path}

        u_msg = self.u_msg_tpl
        for u_tag, u_value in du_replaces.items():
            u_msg = u_msg.replace(u_tag, u_value)

        return u_msg

    def run(self):
        tu_command = self._prepare_command()

        o_result = shell.cmd_run(tu_command)

        # TODO: Add better error catching/logging here.
        # Even though it won't look nice, printing the stdout+stderr to screen would be a good idea in debug mode.
        b_success = False
        if o_result.i_rcode == 0:
            b_success = True

        # --- TEST CODE ---
        else:
            print(o_result.nice_format())
            quit()
        # ------ end ------

        return b_success

    u_msg = property(fget=_get_u_msg, fset=None)
