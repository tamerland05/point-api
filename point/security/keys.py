from point.config import settings


class SecurityWalletPrivateKey:
    def __init__(self, seed: bytes) -> None:
        self.__raw_private_key = seed.hex()

    def get_encrypted(self) -> str:
        cipher = settings.merchant_cipher
        key: str = cipher.encrypt(self.__raw_private_key.encode()).decode()
        return key

    @classmethod
    def decrypt_private_key(cls, encrypted_private_key: str) -> str:
        key: str = settings.merchant_cipher.decrypt(encrypted_private_key).decode()
        return key
