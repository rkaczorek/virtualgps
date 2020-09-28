#!/bin/bash

LOCATION_DIR="/etc/location.conf.d"
LOCATION_FILE="${LOCATION_DIR}/location.conf"
ALL_LOCATIONS="${LOCATION_DIR}/*.conf"

function create {
	if [ -e $LOCATION_FILE ]
	then
		LAT="$(grep latitude $LOCATION_FILE | cut -d\= -f2 | xargs)"
		LON="$(grep longitude $LOCATION_FILE | cut -d\= -f2 | xargs)"
		ELEV="$(grep elevation $LOCATION_FILE | cut -d\= -f2 | xargs)"
		NAM="$(grep name $LOCATION_FILE | cut -d\= -f2 | xargs -0)"
	fi

	DATA=$(zenity --forms --title="Geographic location" \
		--text="Set your geographic location" \
		--separator=";" \
		--add-entry="Latitude ($LAT)" \
		--add-entry="Longitude ($LON)" \
		--add-entry="Elevation ($ELEV)" \
		--add-entry="Name ($NAM)")

	LAT="$(echo $DATA | cut -d\; -f1)"
	LON="$(echo $DATA | cut -d\; -f2)"
	ELEV="$(echo $DATA | cut -d\; -f3)"
	NAM="$(echo $DATA | cut -d\; -f4)"

	if [ "$LAT" != "" ] && [ "$LON" != "" ] && [ "$ELEV" != "" ]  && [ "$NAM" != "" ]
	then
		mkdir -p ${LOCATION_DIR}
		cat > ${LOCATION_FILE} << EOF
[default]
latitude  = $LAT
longitude = $LON
elevation = $ELEV
name = $NAM
EOF
		FILENAM="${NAM//[\w\'\*\+<>\\\/]/_}.conf"
		cat > $LOCATION_DIR/$FILENAM << EOF
[default]
latitude  = $LAT
longitude = $LON
elevation = $ELEV
name = $NAM
EOF
	else
		zenity --error --width=300 --text="One or more blank fields. Creation failed."
	fi
}

function get_locations {
	LOCATIONS=()
	for F in $ALL_LOCATIONS
	do
		if [ "$F" != "$LOCATION_FILE" ]
		then
			N="$(grep name $F | cut -d\= -f2 | xargs)"
			LOCATIONS+=(FALSE "${N}")
		fi
	done
}

function existing {
	if [ -d $LOCATION_DIR ]
	then
		get_locations
		CONFIG=$(zenity --height=300 --list --radiolist --title="Which locations?" --print-column=2 --column="" --column="Location" "${LOCATIONS[@]}")
		if [ "$CONFIG" != "" ]
		then
			sudo cp -p "${LOCATION_DIR}/${CONFIG// /_}.conf" "${LOCATION_FILE}"
		else
			zenity --info --width=300 --text="No change to the location"
		fi
	else
		zenity --error --text="No existing locations"
	fi
}

zenity --question --width=300 --text="Use an existing location?\nChoose No to create a new one."

if [ "$?" = "1" ]
then
	create
else
	existing
fi
