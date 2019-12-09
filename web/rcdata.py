# -*-coding:UTF-8–*-

from enum import Enum


class Shape_Type(Enum):
    REC = 0
    T = 1
    CIR = 2
    RING = 3


class Mode(Enum):
    GZH = 1
    GB = 2


class RC_Type(Enum):
    C15 = 0
    C20 = 1
    C25 = 2
    C30 = 3
    C35 = 4
    C40 = 5
    C45 = 6
    C50 = 7
    C55 = 8
    C60 = 9
    C65 = 10
    C70 = 11
    C75 = 12
    C80 = 13


class Steel_Type(Enum):
    HPB300 = 0
    HRB335 = HRBF335 = 1
    HRB400 = HRBF400 = RRB400 = 2
    HRB500 = HRBF500 = 3
