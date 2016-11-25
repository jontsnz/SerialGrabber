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

import logging
import serial, os, os.path, time
from serial_grabber import poster_exceptions
from serial_grabber.poster_exceptions import ConnectionException
from serial_grabber.reader import Reader
from serial.serialutil import SerialException


class SerialConnection:
    """
    Base class for all serial connections.
    """

    def connect(self):
        raise NotImplementedError("connect is required")

    def read(self):
        """
        Single byte reading method
        """
        raise NotImplementedError("read is required")

    def write(self, data):
        """
        Writes data to the serial connection
        """
        raise NotImplementedError("write is required")

    def close(self):
        """
        Closes the connection.
        """
        raise NotImplementedError("close is required")

    def is_connected(self):
        """
        Returns whether the serial connection is currently open
        """
        raise NotImplementedError("is_connected is required")

    def inWaiting(self):
        """
        This method returns the numbering of bytes in the incoming buffer.
        It is required by the XBee module, as it is normally provided by
        pySerial
        """
        raise NotImplementedError("inWaiting is required")


class SerialPort(SerialConnection):
    def __init__(self, port, baud, timeout=60, parity=serial.PARITY_NONE,
                 stop_bits=serial.STOPBITS_ONE):
        """
        :param str port: The serial port to use, eg: /dev/ttyUSB0
        :param int baud: The baud rate to use, eg: 115200
        :param int timeout: eg: 60
        :param int parity: eg: serial.PARITY_NONE
        :param int stop_bits: eg: serial.STOPBITS_ONE
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.parity = parity
        self.stop_bits = stop_bits
        self.con = None

    def connect(self):
        try:
            self.con = serial.Serial(self.port, self.baud,
                                     timeout=self.timeout,
                                     parity=self.parity,
                                     stopbits=self.stop_bits)
        except OSError, e:
            time.sleep(2)
            raise ConnectionException("Port: " + self.port + " does not exists.", e)

        # These are not the droids you are looking for....
        os.system("/bin/stty -F %s %s" % (self.port, self.baud))

    def is_connected(self):
        return self.con is not None and self.con.isOpen()

    def close(self):
        if self.con is not None:
            self.con.close()
            self.con = None

    def write(self, data):
        if self.con is None:
            raise ValueError("There is no currently open connection")
        self.con.write(data)

    def read(self):
        try:
            return self.stream.read()
        except SerialException, se:
            self.close()
            raise se

    def inWaiting(self):
        return self.stream.inWaiting()


class SerialReader(Reader):
    """
    A reader that connects to the specified serial port for its input.

    :param transaction_extractor: The transaction extractor used to parse the input stream.
    :type transaction_extractor: :py:class:`serial.grabber.reader.TransactionExtractor`
    :param int startup_ignore_threshold_milliseconds: The interval that input is ignored for at startup
    """
    def __init__(self, transaction_extractor,
                 startup_ignore_threshold_milliseconds, serial_connection):
        Reader.__init__(self, transaction_extractor, startup_ignore_threshold_milliseconds)
        self.serial_connection = serial_connection

    def try_connect(self):
        logger = logging.getLogger("SerialConnection")
        try:
            self.serial_connection.connect()
            if self.serial_connection.is_connected():
                self.stream = self.serial_connection
                return
        except serial.SerialException, se:
            time.sleep(2)
            logger.error(se)
            logger.error("Closing port and re-opening it.")
            try:
                if self.serial_connection.is_open():
                    self.serial_connection.close()
                    self.stream = None
            except Exception, e:
                pass
        if not self.serial_connection.is_connected():
            raise poster_exceptions.ConnectionException(
                "Could not connect to port: %s" % self.port)

    def setup(self):
        if self.serial_connection.is_connected():
            self.serial_connection.close()
        self.try_connect()

    def close(self):
        self.serial_connection.close()
        self.stream = None

    def getCommandStream(self):
        return self.stream

    def read_data(self):
        return self.stream.read()
