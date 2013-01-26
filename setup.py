#!/usr/bin/env python
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
from distutils.core import setup

setup(
	name = 'sawmill',
	version = '0.0.1',
	description = 'Tiny, composable, generator-based log parsing library.',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/Sawmill/',
    #scripts = [
    #],
	py_modules = [
		'sawmill',
	],
)
