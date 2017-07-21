import subprocess
import sys


class RunCmdException(Exception):
    """
    When executing an shell command, there was an error
    """
    pass


def run_command(args, cwd=None, shell=False, stream=False):
    """
    :param args: List of strings that are parts of the command
    :param cwd : Set the working directory for the command
    :param shell: If true, the input string will be parsed and expanded by the shell
    :param stream: Stream the output from the command, otherwise return the output all at once
    :return: Tuple (str, str, int): standard out, standard error, return code
    :raise RunCmdException: If command returns a non-zero return code
    """
    cmd = subprocess.Popen(args, cwd=cwd, shell=shell, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    out = ""

    if stream:
        for c in iter(lambda: cmd.stdout.read(1), ''):
            sys.stdout.write(c)
            out += c
        error = cmd.stderr.read()
    else:
        out, error = cmd.communicate()

    if cmd.returncode:
        raise RunCmdException("Error executing command: {}\n{}, return code: "
                              "{}".format(args, error, cmd.returncode))
    return out, error
