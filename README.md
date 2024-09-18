# Virtual GPS
Virtual GPS simulates GPS receiver, which uses configurable geographic location

# How to build it?
Run the following commands:
```
git clone https://github.com/rkaczorek/virtualgps.git
cd virtualgps
python -m build
pip install dist/virtualgps-2.0.0-py3-none-any.whl
```

# How to use it?
Run Virtual GPS from command line:
```
virtual-gps
```

OR

Setup system-wide service:
```
sudo cp virtualgps.service /etc/systemd/system/
sudo systemctl enable virtualgps.service
sudo systemctl start virtualgps.service
```

# How to access Virtual GPS?
Virtual GPS device is linked to pseudoterminal e.g. /dev/pts/0 (available only when virtual-gps is running)

# How to configure virtual location?
You can edit $HOME/.virtualgps file or use command line parameters.
```
usage: virtual-gps [-h] [-c CONFIG] [-p PROFILE] [-n NMEA] [-v] [--version] [--lat LAT] [--lon LON] [--el EL]

Emulates GPS serial device using configurable virtual location

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file (default=$HOME/.virtualgps)
  -p PROFILE, --profile PROFILE
                        Configuration profile name (default=default)
  -n NMEA, --nmea NMEA  NMEA log file to restream
  -v, --verbose         Verbose output (default=false)
  --version             Output version and exit
  --lat LAT             Virtual Latitude (default=0)
  --lon LON             Virtual Longitude (default=0)
  --el EL               Virtual Elevation (default=0)
```

# What's the deal of using Virtual GPS?
If you don't have GPS device but you use applications that require one, you can simulate GPS device with Virtual GPS.
While started it reads location from .virtualgps file and feeds it to gpsd daemon. Any application that uses gpsd
to get location data will use virtual location simulated by Virtual GPS.

# Issues
File any issues on https://github.com/rkaczorek/virtualgps/issues

