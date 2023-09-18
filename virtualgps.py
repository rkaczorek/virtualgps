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

import os, sys, re, signal, time, datetime, argparse, configparser

__author__ = 'Radek Kaczorek'
__copyright__ = 'Copyright 2019 - 2023 Radek Kaczorek'
__license__ = 'GPL-3'
__version__ = '1.2.0'

# default config file
config_file = "/etc/virtualgps.conf"

# default profile name
profile_name = "default"

# default location
latitude, longitude, elevation = "0", "0", "0"

def convert_to_sexagesimal(coord):
	"""
	Convert a string of coordinates using delimiters for minutes ('),
	seconds (") and degrees (º). It also supports colon (:).

		>>> from virtualgps import convert_to_sexagesimal
		>>> convert_to_sexagesimal(u"52:08.25:1.5\"")
		52.13791666666667
		>>> convert_to_sexagesimal(u"52:08:16.5\"")
		52.13791666666667
		>>> convert_to_sexagesimal(u"52.1:02:16.5\"")
		52.13791666666667
		>>> convert_to_sexagesimal(u"52º08'16.5\"")
		52.13791666666667

	:param coord: Coordinates in string representation
	:return: Coordinates in float representation
	"""
	elements = re.split(r'[\u00ba\':\"]', coord)

	degrees = float(elements[0])
	if (len(elements) - 1) > 0:
		# Convert minutes to degrees
		degrees += float(elements[1]) / 60
	if (len(elements) - 1) > 1:
		# Convert seconds to degrees
		degrees += float(elements[2]) / 3600
	return degrees


def nmea_checksum(sentence):
    chsum = 0
    for s in sentence:
        chsum ^= ord(s)
    return hex(chsum)[2:]

def shutdown():
	try:
		os.close(master)
		os.close(slave)
	except:
		pass
	sys.exit()

def term_handler(signum, frame):
	raise KeyboardInterrupt

