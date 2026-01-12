from nacl.bindings import crypto_sign_seed_keypair
from pytoniq_core.crypto.keys import mnemonic_new, mnemonic_to_seed
from tonutils.wallet import WalletV5R1

from point.config import settings
from point.security.keys import ServiceWalletPrivateKey

from .ton_network import tns


class WalletService:
    wallet_id = settings.wallet_id
    seed = settings.seed.encode("utf-8")

    @classmethod
    async def create(cls) -> tuple[str, str]:
        mnemonic = mnemonic_new(24)
        seed = mnemonic_to_seed(mnemonic, cls.seed)[:32]
        public_key, private_key = crypto_sign_seed_keypair(seed)
        wallet = WalletV5R1.from_private_key(
            client=tns,
            private_key=private_key,
            wallet_id=cls.wallet_id,
        )

        address = wallet.address.to_str(is_url_safe=True, is_user_friendly=True, is_bounceable=False)

        seed = ServiceWalletPrivateKey(seed).get_encrypted()

        return address, seed
