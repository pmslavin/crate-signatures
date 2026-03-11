# crate-signatures

Experiments in signing RO-Crates

## Installation

```
$ python -m pip install .
```

## Usage

```
$ crate-signature -h
usage: crate-signature [-h] {sign,validate} ...

Experiments in RO-Crate signing

options:
  -h, --help       show this help message and exit

mode:
  {sign,validate}
    sign           Sign an RO-Crate
    validate       Validate an RO-Crate
```

### Sign

```
$ crate-signature sign data/ro-crate-metadata.json data/example_private_key.pem
```

### Validate

```
$ crate-signature validate signed_create.json
```