# register term handler
signal.signal(signal.SIGTERM, term_handler)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Emulates GPS serial device based on virtual location\n')
	parser.add_argument('--config', type=str, help='Configuration file (default=/etc/virtualgps.conf)')
	parser.add_argument('--profile', type=str, help='Configuration profile name (default=default)')
	parser.add_argument('--nmea', type=str, help='NMEA log file to restream')
	parser.add_argument('--lat', type=str, help='Virtual Latitude')
	parser.add_argument('--lon', type=str, help='Virtual Longitude')
	parser.add_argument('--el', type=str, help='Virtual Elevation')
	args = parser.parse_args()

	if args.config:
		config_file = args.config

	if args.profile:
		profile_name = args.profile

	# use location data from config
	if os.path.isfile(config_file):
		config = configparser.ConfigParser()
		config.read(config_file)
		if 'latitude' in config[profile_name] and 'longitude' in config[profile_name] and 'elevation' in config[profile_name]:
			latitude = convert_to_sexagesimal(config[profile_name]['latitude'])
			longitude = convert_to_sexagesimal(config[profile_name]['longitude'])
			elevation = float(config[profile_name]['elevation'])
		else:
			# if config wrong exit
			raise KeyboardInterrupt
	else:
		# if config does not exist exit
		raise KeyboardInterrupt

	# use command line arguments only
	if args.lat:
		latitude = convert_to_sexagesimal(args.lat)

	if args.lon:
		longitude = convert_to_sexagesimal(args.lon)

	if args.el:
		elevation = float(args.el)

	# create pseudo terminal device
	master, slave = os.openpty()
	pty = os.ttyname(slave)

	# set permissions for gpsd
	os.chmod(pty, 0o444)

	# on some systems apparmor allows for gpsfake only /tmp/gpsfake-*.sock
	# we need to handle this by adding pty device to apparmor configuration
	apparmor = "/etc/apparmor.d/usr.sbin.gpsd"
	os.system("sudo aa-complain %s" % apparmor)

	# add device to gpsd
	try:
		os.system("sudo gpsdctl add %s" % pty)
	except:
		print("Error adding %s device to gpsd server", pty)
		sys.exit()

	if args.nmea:
		print("Restreaming NMEA log file %s to serial GPS device %s" % (args.nmea, pty))
	else:
		print("Streaming virtual location (Lat: %s, Lon: %s, El: %s) to serial GPS device %s" % (latitude, longitude, elevation, pty))

	# format for NMEA
	# N or S
	if latitude > 0:
		NS = 'N'
	else:
		NS = 'S'

	# W or E
	if longitude > 0:
		WE = 'E'
	else:
		WE = 'W'

	latitude = abs(latitude)
	longitude = abs(longitude)
	lat_deg = int(latitude)
	lon_deg = int(longitude)
	lat_min = (latitude - lat_deg) * 60
	lon_min = (longitude - lon_deg) * 60
	latitude = "%02d%07.4f" % (lat_deg, lat_min)
	longitude = "%03d%07.4f" % (lon_deg, lon_min)

	while True:
		try:
			# restream nmea log file only
			if args.nmea:
				with open(args.nmea) as f:
					for line in f.readlines():
						os.write(master, line.encode())
						time.sleep(1)
				f.close()
				continue

			now = datetime.datetime.utcnow()
			date_now = now.strftime("%d%m%y")
			time_now = now.strftime("%H%M%S")

			# NMEA minimal sequence:
			#$GPGGA,231531.521,5213.788,N,02100.712,E,1,12,1.0,0.0,M,0.0,M,,*6A
			#$GPGSA,A,1,,,,,,,,,,,,,1.0,1.0,1.0*30
			#$GPRMC,231531.521,A,5213.788,N,02100.712,E,,,261119,000.0,W*72

			nmea = ""

			# assemble nmea sentences
			#nmea += "$PGRMZ,1815,f,3*26\n"
			#nmea += "$PGRMM,WGS 84*06\n"
			#nmea += "$GPBOD,000.6,T,000.0,M,CB,AC*42\n"
			#nmea += "$GPRTE,1,1,c,0,AC,CB,BB*28\n"
			#nmea += "$GPWPL,4804.712,N,01138.270,E,AC*4B\n"
			#nmea += "$GPRMC,133718,A,3412.717,N,01138.281,E,000.0,185.1,140900,000.6,E*76\n"
			#nmea += "$GPRMB,A,0.00,R,AC,CB,3412.999,N,01138.290,E,000.3,001.3,,V*04\n"

			gpgga = "GPGGA,%s,%s,%s,%s,%s,1,12,1.0,%s,M,0.0,M,," % (time_now, latitude, NS, longitude, WE, elevation)
			gpgga = "$%s*%s" % (gpgga, nmea_checksum(gpgga))
			nmea += gpgga + "\n" 

			gpgsa = "GPGSA,A,3,,,,,,,,,,,,,1.0,1.0,1.0"
			gpgsa = "$%s*%s" % (gpgsa, nmea_checksum(gpgsa))
			nmea += gpgsa + "\n"

			gprmc = "GPRMC,%s,A,%s,%s,%s,%s,,,%s,000.0,W" % (time_now, latitude, NS, longitude, WE, date_now)
			gprmc = "$%s*%s" % (gprmc, nmea_checksum(gprmc))
			nmea += gprmc + "\n"

			nmea += "$GPGSV,2,1,08,05,18,052,48,16,22,303,00,18,63,159,44,21,62,175,49*7A\n"
			nmea += "$GPGSV,2,2,08,25,24,128,40,26,53,299,00,29,54,061,51,31,43,231,00*73"
			#nmea += "$PGRME,38.9,M,40.2,M,55.9,M*13\n"
			#nmea += "$GPGLL,3412.717,N,01138.281,E,133719,A*2C"

			for sentence in nmea.split("\n"):
				sentence += "\n"
				os.write(master, sentence.encode())
				time.sleep(0.01)

			time.sleep(1)

		except KeyboardInterrupt:
			shutdown()
