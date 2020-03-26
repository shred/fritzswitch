# fritzswitch

fritzswitch is a small python command line tool for controlling Fritz!Box home automation, especially Fritz!DECT remote controlled wallplugs.

## Invocation

fritzswitch accepts these parameters:

* `-u`, `--user`: Login user name (default: `admin`)
* `-p`, `--password`: Password for logging in, required
* `-H`, `--host`: Host name of the FritzBox to connect to (default: `fritz.box`)
* `-l`, `--list`: List all available AIDs
* `-a`, `--ain`: Select AIN to control
* `-0`, `--off`: Turn AIN off
* `-1`, `--on`: Turn AIN on
* `-t`, `--toggle`: Toggle AIN
* `-s`, `--state`: Show current AIN state
* `-X`, `--xml`: Output current AIN state as XML
* `-tt`, `--temperature`: Outputs the current AIN temperature. If no AIN is provided, returns a list of all AINs providing a temperature reading.

## License

This sofware is licensed under GNU General Public License V3.
