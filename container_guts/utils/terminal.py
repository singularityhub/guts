__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2024, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
from subprocess import PIPE, STDOUT, Popen

from container_guts.logger import logger


def ensure_no_extra(extra):
    """
    Ensure no extra arguments (in case typos)
    """
    if extra:
        logger.exit(
            "Extra arguments provided that are not known to this command: %s"
            % " ".join(extra)
        )


def get_installdir():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_userhome():
    """
    Get the user home based on the effective uid.
    """
    try:
        import pwd

        return pwd.getpwuid(os.getuid())[5]
    except Exception:
        # Fallback to envar for Windows, etc.
        return os.environ.get("HOME")


def run_command(cmd, sudo=False, stream=False):
    """
    run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    """
    stdout = PIPE if not stream else None
    if sudo is True:
        cmd = ["sudo"] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=stdout)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")

    return output


def confirm_action(question, force=False):
    """confirm if the user wants to perform a certain action

    Parameters
    ==========
    question: the question that will be asked
    force: if the user wants to skip the prompt
    """
    if force is True:
        return True

    response = input(question + " (yes/no)? ")
    while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
        response = input("Please answer yes or no: ")

    if response[0].lower().strip() in "no":
        return False
    return True
