# crate-signatures

Experiments in signing RO-Crates

## Installation

```
$ python -m pip install .
```


## What this does...

This is a demonstration of one approach to adding a "self-contained" signature to an RO-Crate.

There are two main steps to this process:
  1. A credentials record is added to the RO-Crate using (broadly) the format
     proposed in [ro-crate#282](https://github.com/ResearchObject/ro-crate/issues/282).
     This contains a base64 representation of the public key corresponding to
     the private key which will subsequently be used to sign the document.
  2. The whole document, including the record added in (1) above, is serialised
     and a signature added to the above credential record. This allows the embedded
     public key to be used to validate the document, at the point immediately before
     addition of the signature.

Several issues with this approach can be observed:
  1. The serialisation procedure prior to signing must be consistent across all
     platforms and implementations which perform this operation.
  2. Large blocks of ugly base64 appear in the json-ld.
  3. Subsequent modification of the document is not precluded if further signatures are
     added. As such, the validation process must be aware of the times at which signing(s)
     was (were) performed.
  4. Signing *all* the contents of a RO-Crate and not merely the json metadata using this
     method requires that a hash digest for all of those contents appears in the json
     prior to signing.

### Example

The operation...

```
$ crate-signature sign data/ro-crate-metadata.json data/example_private_key.pem
```

...performed on the supplied example RO-Crate and using the example signing key adds
the following credential record to the `ro-crate-metadata.json`.

``` json
{
      "@id": "https://example.ac.uk/credential",
      "@type": [
        "VerifiableCredential",
        "RoCrateCredential"
      ],
      "issuer": {
        "@id": "https://orcid.org/0009-0009-5499-2096"
      },
      "issuanceDate": "2026-03-12T10:06:14",
      "credentialSubject": "ro-crate-metadata.json",
      "rsaPublicKey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqMyv47T6F0k/KsQAVflBGNPzs4gIHQ2D0hqSndW5j3DnRCjyyp0nsnOK9qv54s4oQI37e4fcPgpjm9dmC/gs168R4gMGVE9vrZBxZz0ImGRuNn9ypOJaKAeYlRlErT9uPgQxqLZ++aEpBlT9eORMmVfm51/WcQntzI64F+p8tVzgUV+qAFWL/m1Dychv2AozxBk7uB3y+sntMVX2mH13O214PTqUjzAPFRIxf6m+XjLUxJvpZ+mklVZQ//q7nJRqc055xaEsz/klVG3bilZpf3M0R1yFtqePw+CDZE0TxNcCjwxjypZrlRybaVtq7XIlYn07XZGyWX3vohAvNyKuZQIDAQAB",
      "signature": "RvJcpnLB8/rnMeR26wf0sHdP5i++9gOYcrXP140HyE1jxGvqSgVUQ4Imv8dsA1gCWXwdK1EdfxSmacO0rmDz6mOKzBw4wG6wOQrHgdztH4ChZtVtjSc/8NeWuTJmI2B76rOfLGBLu6/uh0rlA+lCxg0IZbfWoTLfeQXaTagW43LpglOO2Zfcy8ZETOnDAiqv9iIyKf5x+UHZ5S+TIxqKqi2Yae7hIIHKnUURyY5mKlCK5zVCHb/oqR/z7YbDAH8dtERpZjRmUb+eohriYfZdGv1lmjMf96vTJh7Zt4LDH5vTk/Ot6X6rDwdkLTJqNV1k0dFXnrJAViixjHgbHCqOWg=="
}
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
