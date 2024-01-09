# Virtual Gps
Virtual GPS simulates GPS receiver, which uses configurable geographic location

# How to use it?
Run Virtual GPS from command line as gpsd user:
```
sudo -u gpsd python3 virtualgps.py
```

OR

Setup system-wide service:
```
sudo cp virtualgps.py /usr/bin/
sudo cp virtualgps.service /etc/systemd/system/
sudo systemctl enable virtualgps.service
sudo systemctl start virtualgps.service
```
Note: Running virtualgps.py as gpsd user ensures that gpsd daemon can access /tmp/virtualgps device.
If you run the application as any other user, make sure that access rights are set properly.

Debian package with Virtual GPS is available from [www.astroberry.io](https://www.astroberry.io).

# How to access Virtual GPS?
Virtual GPS device is linked to /tmp/virtualgps file (only when virtualgps.py is running)

# How to configure virtual location?
You can edit /etc/virtualgps.conf file or use Preferences/Geographic Location menu

# What's the deal of using Virtual GPS?
If you don't have GPS device but you use applications that require one, you can simulate GPS device with Virtual GPS.
While started it reads location from /etc/virtualgps.conf file and feeds it to gpsd daemon. Any application that
can get location form gpsd will use your location from configuration file.

# Issues
File any issues on https://github.com/rkaczorek/virtualgps/issues

