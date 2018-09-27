import shutil
import subprocess as sub
import os
import os.path
import sys
import re


def find_labeled_output(out, label):
    data = []
    for l in out:
        if str(label) in l and 'Keyword' in l:
            data.append(l)
            continue
        if len(data) > 0:
            if '****' in l:
                break
            data.append(l)
    return list(filter(lambda _: len(_), data))


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class Zgoubi:
    """Encapsulation of methods to run Zgoubi from Python."""
    ZGOUBI_RES_FILE = 'zgoubi.res'

    def __init__(self, executable='zgoubi', path=None, **kwargs):
        """

        :param beamlines:
        :param path: path to the simulator executable (default: lookup using 'which')
        :param kwargs:
        """
        self._executable: str = executable
        self._path: str = path

    @property
    def executable(self) -> str:
        return self._get_exec()

    def __call__(self, _, debug=False):
        _()
        stderr = None
        p = sub.Popen([self._get_exec()],
                      stdin=sub.PIPE,
                      stdout=sub.PIPE,
                      stderr=sub.STDOUT,
                      cwd=".",
                      shell=True
                      )

        # Run
        output = p.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        result = open(Zgoubi.ZGOUBI_RES_FILE, 'r').read().split('\n')
        for e in _.line:
            e.attach_output(find_labeled_output(result, e.LABEL1))

        # Extract CPU time
        cputime = -1.0
        if stderr is None:
            lines = [line.strip() for line in output[0].decode().split('\n') if
                     re.search('CPU time', line)]
            if len(lines):
                cputime = float(re.search("\d+\.\d+[E|e]?[\+|-]?\d+", lines[0]).group())
        if debug:
            print(output[0].decode())
        try:
            return {
                'stdout': output[0].decode().split('\n'),
                'stderr': stderr,
                'cputime': cputime,
                'result': result,
                'input': _,
            }
        except FileNotFoundError:
            raise ZgoubiException("Executation terminated with errors.")

    def _get_exec(self) -> str:
        """Retrive the path to the simulator executable."""
        if self._path is not None:
            return os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            return shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                return f"{sys.prefix}/bin/{self._executable}"
            else:
                return shutil.which(self._executable, path=os.path.join(os.environ['PATH'], '/usr/local/bin'))

