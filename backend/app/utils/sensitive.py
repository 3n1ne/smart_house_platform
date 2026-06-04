import base64
import hashlib
import hmac
from secrets import token_bytes

from flask import current_app


ENCRYPTED_PREFIX = "enc:v1:"


def _data_key():
    configured = current_app.config.get("SENSITIVE_DATA_KEY")
    secret = configured or current_app.config.get("SECRET_KEY") or "dev-secret-key"
    return hashlib.sha256(str(secret).encode("utf-8")).digest()


def _keystream(key, nonce, length):
    chunks = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < length:
        counter_bytes = counter.to_bytes(4, "big")
        chunks.append(hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest())
        counter += 1
    return b"".join(chunks)[:length]


def encrypt_sensitive(value):
    if value in (None, ""):
        return None
    text = str(value)
    if text.startswith(ENCRYPTED_PREFIX):
        return text

    key = _data_key()
    nonce = token_bytes(16)
    plaintext = text.encode("utf-8")
    stream = _keystream(key, nonce, len(plaintext))
    ciphertext = bytes(left ^ right for left, right in zip(plaintext, stream))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    payload = base64.urlsafe_b64encode(nonce + tag + ciphertext).decode("ascii")
    return f"{ENCRYPTED_PREFIX}{payload}"


def decrypt_sensitive(value):
    if value in (None, ""):
        return None
    text = str(value)
    if not text.startswith(ENCRYPTED_PREFIX):
        return text

    raw = base64.urlsafe_b64decode(text.removeprefix(ENCRYPTED_PREFIX).encode("ascii"))
    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]
    key = _data_key()
    expected_tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(tag, expected_tag):
        return None

    stream = _keystream(key, nonce, len(ciphertext))
    plaintext = bytes(left ^ right for left, right in zip(ciphertext, stream))
    return plaintext.decode("utf-8")


def mask_identity_no(value):
    plain = decrypt_sensitive(value)
    if not plain:
        return None
    if len(plain) <= 6:
        return "*" * len(plain)
    return f"{plain[:2]}{'*' * (len(plain) - 6)}{plain[-4:]}"


def mask_phone(value):
    if not value:
        return None
    text = str(value)
    if len(text) < 7:
        return "*" * len(text)
    return f"{text[:3]}****{text[-4:]}"


def mask_email(value):
    if not value:
        return None
    text = str(value)
    if "@" not in text:
        return text[:2] + "***" if len(text) > 2 else "***"
    local, domain = text.split("@", 1)
    if len(local) <= 2:
        masked_local = f"{local[:1]}***"
    else:
        masked_local = f"{local[:2]}***"
    return f"{masked_local}@{domain}"
