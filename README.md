# Log external/public IP address changes

Detect when your external IP changes and log the changes to a CSV file.

If you do not have a static IP assigned by your ISP and you want to track changes as new IP address is assigned to your connection then use this script.

## Caveat:
The script does not auto detect the IP address change instantly as it happens.

Instead it queries public IP address at a regular configurable interval (60 seconds by default). See the [**Options**](https://github.com/bijalthanawala/external_ip_logger#options) for details.

## Simple Usage:
### On a Linux platform
```
./external_ip_logger.py
```

#### Simple Usage Run<sup>*</sup>
```
$ ./external_ip_logger.py
Logging IP address changes to external_ip_logger_20240526_122045.csv
Querying public IP from https://ifconfig.me every 60 seconds
Public IP address 6x.7x.2x2.8x - observed last at Sun May 26 12:21:49 2024
Public IP address 1x0.x1.x26.2x1 - observed last at Sun May 26 12:25:50 2024
<Press CTRL-C to terminate the scripti anytime>

$ # View the generated CSV file anytime
$ # The CSV file is updated at every query cycle (60 seconds in this example)
$ cat external_ip_logger_20240526_122045.csv
ip_address,start_time,end_time
6x.6x.2x2.8x,20240526_122048,20240526_122450
1x0.x1.x26.2x1,20240526_122450,20240526_123152
```
<sup>*</sup>Real IP address masked in this sample output


### On a Windows platform
```
<todo - work in progress>
```


## Options
```
./external_ip_logger.py --help
usage: external_ip_logger.py [-h] [--delay DELAY] [--csv_prefix CSV_PREFIX] [--url URL] [--quiet] [--quieter]

options:
  -h, --help            show this help message and exit
  --delay DELAY         Wait specified number of seconds before each check (Default=60)
  --csv_prefix CSV_PREFIX
                        CSV filename prefix e.g. With csv_prefix XYZ, the file created will be XYZ_yyyymmdd_hhmmss.csv
                        (Default=base name of this script)
  --url URL             URL to query public IP from (Default=https://ifconfig.me)
  --quiet               Run quietly - do not show IP updates on console (Default=False)
  --quieter             Run even quieter - do not show the name of the CSV file also. Implies --quiet also (Default=False)
```
