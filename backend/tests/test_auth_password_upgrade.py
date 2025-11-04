import hashlib

from backend.auth import (
    hash_password,
    verify_and_upgrade_password,
    is_bcrypt_hash,
)
from backend.models import User


def test_verify_bcrypt_marks_flag_false():
    plaintext = "StrongPass!123"
    user = User(
        username="tester",
        password_hash=hash_password(plaintext),
        password_hash_is_legacy=True,
    )

    assert verify_and_upgrade_password(plaintext, user) is True
    assert user.password_hash_is_legacy is False
    assert is_bcrypt_hash(user.password_hash)


def test_verify_legacy_rehashes_and_marks_flag():
    plaintext = "LegacyPass!123"
    legacy_hash = hashlib.sha256(plaintext.encode()).hexdigest()
    user = User(
        username="legacy",
        password_hash=legacy_hash,
        password_hash_is_legacy=True,
    )

    assert verify_and_upgrade_password(plaintext, user) is True
    assert user.password_hash_is_legacy is False
    assert is_bcrypt_hash(user.password_hash)
    assert user.password_hash != legacy_hash
