
[![PyPI Version](https://img.shields.io/pypi/v/nstimes.svg)](https://pypi.org/project/nstimes)
![Python Version](https://img.shields.io/badge/Python-3.10%20%E2%86%92%203.12-blue)
![CI/CD](https://github.com/evanraalte/nstimes/actions/workflows/actions.yml/badge.svg)
![Coverage](coverage.svg)


# `nstimes`

Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.

**Usage**:

```console
$ nstimes [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Print version info
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `journey`: Provide train type, platform and departure...
* `update-stations-json`: Generate stations lookup

## `nstimes journey`

Provide train type, platform and departure times of an A -> B journey

**Usage**:

```console
$ nstimes journey [OPTIONS]
```

**Options**:

* `--start TEXT`: Start station  [required]
* `--end TEXT`: Stop station  [required]
* `--token TEXT`: Token to talk with the NS API  [env var: NS_API_TOKEN; required]
* `--time TEXT`: Time to departure (%H:%M)  [default: 12:19]
* `--date TEXT`: Date to departure (%d-%m-%Y)  [default: 15-10-2023]
* `--printer-choice [table|ascii|pixelclock]`: [default: ascii]
* `--help`: Show this message and exit.

## `nstimes update-stations-json`

Generate stations lookup, should not be neccesary

**Usage**:

```console
$ nstimes update-stations-json [OPTIONS]
```

**Options**:

* `--token TEXT`: Token to talk with the NS API  [env var: NS_API_TOKEN; required]
* `--path TEXT`: Token to talk with the NS API  [env var: NS_API_TOKEN; default: /home/erik/dev/ns_cli/nstimes/stations.json]
* `--help`: Show this message and exit.



**Installation**

To install, run the following:
```bash
pip install nstimes
```

To verify, run:
```bash
nstimes --version
```

To install auto-completion, run:
```bash
nstimes --install-completion
```

In order for autocomplete to work, one might need to add this to their `.zshrc`:
```bash
echo -e "\ncompinit -D\n" | tee -a ~/.zshrc
source ~/.zshrc # Reload shell
```

**Obtaining NS token**
Create an account at the [NS API portal](https://apiportal.ns.nl/signin).
Then create a token [here](https://apiportal.ns.nl/api-details#api=reisinformatie-api).

Add the token to your shell:
```bash
echo -e "\nexport NS_API_TOKEN=****\n" | tee -a ~/.zshrc
source ~/.zshrc # Reload shell
```


**Printers**
By default, this tool prints in ASCII, e.g.:
```bash
IC  p.  6 in  6 min (12:28)
IC  p.  6 in 18 min (12:40)
SPR p.  6 in 27 min (12:49)
IC  p.  6 in 36 min (12:58)
IC  p.  6 in 48 min (13:10)
```
If you use the `--printer-choice table` option it prints like:
```bash
  Journeys from Amersfoort Centraal -> Utrecht
          Centraal at 15-10-2023 12:23
┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Train ┃ Platform ┃ Leaves in ┃ Departure time ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ IC    │        6 │     4 min │          12:28 │
│ IC    │        6 │    16 min │          12:40 │
│ SPR   │        6 │    25 min │          12:49 │
│ IC    │        6 │    34 min │          12:58 │
│ IC    │        6 │    46 min │          13:10 │
└───────┴──────────┴───────────┴────────────────┘
```
It also has support for printing on the [Pixel Clock](https://github.com/Blueforcer/awtrix-light). You just need to add the IP of the clock to your environment variables, e.g. `export PIXEL_CLOCK_IP=192.168.0.100`.
