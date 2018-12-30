"""Provides an interface to run Zgoubi from Python; supports multiprocessing.

.. seealso::

    The full `Zgoubi User Guide`_ can also be consulted for reference.

    .. _Zgoubi User Guide: https://sourceforge.net/projects/zgoubi/


"""
from typing import List, Mapping, Iterable, Optional
from functools import partial as _partial
import logging
import shutil
import os
import sys
import re
import multiprocessing
from multiprocessing.pool import ThreadPool as _ThreadPool
import subprocess as sub
import pandas as _pd
from .input import Input
from .output import read_plt_file


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class ZgoubiRun:
    """

    """
    def __init__(self, results: List[Mapping]):
        """

        Args:
            results:
        """
        self._results = results
        self._tracks = None

    @property
    def tracks(self) -> Optional[_pd.DataFrame]:
        """
        Collect all tracks from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result.
        """
        if self._tracks is None:
            try:
                tracks = list()
                for r in self._results:
                    tracks.append(read_plt_file(path=r['path']))
                self._tracks = _pd.concat(tracks)
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    "Unable to read and load the Zgoubi .plt files required to collect the tracks.")
                return None
        return self._tracks

    @property
    def matrix(self):
        """

        Returns:

        """
        pass

    @property
    def results(self) -> List[Mapping]:
        """

        Returns:

        """
        return self._results


class Zgoubi:
    """High level interface to run Zgoubi from Python."""

    ZGOUBI_EXECUTABLE_NAME = 'zgoubi'
    """Default name of the Zgoubi executable."""

    ZGOUBI_RES_FILE = 'zgoubi.res'
    """Default name of the Zgoubi result '.res' file."""

    def __init__(self, executable: str = ZGOUBI_EXECUTABLE_NAME, path: str = None):
        """
        The created `Zgoubi` object is an interface to the Zgoubi executable. The executable can be found
        automatically or its name and path can be specified.

        The Zgoubi executable is called on an instance of `Input` specifying a list of paths containing Zgoubi input
        files. Multiple instances can thus be run in parallell.

        Args:
            - executable: name of the Zgoubi executable
            - path: path to the Zgoubi executable
        """
        self._executable: str = executable
        self._path: str = path
        self._results: List[multiprocessing.pool.ApplyResult] = list()

    @property
    def executable(self) -> str:
        """Provides the full path to the Zgoubi executable.

        Returns:
            full path to the Zgoubi executable.
        """
        return self._get_exec()

    def __call__(self, zgoubi_input: Input, debug: bool = False, n_procs: int = None) -> ZgoubiRun:
        """
        Starts up to `n_procs` Zgoubi runs.

        Args:
            zgoubi_input: `Input` object specifying the Zgoubi inputs and input paths.
            debug: verbose output
            n_procs: maximum number of Zgoubi simulations to be started in parallel

        Returns:
            a ZgoubiRun object holding the simulation results.
        """
        n = n_procs or multiprocessing.cpu_count()
        self._results = list()
        pool = _ThreadPool(n)
        if len(zgoubi_input.paths) == 0:
            raise ZgoubiException("The input must be written before calling Zgoubi.")
        for p in zgoubi_input.paths:
            try:
                path = p.name
            except AttributeError:
                path = p
            self._results.append(pool.apply_async(self._execute_zgoubi, (zgoubi_input, path)))
        pool.close()
        pool.join()
        return ZgoubiRun(list(map(lambda _: getattr(_, 'get', None)(), self._results)))

    def _execute_zgoubi(self, zgoubi_input: Input, path: str = '.', debug=False) -> dict:
        """

        Args:
            zgoubi_input:
            path:
            debug:

        Returns:
            a dictionary holding the results of the run.
        """
        stderr = None
        p = sub.Popen([self._get_exec()],
                      stdin=sub.PIPE,
                      stdout=sub.PIPE,
                      stderr=sub.STDOUT,
                      cwd=path,
                      )

        # Run
        output = p.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        result = open(os.path.join(path, Zgoubi.ZGOUBI_RES_FILE)).read().split('\n')
        for e in zgoubi_input.line:
            list(
                map(_partial(e.attach_output, zgoubi_input=zgoubi_input), Zgoubi.find_labeled_output(result, e.LABEL1))
            )

        # Extract CPU time
        cputime = -1.0
        if stderr is None:
            lines = [line.strip() for line in output[0].decode().split('\n') if
                     re.search('CPU time', line)]
            if len(lines):
                cputime = float(re.search(r"\d+\.\d+[E|e]?[+|-]?\d+", lines[0]).group())
        if debug:
            print(output[0].decode())
        return {
            'stdout': output[0].decode().split('\n'),
            'stderr': stderr,
            'cputime': cputime,
            'result': result,
            'input': zgoubi_input,
            'path': path,
        }

    def _get_exec(self, optional_path: str = '/usr/local/bin') -> str:
        """Retrive the path to the Zgoubi executable.

        Returns:

        """
        if self._path is not None:
            return os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            return shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                return f"{sys.prefix}/bin/{self._executable}"
            else:
                return shutil.which(self._executable, path=os.path.join(os.environ['PATH'], optional_path))

    @staticmethod
    def find_labeled_output(out: Iterable[str], label: str) -> list:
        """
        Process the Zgoubi output and retrieves output data for a particular labeled element.

        Args:
            - out: the Zgoubi output
            - label: the label of the element to be retrieved

        Returns:
            the output of the given label
        """
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
