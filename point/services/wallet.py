from nacl.bindings import crypto_sign_seed_keypair
from tonsdk.contract.wallet import WalletV4ContractR2
from tonsdk.crypto._mnemonic import mnemonic_new, mnemonic_to_seed

from point.config import settings
from point.security.keys import SecurityWalletPrivateKey


class ServiceWalletController:
    wallet_id = settings.wallet_id
    seed = settings.seed.encode("utf-8")

    @classmethod
    async def create(cls) -> (str, str):
        mnemonic = mnemonic_new(24)
        seed = mnemonic_to_seed(mnemonic, cls.seed)[:32]
        public_key, private_key = crypto_sign_seed_keypair(seed)
        wallet = WalletV4ContractR2(
            private_key=private_key,
            public_key=public_key,
            wallet_id=cls.wallet_id,
        )

        address = wallet.address.to_string(is_url_safe=True, is_user_friendly=True, is_bounceable=False)

        seed = SecurityWalletPrivateKey(seed).get_encrypted()

        return address, seed
