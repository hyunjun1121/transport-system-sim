"""Metrics collector for simulation KPIs."""

import math
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
        - bus_minutes: legacy bus/shuttle road vehicle service time (min)
        - train_minutes: legacy train service time (min)
        - lastmile_minutes: legacy last-mile minutes; historical runs may use
          either vehicle-minutes or passenger-minutes here, so this field is
          excluded from service-minute denominators
        - lastmile_vehicle_minutes: last-mile road vehicle service time (min)
        - road_vehicle_service_minutes: bus + last-mile vehicle service time
        - train_service_minutes: train service time
        - total_service_minutes: road vehicle + train service time
        - passenger_travel_minutes: optional passenger-minute travel exposure
        - passengers_per_vehicle_minute: delivered pax per road vehicle-minute
        - passengers_per_total_service_minute: delivered pax per service-minute
        - leftover_count: personnel not transported (stranded)
        - censored_count: personnel not delivered within the simulation horizon
        - completion_rate: fraction delivered within the simulation horizon
        - penalized_makespan: makespan with a penalty for censored personnel
    """

    total_personnel: int = 0
    time_limit: float = 1440.0
    late_penalty_min: float | None = None

    # Arrival records: (person_id, arrival_time_at_D)
    arrivals: list[tuple[int, float]] = field(default_factory=list)

    # Resource usage. ``bus_minutes`` and ``train_minutes`` are retained as
    # legacy field names because scenario code mutates them directly.
    bus_trips: int = 0
    train_trips: int = 0
    bus_minutes: float = 0.0
    train_minutes: float = 0.0

    # Backward-compatible legacy field. Historical scenario versions used this
    # for different last-mile minute units, so unit-consistent service KPIs
    # deliberately do not include this value.
    lastmile_minutes: float = 0.0

    # Unit-explicit fields for new resource accounting.
    lastmile_vehicle_minutes: float = 0.0
    passenger_travel_minutes: float = 0.0

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
    def censored_count(self) -> int:
        """Personnel not delivered within the simulation time limit."""
        if self.total_personnel <= 0:
            return max(0, int(self.leftover_count))
        not_successful = self.total_personnel - self.success_count
        return max(0, int(not_successful), int(self.leftover_count))

    @property
    def completion_rate(self) -> float:
        """Fraction of personnel delivered within the simulation time limit."""
        if self.total_personnel <= 0:
            return 0.0
        completed = self.total_personnel - self.censored_count
        return max(0.0, min(1.0, completed / self.total_personnel))

    @property
    def penalized_makespan(self) -> float:
        """Makespan with an added penalty for censored personnel.

        The legacy ``makespan`` remains the last observed delivery time. When
        delivery is incomplete, this KPI anchors the run at at least the time
        limit and adds one late penalty per censored person.
        """
        censored = self.censored_count
        if censored == 0:
            return self.makespan

        base = self.makespan
        if not math.isfinite(base):
            base = self.time_limit
        elif math.isfinite(self.time_limit):
            base = max(base, self.time_limit)

        penalty = self._late_penalty_min()
        return base + censored * penalty

    @property
    def road_vehicle_service_minutes(self) -> float:
        """Total road vehicle service minutes.

        Includes bus/shuttle service time plus explicit last-mile vehicle time.
        It excludes ``lastmile_minutes`` because that legacy field may contain
        either vehicle-minutes or passenger-minutes depending on the producer.
        """
        return self.bus_minutes + self.lastmile_vehicle_minutes

    @property
    def train_service_minutes(self) -> float:
        """Total train service minutes."""
        return self.train_minutes

    @property
    def total_service_minutes(self) -> float:
        """Total unit-consistent vehicle/train service minutes."""
        return self.road_vehicle_service_minutes + self.train_service_minutes

    @property
    def passengers_per_vehicle_minute(self) -> float:
        """Delivered passengers per road vehicle service minute."""
        return self._delivered_per_service_minute(self.road_vehicle_service_minutes)

    @property
    def passengers_per_total_service_minute(self) -> float:
        """Delivered passengers per total vehicle/train service minute."""
        return self._delivered_per_service_minute(self.total_service_minutes)

    @property
    def resource_efficiency(self) -> float:
        """Backward-compatible alias for passengers_per_total_service_minute.

        The legacy implementation mixed vehicle/train service minutes with
        last-mile passenger-minutes. The alias now uses only unit-consistent
        service minutes.
        """
        return self.passengers_per_total_service_minute

    def _late_penalty_min(self) -> float:
        """Penalty minutes assigned to each censored person."""
        penalty = self.time_limit if self.late_penalty_min is None else self.late_penalty_min
        if not math.isfinite(penalty):
            return float(penalty)
        return max(0.0, float(penalty))

    def _delivered_per_service_minute(self, service_minutes: float) -> float:
        """Return delivered-passenger rate for a service-minute denominator."""
        if not math.isfinite(service_minutes) or service_minutes <= 0:
            return 0.0
        return self.success_count / service_minutes

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
            "lastmile_vehicle_minutes": round(self.lastmile_vehicle_minutes, 2),
            "road_vehicle_service_minutes": round(self.road_vehicle_service_minutes, 2),
            "train_service_minutes": round(self.train_service_minutes, 2),
            "total_service_minutes": round(self.total_service_minutes, 2),
            "passenger_travel_minutes": round(self.passenger_travel_minutes, 2),
            "passengers_per_vehicle_minute": round(self.passengers_per_vehicle_minute, 4),
            "passengers_per_total_service_minute": round(
                self.passengers_per_total_service_minute,
                4,
            ),
            "resource_efficiency": round(self.resource_efficiency, 4),
            "leftover_count": self.leftover_count,
            "censored_count": self.censored_count,
            "completion_rate": self.completion_rate,
            "penalized_makespan": self.penalized_makespan,
        }
