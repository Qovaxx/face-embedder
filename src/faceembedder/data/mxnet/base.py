# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# coding: utf-8
# pylint: disable=invalid-name, no-member, trailing-comma-tuple, bad-mcs-classmethod-argument, unnecessary-pass, too-many-lines, wrong-import-position
"""ctypes library of mxnet and helper functions."""
from __future__ import absolute_import

import os
import sys
import ctypes

__all__ = ['MXNetError']

error_types = {}

if sys.version_info[0] > 2:
    # this function is needed for python3
    # to convert ctypes.char_p .value back to python str
    py_str = lambda x: x.decode('utf-8')
else:
    py_str = lambda x: x


class MXNetError(RuntimeError):
    """Default error thrown by MXNet functions.
    MXNetError will be raised if you do not give any error type specification,
    """


def _valid_error_name(name):
    """Check whether name is a valid error name."""
    return all(x.isalnum() or x in "_." for x in name)


def _find_error_type(line):
    """Find the error name given the first line of the error message.
    Parameters
    ----------
    line : str
        The first line of error message.
    Returns
    -------
    name : str The error name
    """
    end_pos = line.find(":")
    if end_pos == -1:
        return None
    err_name = line[:end_pos]
    if _valid_error_name(err_name):
        return err_name
    return None


def c2pyerror(err_msg):
    """Translate C API error message to python style.
    Parameters
    ----------
    err_msg : str
        The error message.
    Returns
    -------
    new_msg : str
        Translated message.
    err_type : str
        Detected error type.
    """
    arr = err_msg.split("\n")
    if arr[-1] == "":
        arr.pop()
    err_type = _find_error_type(arr[0])
    trace_mode = False
    stack_trace = []
    message = []
    for line in arr:
        if trace_mode:
            if line.startswith("  "):
                stack_trace.append(line)
            else:
                trace_mode = False
        if not trace_mode:
            if line.startswith("Stack trace"):
                trace_mode = True
            else:
                message.append(line)
    out_msg = ""
    if stack_trace:
        out_msg += "Traceback (most recent call last):\n"
        out_msg += "\n".join(reversed(stack_trace)) + "\n"
    out_msg += "\n".join(message)
    return out_msg, err_type


def get_last_ffi_error():
    """Create error object given result of MXGetLastError.
    Returns
    -------
    err : object
        The error object based on the err_msg
    """
    c_err_msg = py_str(_LIB.MXGetLastError())
    py_err_msg, err_type = c2pyerror(c_err_msg)
    if err_type is not None and err_type.startswith("mxnet.error."):
        err_type = err_type[10:]
    return error_types.get(err_type, MXNetError)(py_err_msg)


def check_call(ret):
    """Check the return value of C API call.
    This function will raise an exception when an error occurs.
    Wrap every API call with this function.
    Parameters
    ----------
    ret : int
        return value from API calls.
    """
    if ret != 0:
        raise get_last_ffi_error()


def _load_lib():
    """Load library by searching possible path."""
    lib_path = [os.path.join(os.path.dirname(__file__), "native/libmxnet.so")]
    lib = ctypes.CDLL(lib_path[0], ctypes.RTLD_LOCAL)
    # DMatrix functions
    lib.MXGetLastError.restype = ctypes.c_char_p
    return lib


_LIB = _load_lib()
# type definitions
RecordIOHandle = ctypes.c_void_p

if sys.version_info[0] < 3:
    def c_str(string):
        """Create ctypes char * from a Python string.
        Parameters
        ----------
        string : string type
            Python string.
        Returns
        -------
        str : c_char_p
            A char pointer that can be passed to C API.
        Examples
        --------
        >>> x = c_str("Hello, World")
        >>> print x.value
        Hello, World
        """
        return ctypes.c_char_p(string)
else:
    def c_str(string):
        """Create ctypes char * from a Python string.
        Parameters
        ----------
        string : string type
            Python string.
        Returns
        -------
        str : c_char_p
            A char pointer that can be passed to C API.
        Examples
        --------
        >>> x = c_str("Hello, World")
        >>> print(x.value)
        b"Hello, World"
        """
        return ctypes.c_char_p(string.encode('utf-8'))
