import argparse
import base64
import datetime
import json
import pathlib
import sys

from io import BytesIO

from cryptography.hazmat.primitives import (
    hashes,
    serialization
)
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def read_json(filename):
    with open(filename, 'r') as fp:
        src = json.load(fp)

    return src


def print_json(src):
    jstr = json.dumps(src, indent=2)
    print(jstr)


def read_priv_key(priv_keyfile):
    with open(priv_keyfile, 'rb') as fp:
        priv_key = serialization.load_pem_private_key(fp.read(), password=None)

    return priv_key


def sign_message(priv_key, msg):
    pad_opts = padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
               )

    signature = priv_key.sign(msg, pad_opts, hashes.SHA256())
    return signature


def make_public_pem(priv_key):
    pub_key = priv_key.public_key()
    pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
          )
    return pem


def make_pubkey_from_pem(pub_pem):
    pem_buf = BytesIO(pub_pem.encode())
    return serialization.load_pem_public_key(pem_buf.read())


def hash_key(key_bytes):
    h256 = hashes.Hash(hashes.SHA256())
    h256.update(key_bytes)
    return h256.finalize()


def add_credential_record(src, priv_key):
    record = {
        "@id": "https://example.ac.uk/credential",
        "@type": ["VerifiableCredential", "RoCrateCredential"],
        "issuer": { "@id": "https://orcid.org/0009-0009-5499-2096"},
        "issuanceDate": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S"),
        "credentialSubject": "ro-crate-metadata.json"
    }
    pub_pem = make_public_pem(priv_key)
    key_body = b"".join(pub_pem.split(b'\n')[1:-2])
    record["rsaPublicKey"] = key_body.decode()
    src["@graph"].append(record)
    sig = sign_message(priv_key, bytes(str(src), encoding="utf8"))
    record["signature"] = base64.b64encode(sig).decode()


def find_credential_record(src):
    type_key = "RoCrateCredential"
    for v in src["@graph"]:
        if types := v.get("@type"):
            for t in types:
                if t == type_key:
                    return v
    return


def build_pem_key(pubkey_b64):
    pem_prefix = "-----BEGIN PUBLIC KEY-----"
    pem_suffix = "-----END PUBLIC KEY-----"
    blocks, rem = divmod(len(pubkey_b64), 64)
    pem_body = [pubkey_b64[i*64:(i+1)*64] for i in range(blocks+1)]
    pem_lines = [pem_prefix, *pem_body, pem_suffix]
    return '\n'.join(pem_lines)


def validate_signature(src):
    record = find_credential_record(src)
    pubkey = record["rsaPublicKey"]
    signature = record.pop("signature")
    pub_pem = build_pem_key(pubkey)
    pub_key = make_pubkey_from_pem(pub_pem)
    sig_bytes = base64.b64decode(signature.encode())
    pad_opts = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                           salt_length=padding.PSS.MAX_LENGTH)
    pub_key.verify(sig_bytes, bytes(str(src), encoding="utf8"),
                   pad_opts, hashes.SHA256())


def sign_crate(filename, keyfile):
    src = read_json(filename)
    priv_key = read_priv_key(keyfile)
    msg = bytes(str(src), encoding="utf8")
    sign_message(priv_key, msg)
    add_credential_record(src, priv_key)
    print_json(src)
    sys.exit(0)


def validate_crate(filename):
    src = read_json(filename)
    try:
        validate_signature(src)
    except InvalidSignature:
        print("Invalid signature", file=sys.stderr)
        sys.exit(1)

    print("Valid signature")
    sys.exit(0)


def parse_args(argv):
    parser = argparse.ArgumentParser(
                prog="crate-signature",
                description="Experiments in RO-Crate signing"
             )
    sp = parser.add_subparsers(title="mode", dest="command")

    sp_sign = sp.add_parser("sign", help="Sign an RO-Crate")
    sp_sign.add_argument("filename", type=pathlib.Path,
                         help="Filename of RO-Crate to sign")
    sp_sign.add_argument("keyfile", type=pathlib.Path,
                         help="Private key in PEM format")

    sp_valid = sp.add_parser("validate", help="Validate an RO-Crate")
    sp_valid.add_argument("filename", type=pathlib.Path,
                          help="Filename of signed RO-Crate to validate")

    if len(argv) == 1:
        parser.print_help()
        parser.exit(0)

    return parser.parse_args()


def handle_args(args):
    if args.command == "sign":
        sign_crate(args.filename, args.keyfile)
    elif args.command == "validate":
        validate_crate(args.filename)

def main():
    args = parse_args(sys.argv)
    handle_args(args)

if __name__ == "__main__":
    main()
