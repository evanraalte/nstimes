
[![PyPI Version](https://img.shields.io/pypi/v/nstimes.svg)](https://pypi.org/project/nstimes)
![Python Version](https://img.shields.io/badge/Python-3.10%20%E2%86%92%203.12-blue)
![CI/CD](https://github.com/evanraalte/nstimes/actions/workflows/actions.yml/badge.svg)
![Coverage](coverage.svg)

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
* `update-stations-json`

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
* `--time TEXT`: Time to departure (%H:%M)  [default: 13:30]
* `--date TEXT`: Date to departure (%d-%m-%Y)  [default: 12-10-2023]
* `--print-table`: Print table instead of text
* `--help`: Show this message and exit.

## `nstimes update-stations-json`

**Usage**:

```console
$ nstimes update-stations-json [OPTIONS]
```

**Options**:

* `--token TEXT`: Token to talk with the NS API  [env var: NS_API_TOKEN; required]
* `--help`: Show this message and exit.
