'''
This file is part of the Sawmill library.

The Sawmill library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Sawmill library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Sawmill library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

import re
import gzip
import shlex, subprocess
import os, os.path

# =============================================================================
# Sources
# =============================================================================

def cat(source):
    '''
    Takes a set of filenames or file-like objects, and outputs the file
    contents line by line.
    '''
    for item in source:
        if is_filelike(item):
            for line in item:
                yield line
            
        with open(item, 'r') as fileobj:
            for line in fileobj:
                yield line

def gzcat(source):
    '''
    Opens files in gzip format.
    '''
    for item in source:
        if is_filelike(item):
            for line in item:
                yield line
            
        with gzip.GzipFile(item, 'r') as fileobj:
            for line in fileobj:
                yield line

def system(source):
    '''
    Calls an external process for each source item.

    If item is a string, it is passed to a shell process.
    If item is an array, it is used as argv.

    Returns subprocess.Popen() object.
    '''
    for item in source:
        if isinstance(item, basestring):
            argv = shlex.split(item)
        else:
            argv = list(item)
        yield subproces.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def system_stdout(source):
    '''
    Convenience function for getting each line of output of each system call.
    '''
    return cat( dig( system(source), 'stdout', dictstyle=False) )

def listdir(path):
    '''
    List all files and directories at the given path.

    Protip: filter these with files() and/or dirs().
    '''
    return (os.path.join(path, item) for item in os.listdir(path))

def listdirs(source):
    '''
    Take a list of paths, and expand each with listdir.
    '''
    for path in source:
        for item in listdir(path):
            yield item

# =============================================================================
# Filters
# =============================================================================

def once(source, *callbacks):
    '''
    Call one or more callbacks for each source item, stopping at first non-None
    value returned by a callback and passing that on.

    Does not pass on anything if final result is None.
    '''
    for item in source:
        result = None
        for callback in callbacks:
            result = callback(item)
            if result != None:
                yield result
                break

def grep(source, pattern, category=None, invert=False):
    '''
    Filter items by a regular expression pattern, on the items themselves,
    or on a property they contain. Properties are selected with dict syntax.

    Find is more efficient if you don't need advanced regex stuff.
    '''
    pattern = re.compile(pattern)
    if category == None:
        for item in source:
            if bool(pattern.search(item)) ^ invert:
                yield item
    else:
        for item in source:
            if bool(pattern.search(item[category])) ^ invert:
                yield item

def find(source, pattern, category=None, invert=False):
    '''
    Filter items by a substring, on the items themselves, or on a property
    they contain. Properties are selected with dict syntax.

    Find is more efficient than grep, using the "in" keyword.
    '''
    if category == None:
        for item in source:
            if bool(pattern in item) ^ invert:
                yield item
    else:
        for item in source:
            if bool(pattern in item[category]) ^ invert:
                yield item

def dig(source, category, dictstyle=True):
    '''
    Dig out a property from each item.

    When dictstyle is true, retrieve by item[category]. Otherwise, getattr.
    '''
    if dictstyle:
        for item in source:
            yield item[category]
    else:
        for item in source:
            yield getattr(item, category)

def files(source):
    '''
    Takes a series of paths, and only passes on the ones that point to files.
    '''
    for item in source:
        if os.path.isfile(item):
            yield item

def dirs(source):
    '''
    Takes a series of paths, and only passes on the ones that point to
    directories.
    '''
    for item in source:
        if os.path.isdir(item):
            yield item

# =============================================================================
# Sinks
# =============================================================================

def write(source, filename):
    '''
    Output every item in source to a file, separated by newlines.
    '''
    with open(filename, 'w') as fileobj:
        for item in source:
            f.write(str(item) + "\n")

# =============================================================================
# Utility
# =============================================================================

def is_filelike(item):
    return hasattr(item, 'read') and hasattr(item, 'write')
