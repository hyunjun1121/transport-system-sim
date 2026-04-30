"""Departure policies for transport dispatch.

STRICT: depart at scheduled time, latecomers take follow-on transport.
GRACE: wait up to W minutes or until theta% of expected personnel arrive.
"""

from abc import ABC, abstractmethod


class DeparturePolicy(ABC):
    """Base class for departure policies."""

    @abstractmethod
    def should_depart(
        self,
        elapsed_wait: float,
        arrived_count: int,
        total_expected: int,
        vehicle_capacity: int,
    ) -> bool:
        """Decide whether a vehicle should depart now.

        Args:
            elapsed_wait: minutes elapsed since scheduled departure
            arrived_count: number of personnel who have arrived
            total_expected: total expected personnel for this dispatch
            vehicle_capacity: max passengers per vehicle

        Returns:
            True if vehicle should depart
        """
        ...

    @abstractmethod
    def name(self) -> str:
        ...


class StrictPolicy(DeparturePolicy):
    """Strict on-time departure. Depart immediately at scheduled time."""

    def should_depart(
        self,
        elapsed_wait: float,
        arrived_count: int,
        total_expected: int,
        vehicle_capacity: int,
    ) -> bool:
        return True

    def name(self) -> str:
        return "STRICT"


class GracePolicy(DeparturePolicy):
    """Grace period policy. Wait up to W min or until theta% arrive."""

    def __init__(self, W: float, theta: float):
        self.W = W          # max wait time (min)
        self.theta = theta  # arrival fraction threshold

    def should_depart(
        self,
        elapsed_wait: float,
        arrived_count: int,
        total_expected: int,
        vehicle_capacity: int,
    ) -> bool:
        # Max wait reached
        if elapsed_wait >= self.W:
            return True
        # Enough personnel arrived
        if total_expected > 0 and arrived_count / total_expected >= self.theta:
            return True
        # Vehicle full
        if arrived_count >= vehicle_capacity:
            return True
        return False

    def name(self) -> str:
        return f"GRACE_W{self.W}_T{self.theta}"


def build_policies(config: dict) -> list[DeparturePolicy]:
    """Build all policy instances from config."""
    policies = []
    for pname, pconf in config["policies"].items():
        if pconf["type"] == "strict":
            policies.append(StrictPolicy())
        elif pconf["type"] == "grace":
            for W in pconf.get("W", [30]):
                for theta in pconf.get("theta", [0.9]):
                    policies.append(GracePolicy(W=W, theta=theta))
    return policies
