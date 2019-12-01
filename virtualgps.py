#!/usr/bin/env python3
# coding=utf-8

# Virtual GPS simulates GPS receiver available on pseudo terminal
#
# Copyright(c) 2019 Radek Kaczorek  <rkaczorek AT gmail DOT com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License version 3 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file COPYING.LIB.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import os, sys, signal, time, datetime, configparser

__author__ = 'Radek Kaczorek'
__copyright__ = 'Copyright 2019  Radek Kaczorek'
__license__ = 'GPL-3'
__version__ = '1.0.0'

config_file = "/etc/location.conf"
virtualgps_dev = "/tmp/virtualgps"

def nmea_checksum(sentence):
    chsum = 0
    for s in sentence:
        chsum ^= ord(s)
    return hex(chsum)[2:]

def shutdown():
	os.close(master)
	os.close(slave)
	os.remove(virtualgps_dev)
	os.system("gpsdctl remove /tmp/virtualgps")
	sys.exit()

def term_handler(signum, frame):
	raise KeyboardInterrupt

# register term handler
signal.signal(signal.SIGTERM, term_handler)

if __name__ == '__main__':
	# create pseudo terminal device
	master, slave = os.openpty()
	pty = os.ttyname(slave)

	# create symlink to pseudo terminal device
	if os.path.islink(virtualgps_dev) or os.path.isfile(virtualgps_dev):
		os.remove(virtualgps_dev)
	os.symlink(pty,virtualgps_dev)

	# add virtual gps to gpsd
	os.system("gpsdctl add /tmp/virtualgps")

	# load location data from config
	if os.path.isfile(config_file):
		config = configparser.ConfigParser()
		config.read(config_file)
		if 'latitude' in config['default'] and 'longitude' in config['default'] and 'elevation' in config['default']:
			latitude = float(config['default']['latitude'])
			longitude = float(config['default']['longitude'])
			elevation = float(config['default']['elevation'])
		else:
			# if config wrong exit
			raise KeyboardInterrupt
	else:
		# if config does not exist exit
		raise KeyboardInterrupt

	# W or E
	if latitude > 0:
		NS = 'N'
	else:
		NS = 'S'

	# N or S
	if longitude > 0:
		WE = 'E'
	else:
		WE = 'W'

	# format for NMEA
	lat_deg = int(latitude)
	lon_deg = int(longitude)
	lat_min = (latitude - lat_deg) * 60
	lon_min = (longitude - lon_deg) * 60
	latitude = "%d%07.4f" % (lat_deg, lat_min)
	longitude = "%d%07.4f" % (lon_deg, lon_min)

	while True:
		try:
			now = datetime.datetime.utcnow()
			date_now = now.strftime("%d%m%y")
			time_now = now.strftime("%H%M%S")

			# assemble nmea sentences
			# NMEA minimal sequence:
			#$GPGGA,231531.521,5213.788,N,02100.712,E,1,12,1.0,0.0,M,0.0,M,,*6A
			#$GPGSA,A,1,,,,,,,,,,,,,1.0,1.0,1.0*30
			#$GPRMC,231531.521,A,5213.788,N,02100.712,E,,,261119,000.0,W*72
			gpgga = "GPGGA,%s,%s,%s,%s,%s,1,12,1.0,%s,M,0.0,M,," % (time_now, latitude, NS, longitude, WE, elevation)
			gpgsa = "GPGSA,A,3,,,,,,,,,,,,,1.0,1.0,1.0"
			gprmc = "GPRMC,%s,A,%s,%s,%s,%s,,,%s,000.0,W" % (time_now, latitude, NS, longitude, WE, date_now)

			# add nmea checksums
			gpgga = "$%s*%s\n" % (gpgga, nmea_checksum(gpgga))
			gpgsa = "$%s*%s\n" % (gpgsa, nmea_checksum(gpgsa))
			gprmc = "$%s*%s\n" % (gprmc, nmea_checksum(gprmc))

			os.write(master, gpgga.encode())
			os.write(master, gpgsa.encode())
			os.write(master, gprmc.encode())

			time.sleep(1)
		except KeyboardInterrupt:
			shutdown()
