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

# All publicly-accessible functions

__all__ = [

    # Sources
    'cat',
    'gzcat',
    'system',
    'system_stdout',
    'listdir',
    'listdirs',

    # Filters
    'once',
    'grep',
    'find',
    'dig',
    'columns',
    'uncolumns',
    'files',
    'dirs',

    # Sinks
    'write',
    'count',
    'frequency',
    'top_frequency',
    'print_frequency',

    # Recipes
    'clever_cat',
    'http_log',
    'apache2',
    'nginx',
    'highest_pageviews',

    # Utility
    'is_filelike',
    'forever',
]

NGINX_COLUMNS = ("ip","ident","authuser","date","request","status","bytes")

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

def columns(source, sep, column_names, splitter_type='split'):
    '''
    Turn columnized string data into dicts.

    >>> data = [
    ...     "a b c",
    ...     "x y z",
    ... ]
    >>> list(columns(data, " ", ('Left', None, 'Right')))
    [{'Left':'a','Right':'c'},{'Left':'x','Right':'z'}]
    '''
    num_columns = len(column_names)
    if splitter_type == "split":
        splitter = lambda x: x.split(sep, maxsplit=num_columns)
    elif splitter_type == "shlex":
        splitter = lambda x: shlex.split(x)
    else:
        raise ValueError("Unrecognized splitting mechanism", splitter_type)

    for item in source:
        column_values = splitter(item)
        output_dict = {}
        for i in range(num_columns):
            name = column_names[i]
            value = column_values[i]
            if name != None:
                output_dict[name] = value
        yield output_dict

def uncolumns(source, sep, column_names):
    '''
    Turn dict items into columnized strings.
    '''
    for item in source:
        yield sep.join(item[name] for name in column_names)

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

def count(source):
    '''
    Return the number of items in the source.
    '''
    result = 0
    for item in source:
        result += 1
    return result

def frequency(source):
    '''
    Tally for each item in source, returning final count at the end.
    '''
    counts = {}
    for item in source:
        if not item in counts:
            counts[item] = 0
        counts[item] += 1
    return counts

def top_frequency(freq_dict, limit=None, ascending=False):
    '''
    Turn a frequency dict into a (key, value) stream of highest-value elements.
    '''
    sortlist = sorted(freq.iteritems(), key=lambda x:x[1], reverse=True)
    if limit != None:
        sortlist = sortlist[:limit]
    for item in sortlist:
        yield item

def print_frequency(source, limit=None):
    '''
    Print frequency chart.
    '''
    freq = frequency(source)
    sortlist = top_frequency(freq, limit)

    count_width = 5 # "count" is 5 letters
    if sortlist:
        count_width = max(5, len(str(sortlist[0][1]))) # First count is highest
    yield "count" + (" " * (count_width - 4 )) + "value"
    yield "=" * (count_width + 6)
    for value, total in sortlist:
        yield " " * (count_width - len(str(total))) + str(total) + " " + repr(value)

# =============================================================================
# Recipes
# =============================================================================

def clever_cat(source):
    '''
    Determine wrapper format by filename and delegate to correct cat generator.
    '''
    for path in source:
        if path.endswith('.gz'):
            cat_generator = gzcat
        else:
            cat_generator = cat
        for line in cat_generator((path)):
            yield line

def http_log(logdir, filter='access.log'):
    '''
    Get your system webserver CLF logs, with a find filter on filenames.
    '''
    file_list = find(files(listdir(logdir)), filter)
    return columns(
        clever_cat(file_list),
        "",
        CLF_COLUMNS,
        splitter_type = "shlex"
    )

def apache2(logdir='/var/log/apache2', filter='access.log'):
    '''
    Get your system apache2 logs, with a find filter on filenames.
    '''
    return http_log(logdir, filter)

def nginx(logdir='/var/log/nginx', filter='access.log'):
    '''
    Get your system nginx logs, with a find filter on filenames.
    '''
    return http_log(logdir, filter)

def highest_pageviews(source, limit=10):
    '''
    Takes items that are Common Log Format dicts, returns a frequency analysis
    of the request lines.
    '''
    return top_frequency(frequency(dig(source, 'request')), limit=limit)

# =============================================================================
# Utility
# =============================================================================

def is_filelike(item):
    return hasattr(item, 'read') and hasattr(item, 'write')

def forever(callback):
    '''
    A generator that refills from the same callback after each exhaustion.
    '''
    while True:
        internal_gen = callback()
        for item in internal_gen:
            yield item
