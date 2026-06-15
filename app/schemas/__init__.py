from .divisions import DivisionRead, DivisionWithVlansRead
from .vlans import VlanRead, VlanWithDivisionsRead

VlanWithDivisionsRead.model_rebuild()

__all__ = [
    "DivisionRead",
    "DivisionWithVlansRead",
    "VlanRead",
    "VlanWithDivisionsRead",
]
