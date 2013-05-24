#!/usr/bin/env python
# SerialGrabber reads data from a serial port and processes it with the
# configured processor.
# Copyright (C) 2012  NigelB
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

class config_helper:

    def __init__(self, config):
        self.config = config

    def __setattr__(self, key, value):
        if key == "config":
            self.__dict__[key] = value
        else:
            self.config[key] = value

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, item):
        self.config[key] = item

    def __delitem__(self, key):
        del self.config[key]

    def __getattr__(self, key):
        if key is "__str__": return self.config.__str__
        elif key is "__repr__": return self.config.__repr__
        elif key is "__iter__": return self.config.__iter__
        elif key is "config_delegate": return self.config
        return self.config[key]

    def __contains__(self, item):
        return self.__getattr__(item)

def locate_resource(name):
    import SerialGrabber_Paths, os.path
    search_path = [
        os.path.dirname(SerialGrabber_Paths.__file__),
        SerialGrabber_Paths.data_logger_dir
    ]

    for sp in search_path:
        path = os.path.join(sp, name)
        if os.path.exists(path):
            return os.path.abspath(path)
    return None