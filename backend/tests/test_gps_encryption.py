from app.core.encryption import decrypt_credentials, encrypt_credentials


def test_encrypt_decrypt_roundtrip() -> None:
    original = {"api_key": "abc123", "account_id": "traker-9"}
    encrypted = encrypt_credentials(original)
    assert isinstance(encrypted, bytes)
    assert b"abc123" not in encrypted  # nunca texto plano en el blob encriptado

    decrypted = decrypt_credentials(encrypted)
    assert decrypted == original
