from point.config import settings


class ServiceWalletPrivateKey:
    def __init__(self, seed: bytes) -> None:
        self.__raw_private_key = seed.hex()

    def get_encrypted(self) -> str:
        return settings.fernet_cipher.encrypt(self.__raw_private_key.encode()).decode()

    @classmethod
    def decrypt_private_key(cls, encrypted_private_key: str) -> str:
        return settings.fernet_cipher.decrypt(encrypted_private_key).decode()
