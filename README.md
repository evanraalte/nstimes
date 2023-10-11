
[![PyPI Version](https://img.shields.io/pypi/v/nstimes.svg)](https://pypi.org/project/nstimes)
![Python Version](https://img.shields.io/badge/Python-3.10%20%E2%86%92%203.12-blue)
![CI/CD](https://github.com/evanraalte/nstimes/actions/workflows/actions.yml/badge.svg)

# `nstimes`

Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.

**Usage**:

```console
$ nstimes [OPTIONS] COMMAND [ARGS]...
```

**Options**:

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
* `--help`: Show this message and exit.

## `nstimes update-stations-json`

**Usage**:

```console
$ nstimes update-stations-json [OPTIONS]
```

**Options**:

* `--token TEXT`: Token to talk with the NS API  [env var: NS_API_TOKEN; required]
* `--help`: Show this message and exit.
