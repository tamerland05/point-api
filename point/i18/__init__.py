from pathlib import Path

from quicki18n import i18n

translate = i18n(
    languages=["en", "ru"],
    translations_path=Path(__file__).parent / "translation",
)
