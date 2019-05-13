"""Provides an interface to run Zgoubi from Python; supports multiprocessing and concurrent programming.

"""
from __future__ import annotations
from typing import Dict, List, Optional, Callable, Union
import logging
import shutil
import tempfile
import os
import sys
import re
from io import IOBase as _IOBase
import multiprocessing
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from concurrent.futures import Future as _Future
import subprocess as sub
from .input import Input
from .input import MappedParametersType as _MappedParametersType
from .input import ZGOUBI_INPUT_FILENAME as _ZGOUBI_INPUT_FILENAME

__all__ = ['Executable', 'ResultsType']
_logger = logging.getLogger(__name__)


class ExecutableException(Exception):
    """Exception raised for error in the executable module."""

    def __init__(self, m):
        self.message = m


class ResultsType(type):
    """TODO"""
    pass


class ExecutableResults(metaclass=ResultsType):
    """TODO"""
    pass


class Executable:
    """High level interface to run Zgoubi from Python."""

    def __init__(self, executable: str, results_type: ResultsType, path: str = None, n_procs: Optional[int] = None):
        """


        Args:
            - executable: name of the Zgoubi executable
            - results_type:
            - path: path to the Zgoubi executable
            - n_procs: maximum number of Zgoubi simulations to be started in parallel

        """
        self._executable: str = executable
        self._results_type: ResultsType = results_type
        self._n_procs: int = n_procs or multiprocessing.cpu_count()
        self._path: Optional[str] = path
        self._futures: Dict[str, _Future] = dict()
        self._pool: _ThreadPoolExecutor = _ThreadPoolExecutor(max_workers=self._n_procs)

    @property
    def executable(self) -> str:
        """Provides the full path to the Zgoubi executable.

        Returns:
            full path to the Zgoubi executable.
        """
        return self._get_exec()

    def __call__(self,
                 code_input: Input,
                 identifier: _MappedParametersType = None,
                 mappings: _MappedParametersType = None,
                 debug: bool = False,
                 cb: Callable = None,
                 filename: str = _ZGOUBI_INPUT_FILENAME,
                 path: Optional[str] = None,
                 ) -> Executable:
        """
        Execute up to `n_procs` Zgoubi runs.

        Args:
            code_input: `Input` object specifying the Zgoubi inputs and input paths.
            identifier: TODO
            mappings: TODO
            debug: verbose output
            (default to `multiprocessing.cpu_count`)

        Returns:
            a ZgoubiResults object holding the simulation results.

        Raises:
            a ZgoubiException in case the input paths list is empty.
        """
        mappings = mappings or [{}]
        identifier = identifier or {}
        mappings = [{**m, **identifier} for m in mappings]
        for m, path in code_input(mappings=mappings, filename=filename, path=path).paths:
            print(f"Calling execute for mapping {m}")
            _logger.info(f"Starting Zgoubi in {path}.")
            future = self._pool.submit(
                self._execute,
                m,
                code_input,
                path,
            )
            if cb is not None:
                future.add_done_callback(cb)
            self._futures[path] = future
        return self

    def wait(self):
        """
        TODO

        """
        self._pool.shutdown()
        self._pool = _ThreadPoolExecutor(max_workers=self._n_procs)

    def collect(self, paths: Optional[List[str]] = None) -> ExecutableResults:
        """
        TODO
        Returns:

        """
        paths = paths or list(self._futures.keys())
        futures = [self._futures[p] for p in paths]
        self.wait()
        return self._results_type(results=[_.result() for _ in futures])

    def cleanup(self):
        """

        Returns:

        """
        self.wait()
        self._futures = dict()
        return self

    def _execute(self,
                 mapping: _MappedParametersType,
                 code_input: Input,
                 path: Union[str, tempfile.TemporaryDirectory] = '.',
                 debug=False
                 ) -> dict:
        """Run Zgoubi as a subprocess.

        Zgoubi is run as a subprocess; the standard IOs are piped to the Python process and retrieved.

        Args:
            code_input: Zgoubi input physics (used after the run to process the output of each element).
            path: path to the input file.
            mapping: TODO
            debug: verbose output.

        Returns:
            a dictionary holding the results of the run.

        Raises:
            FileNotFoundError if the result file is not present at the end of the execution.
        """
        stderr = None
        try:
            p = path.name  # Path from a TemporaryDirectory
        except AttributeError:
            p = path  # p is a string
        proc = sub.Popen([self.executable],
                         stdin=sub.PIPE,
                         stdout=sub.PIPE,
                         stderr=sub.STDOUT,
                         cwd=p,
                         )

        # Run
        _logger.info(f"Zgoubi process in {path} has started.")
        output = proc.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        result = self._extract_output(path=p, code_input=code_input, mapping=mapping)

        # Extract CPU time
        cputime = -1.0
        if stderr is None:
            lines = [line.strip() for line in output[0].decode().split('\n') if
                     re.search('CPU time', line)]
            if len(lines):
                cputime = float(re.search(r"\d+\.\d+[E|e]?[+|-]?\d+", lines[0]).group())
        if debug:
            print(output[0].decode())
        _logger.info(f"Zgoubi process in {path} finished in {cputime} s.")
        return {
            'stdout': output[0].decode().split('\n'),
            'stderr': stderr,
            'cputime': cputime,
            'result': result,
            'input': code_input,
            'path': path,
            'mapping': mapping,
        }

    def _extract_output(self, path, code_input: Input, mapping) -> Optional[_IOBase]:
        return None

    def _get_exec(self, path: Optional[str] = '/usr/local/bin') -> str:
        """Retrive the path to the Zgoubi executable.

        Args:
            path: additional path provided to the `which` command.

        Returns:
            a string representing the full path to the executable.

        Raises:
            ZgoubiException in case the executable is not found.
        """
        if self._path is not None:
            executable: Optional[str] = os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            executable: Optional[str] = shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                executable: Optional[str] = f"{sys.prefix}/bin/{self._executable}"
            else:
                executable: Optional[str] = shutil.which(self._executable, path=os.path.join(os.environ['PATH'], path))
        if executable is None:
            raise ExecutableException("Unable to locate the executable.")
        return executable
