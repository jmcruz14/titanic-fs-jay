from enum import Enum

class PassengerSex(str, Enum):
  male = "male"
  female = "female"

class Pclass(int, Enum):
    first = 1
    second = 2
    third = 3

class Embarked(str, Enum):
    C = "C"
    Q = "Q"
    S = "S"
