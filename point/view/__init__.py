import faker

from .base import PointBase
from .common import PointRequestIn, PointUploadIn, PointOut, PointWithScale, Cost
from .earn import *
from .map import *
from .selection import *
from .task import *
from .account import *
from .tip import *
from .admin import *

from .utils import random_address

fake = faker.Faker()
