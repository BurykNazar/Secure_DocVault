"""RSA-PSS, PEM-серіалізація та відбиток ключа."""

from __future__ import annotations

import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ALGORITHM = "RSA-PSS-SHA256"
KEY_SIZE = 2048
PUBLIC_EXPONENT = 65537


def generate_keypair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT, key_size=KEY_SIZE
    )
    return private_key, private_key.public_key()


def serialize_public_key(public_key: rsa.RSAPublicKey) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def load_public_key(pem: str) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(pem.encode("ascii"))


def serialize_private_key(
    private_key: rsa.RSAPrivateKey, passphrase: str | None = None
) -> str:
    encryption = (
        serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
        if passphrase
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    ).decode("ascii")


def load_private_key(
    pem: str, passphrase: str | None = None
) -> rsa.RSAPrivateKey:
    password = passphrase.encode("utf-8") if passphrase else None
    return serialization.load_pem_private_key(
        pem.encode("ascii"), password=password
    )


def fingerprint(public_key: rsa.RSAPublicKey) -> str:
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def sign_content(content: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.sign(
        content,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify_content(
    content: bytes, signature: bytes, public_key: rsa.RSAPublicKey
) -> bool:
    try:
        public_key.verify(
            signature,
            content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False
