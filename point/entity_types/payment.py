from enum import StrEnum


class PaymentTagType(StrEnum):
    stars = "stars"
    establishment_rating = "establishment_rating"

    stars_establishment_rating = f"{stars}.{establishment_rating}"

