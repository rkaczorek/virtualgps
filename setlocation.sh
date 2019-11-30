#!/bin/bash

if [ -e /etc/location.conf ]
then
	LAT="$(grep latitude /etc/location.conf | cut -d\= -f2 | xargs)"
	LON="$(grep longitude /etc/location.conf | cut -d\= -f2 | xargs)"
	ELEV="$(grep elevation /etc/location.conf | cut -d\= -f2 | xargs)"
fi

DATA=$(zenity --forms --title="Geographic location" \
	--text="Set your geographic location" \
	--separator=";" \
	--add-entry="Latitude ($LAT)" \
	--add-entry="Longitude ($LON)" \
	--add-entry="Elevation ($ELEV)")

LAT="$(echo $DATA | cut -d\; -f1)"
LON="$(echo $DATA | cut -d\; -f2)"
ELEV="$(echo $DATA | cut -d\; -f3)"

if [ "$LAT" != "" ] && [ "$LON" != "" ] && [ "$ELEV" != "" ]
then
	cat > /etc/location.conf << EOF
[default]
latitude  = $LAT
longitude = $LON
elevation = $ELEV
EOF
fi
