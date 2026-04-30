"""Metrics collector for simulation KPIs."""

from dataclasses import dataclass, field


@dataclass
class MetricsCollector:
    """Collects KPIs during a simulation run.

    KPIs:
        - makespan: time when last person arrives at D (min)
        - success_count: number of personnel who reached D within time limit
        - total_personnel: total personnel in scenario
        - bus_trips: number of bus dispatches used
        - train_trips: number of train dispatches used
        - bus_minutes: total bus operating time (min)
        - train_minutes: total train operating time (min)
        - lastmile_minutes: total last-mile vehicle time (min)
        - leftover_count: personnel not transported (stranded)
    """

    total_personnel: int = 0
    time_limit: float = 1440.0

    # Arrival records: (person_id, arrival_time_at_D)
    arrivals: list[tuple[int, float]] = field(default_factory=list)

    # Resource usage
    bus_trips: int = 0
    train_trips: int = 0
    bus_minutes: float = 0.0
    train_minutes: float = 0.0
    lastmile_minutes: float = 0.0

    # Personnel still waiting at end
    leftover_count: int = 0

    def record_arrival(self, person_id: int, arrival_time: float) -> None:
        self.arrivals.append((person_id, arrival_time))

    @property
    def makespan(self) -> float:
        """Time when last person arrives at D."""
        if not self.arrivals:
            return float("inf")
        return max(t for _, t in self.arrivals)

    @property
    def success_count(self) -> int:
        """Personnel who arrived at D within time limit."""
        return sum(1 for _, t in self.arrivals if t <= self.time_limit)

    @property
    def success_rate(self) -> float:
        """Fraction of total personnel successfully delivered."""
        if self.total_personnel == 0:
            return 0.0
        return self.success_count / self.total_personnel

    @property
    def resource_efficiency(self) -> float:
        """Delivered pax / (bus_minutes + train_minutes + lastmile_minutes).

        Returns 0 if no resources were used.
        """
        total_resource_time = self.bus_minutes + self.train_minutes + self.lastmile_minutes
        if total_resource_time == 0:
            return 0.0
        return self.success_count / total_resource_time

    def as_dict(self) -> dict:
        """Return all KPIs as a dictionary."""
        return {
            "makespan": self.makespan,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "total_personnel": self.total_personnel,
            "bus_trips": self.bus_trips,
            "train_trips": self.train_trips,
            "bus_minutes": round(self.bus_minutes, 2),
            "train_minutes": round(self.train_minutes, 2),
            "lastmile_minutes": round(self.lastmile_minutes, 2),
            "resource_efficiency": round(self.resource_efficiency, 4),
            "leftover_count": self.leftover_count,
        }
