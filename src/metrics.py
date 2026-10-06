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
        - first/median/80th/95th arrival time for successful arrivals
        - road_vehicle_cycles / road_deployed_seat_capacity /
          road_boarded_passengers / road_mean_vehicle_load_factor: road-only
          utilization accounting
        - rail_deployed_seat_capacity / rail_boarded_passengers /
          rail_mean_load_factor: rail-only utilization accounting

    With ``include_extended=True``, ``vehicle_cycles``,
    ``deployed_seat_capacity``, ``boarded_passengers``, and
    ``mean_vehicle_load_factor`` remain transitional aliases for their
    canonical ``road_*`` counterparts.
    """

    total_personnel: int = 0
    time_limit: float = 1440.0
    late_penalty_min: float | None = None
    # Success deadline decoupled from the simulation censor horizon. ``time_limit``
    # is how long the simulation runs (and the censor cutoff); ``success_deadline_min``
    # is the operational deadline by which an arrival counts as a success
    # (completion_rate / censored_count). When None, it falls back to ``time_limit``
    # so legacy behaviour is unchanged. The success_deadline ladder
    # (5/6/7/8/10/12h) is the Phase-5 robustness sweep; the canonical run sets
    # time_limit generously so both alternatives can complete and be compared.
    success_deadline_min: float | None = None

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
    rerouting_events: int = 0
    passenger_travel_minutes: float = 0.0
    # Per-service (non-rail) counters for the composable multi-service pipeline.
    # Rail stays on train_trips/train_minutes (legacy KPI identity); sea/air
    # accumulate here. ``service_breakdown`` rolls them up for as_dict. These
    # are additive-only: legacy keys in as_dict are never renamed or removed.
    service_trips: dict[str, int] = field(default_factory=dict)
    service_minutes: dict[str, float] = field(default_factory=dict)

    # Personnel still waiting at end
    leftover_count: int = 0

    # Opt-in transport accounting. Appended after every legacy dataclass field
    # to preserve positional construction as well as the default dict contract.
    empty_return_trips: int = 0
    empty_return_minutes: float = 0.0
    # These three storage names predate rail load accounting and are road-only.
    # Explicit ``road_*`` properties/keys below are canonical; ambiguous names
    # remain transitional aliases for existing result readers.
    vehicle_cycles: int = 0
    deployed_seat_capacity: int = 0
    boarded_passengers: int = 0
    rail_deployed_seat_capacity: int = 0
    rail_boarded_passengers: int = 0
    assembly_wait_passenger_minutes: float = 0.0
    assembly_wait_passenger_count: int = 0
    transfer_wait_passenger_minutes: float = 0.0
    transfer_wait_passenger_count: int = 0
    rail_wait_passenger_minutes: float = 0.0
    rail_wait_passenger_count: int = 0

    def __post_init__(self) -> None:
        self._validate_extended_state()

    def record_arrival(self, person_id: int, arrival_time: float) -> None:
        self.arrivals.append((person_id, arrival_time))

    def record_empty_return(
        self,
        travel_time_min: float,
        trips: int = 1,
    ) -> None:
        """Record one or more unladen vehicle-return movements."""
        travel_time_min = self._validated_time(travel_time_min, "travel_time_min")
        trips = self._validated_count(trips, "trips")
        self.empty_return_trips += trips
        self.empty_return_minutes += travel_time_min * trips

    def record_road_vehicle_cycle(self, count: int = 1) -> None:
        """Record completed road-vehicle service cycles."""
        self.vehicle_cycles += self._validated_count(count, "count")

    def record_vehicle_cycle(self, count: int = 1) -> None:
        """Compatibility alias for :meth:`record_road_vehicle_cycle`."""
        self.record_road_vehicle_cycle(count)

    def record_road_vehicle_load(
        self,
        boarded_passengers: int,
        seat_capacity: int,
    ) -> None:
        """Accumulate road-boarded passengers and deployed road seats."""
        boarded_passengers = self._validated_count(
            boarded_passengers,
            "boarded_passengers",
        )
        seat_capacity = self._validated_count(seat_capacity, "seat_capacity")
        if boarded_passengers > seat_capacity:
            raise ValueError("boarded_passengers cannot exceed seat_capacity")
        self.boarded_passengers += boarded_passengers
        self.deployed_seat_capacity += seat_capacity

    def record_vehicle_load(
        self,
        boarded_passengers: int,
        seat_capacity: int,
    ) -> None:
        """Compatibility alias for :meth:`record_road_vehicle_load`."""
        self.record_road_vehicle_load(boarded_passengers, seat_capacity)

    def record_rail_load(
        self,
        boarded_passengers: int,
        seat_capacity: int,
    ) -> None:
        """Accumulate rail-boarded passengers and deployed train seats."""

        boarded_passengers = self._validated_count(
            boarded_passengers,
            "boarded_passengers",
        )
        seat_capacity = self._validated_count(seat_capacity, "seat_capacity")
        if boarded_passengers > seat_capacity:
            raise ValueError("boarded_passengers cannot exceed seat_capacity")
        self.rail_boarded_passengers += boarded_passengers
        self.rail_deployed_seat_capacity += seat_capacity

    def record_passenger_wait(
        self,
        stage: str,
        wait_time_min: float,
        passenger_count: int = 1,
        *,
        count_passengers: bool = True,
    ) -> None:
        """Record passenger-weighted wait at assembly, transfer, or rail stage."""
        if stage not in {"assembly", "transfer", "rail"}:
            raise ValueError(
                "stage must be one of: assembly, transfer, rail"
            )
        wait_time_min = self._validated_time(wait_time_min, "wait_time_min")
        passenger_count = self._validated_count(passenger_count, "passenger_count")
        passenger_minutes = wait_time_min * passenger_count
        minutes_field = f"{stage}_wait_passenger_minutes"
        count_field = f"{stage}_wait_passenger_count"
        setattr(self, minutes_field, getattr(self, minutes_field) + passenger_minutes)
        if count_passengers:
            setattr(self, count_field, getattr(self, count_field) + passenger_count)

    @property
    def makespan(self) -> float:
        """Time when last person arrives at D."""
        if not self.arrivals:
            return float("inf")
        return max(t for _, t in self.arrivals)

    @property
    def success_deadline(self) -> float:
        """Effective success-deadline cutoff (falls back to time_limit)."""
        return (
            self.time_limit
            if self.success_deadline_min is None
            else self.success_deadline_min
        )

    @property
    def success_count(self) -> int:
        """Personnel who arrived at D within the success deadline."""
        return sum(1 for _, t in self.arrivals if t <= self.success_deadline)

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
    def first_arrival_time(self) -> float:
        """Earliest successful destination arrival time."""
        successful = self._successful_arrival_times()
        if not successful:
            return float("inf")
        return successful[0]

    @property
    def median_arrival_time(self) -> float:
        """Median successful destination arrival time."""
        return self._arrival_quantile(0.50)

    @property
    def p80_arrival_time(self) -> float:
        """80th percentile successful destination arrival time."""
        return self._arrival_quantile(0.80)

    @property
    def p95_arrival_time(self) -> float:
        """95th percentile successful destination arrival time."""
        return self._arrival_quantile(0.95)

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
    def road_vehicle_operating_minutes(self) -> float:
        """Loaded road service plus finite empty-return vehicle minutes."""

        return self.road_vehicle_service_minutes + self.empty_return_minutes

    @property
    def total_operating_minutes(self) -> float:
        """All finite vehicle/train operating minutes including empty returns."""

        return self.road_vehicle_operating_minutes + self.train_service_minutes

    @property
    def passengers_per_operating_vehicle_minute(self) -> float:
        """Delivered passengers per road vehicle-minute including returns."""

        return self._delivered_per_service_minute(
            self.road_vehicle_operating_minutes
        )

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
    def mean_vehicle_load_factor(self) -> float:
        """Compatibility alias for road_mean_vehicle_load_factor."""
        return self.road_mean_vehicle_load_factor

    @property
    def road_vehicle_cycles(self) -> int:
        """Completed road-vehicle cycles."""
        return self.vehicle_cycles

    @property
    def road_deployed_seat_capacity(self) -> int:
        """Seats offered across dispatched road vehicles."""
        return self.deployed_seat_capacity

    @property
    def road_boarded_passengers(self) -> int:
        """Passenger boardings across dispatched road vehicles."""
        return self.boarded_passengers

    @property
    def road_mean_vehicle_load_factor(self) -> float:
        """Road boardings divided by deployed road-seat capacity."""
        if self.deployed_seat_capacity <= 0:
            return 0.0
        return self.boarded_passengers / self.deployed_seat_capacity

    @property
    def rail_mean_load_factor(self) -> float:
        """Rail boardings divided by deployed train-seat capacity."""
        if self.rail_deployed_seat_capacity <= 0:
            return 0.0
        return self.rail_boarded_passengers / self.rail_deployed_seat_capacity

    @property
    def mean_assembly_wait_min(self) -> float:
        """Passenger-weighted mean assembly wait in minutes."""
        return self._passenger_weighted_mean(
            self.assembly_wait_passenger_minutes,
            self.assembly_wait_passenger_count,
        )

    @property
    def mean_transfer_wait_min(self) -> float:
        """Passenger-weighted mean transfer wait in minutes."""
        return self._passenger_weighted_mean(
            self.transfer_wait_passenger_minutes,
            self.transfer_wait_passenger_count,
        )

    @property
    def mean_rail_wait_min(self) -> float:
        """Passenger-weighted mean rail wait in minutes."""
        return self._passenger_weighted_mean(
            self.rail_wait_passenger_minutes,
            self.rail_wait_passenger_count,
        )

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

    def _successful_arrival_times(self) -> list[float]:
        """Return sorted arrival times within the configured time limit."""
        return sorted(t for _, t in self.arrivals if t <= self.time_limit)

    def _arrival_quantile(self, q: float) -> float:
        """Return a linearly interpolated successful-arrival quantile."""
        values = self._successful_arrival_times()
        if not values:
            return float("inf")
        if len(values) == 1:
            return values[0]

        q = max(0.0, min(1.0, float(q)))
        position = q * (len(values) - 1)
        lower_index = int(math.floor(position))
        upper_index = int(math.ceil(position))
        if lower_index == upper_index:
            return values[lower_index]
        fraction = position - lower_index
        return values[lower_index] + fraction * (
            values[upper_index] - values[lower_index]
        )

    def _delivered_per_service_minute(self, service_minutes: float) -> float:
        """Return delivered-passenger rate for a service-minute denominator."""
        if not math.isfinite(service_minutes) or service_minutes <= 0:
            return 0.0
        return self.success_count / service_minutes

    @staticmethod
    def _passenger_weighted_mean(
        passenger_minutes: float,
        passenger_count: int,
    ) -> float:
        """Return a finite zero when no passengers contribute to a wait metric."""
        if passenger_count <= 0:
            return 0.0
        return passenger_minutes / passenger_count

    @staticmethod
    def _validated_count(value: int, name: str) -> int:
        """Return a nonnegative integral count or raise ValueError."""
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
        return value

    @staticmethod
    def _validated_time(value: float, name: str) -> float:
        """Return a finite nonnegative duration or raise ValueError."""
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a finite nonnegative number") from exc
        if not math.isfinite(numeric) or numeric < 0:
            raise ValueError(f"{name} must be a finite nonnegative number")
        return numeric

    def _validate_extended_state(self) -> None:
        """Validate all opt-in counters and durations."""
        for name in (
            "empty_return_trips",
            "vehicle_cycles",
            "deployed_seat_capacity",
            "boarded_passengers",
            "rail_deployed_seat_capacity",
            "rail_boarded_passengers",
            "assembly_wait_passenger_count",
            "transfer_wait_passenger_count",
            "rail_wait_passenger_count",
        ):
            self._validated_count(getattr(self, name), name)
        for name in (
            "empty_return_minutes",
            "assembly_wait_passenger_minutes",
            "transfer_wait_passenger_minutes",
            "rail_wait_passenger_minutes",
        ):
            self._validated_time(getattr(self, name), name)
        if self.boarded_passengers > self.deployed_seat_capacity:
            raise ValueError(
                "boarded_passengers cannot exceed deployed_seat_capacity"
            )
        if self.rail_boarded_passengers > self.rail_deployed_seat_capacity:
            raise ValueError(
                "rail_boarded_passengers cannot exceed "
                "rail_deployed_seat_capacity"
            )

    def as_dict(self, include_extended: bool = False) -> dict:
        """Return KPIs, optionally including extended transport accounting."""
        result = {
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
            "rerouting_events": self.rerouting_events,
            "leftover_count": self.leftover_count,
            "censored_count": self.censored_count,
            "completion_rate": self.completion_rate,
            "penalized_makespan": self.penalized_makespan,
            "first_arrival_time": self.first_arrival_time,
            "median_arrival_time": self.median_arrival_time,
            "p80_arrival_time": self.p80_arrival_time,
            "p95_arrival_time": self.p95_arrival_time,
            "service_breakdown": {
                mode: {
                    "trips": self.service_trips.get(mode, 0),
                    "minutes": round(self.service_minutes.get(mode, 0.0), 2),
                }
                for mode in sorted(set(self.service_trips) | set(self.service_minutes))
            },
        }
        if not include_extended:
            return result

        self._validate_extended_state()
        result.update(
            {
                "empty_return_trips": self.empty_return_trips,
                "empty_return_minutes": round(self.empty_return_minutes, 2),
                "road_vehicle_operating_minutes": round(
                    self.road_vehicle_operating_minutes,
                    2,
                ),
                "total_operating_minutes": round(
                    self.total_operating_minutes,
                    2,
                ),
                "passengers_per_operating_vehicle_minute": round(
                    self.passengers_per_operating_vehicle_minute,
                    4,
                ),
                "road_vehicle_cycles": self.road_vehicle_cycles,
                "road_deployed_seat_capacity": self.road_deployed_seat_capacity,
                "road_boarded_passengers": self.road_boarded_passengers,
                "road_mean_vehicle_load_factor": round(
                    self.road_mean_vehicle_load_factor,
                    4,
                ),
                "rail_deployed_seat_capacity": self.rail_deployed_seat_capacity,
                "rail_boarded_passengers": self.rail_boarded_passengers,
                "rail_mean_load_factor": round(self.rail_mean_load_factor, 4),
                # Transitional road-only aliases retained for existing readers.
                "vehicle_cycles": self.vehicle_cycles,
                "deployed_seat_capacity": self.deployed_seat_capacity,
                "boarded_passengers": self.boarded_passengers,
                "mean_vehicle_load_factor": round(
                    self.mean_vehicle_load_factor,
                    4,
                ),
                "assembly_wait_passenger_minutes": round(
                    self.assembly_wait_passenger_minutes,
                    2,
                ),
                "assembly_wait_passenger_count": self.assembly_wait_passenger_count,
                "mean_assembly_wait_min": round(self.mean_assembly_wait_min, 2),
                "transfer_wait_passenger_minutes": round(
                    self.transfer_wait_passenger_minutes,
                    2,
                ),
                "transfer_wait_passenger_count": self.transfer_wait_passenger_count,
                "mean_transfer_wait_min": round(self.mean_transfer_wait_min, 2),
                "rail_wait_passenger_minutes": round(
                    self.rail_wait_passenger_minutes,
                    2,
                ),
                "rail_wait_passenger_count": self.rail_wait_passenger_count,
                "mean_rail_wait_min": round(self.mean_rail_wait_min, 2),
            }
        )
        return result
