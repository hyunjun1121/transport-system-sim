"""KCI slim re-export of the realworld surface used by the corridor study."""

from __future__ import annotations

from .adapter import (
    REQUIRED_EDGE_FIELDS,
    REQUIRED_ROUTES,
    build_simulator_graph,
    osm_graph_to_simulator_graph,
    realworld_network_config,
    to_simulator_graph,
)
from .attributes import (
    DEFAULT_ROUTEABLE_HIGHWAY_CLASSES,
    RoadClassDefaults,
    is_routeable_vehicle_highway,
    map_edge_attributes,
)
from .osm_network import load_graphml
from .regions import load_region_spec
from .types import RegionSpec
from .validation import assert_graph_ready
from .zones import add_connector_edges, snap_region_points

__all__ = [
    "DEFAULT_ROUTEABLE_HIGHWAY_CLASSES",
    "REQUIRED_EDGE_FIELDS",
    "REQUIRED_ROUTES",
    "RegionSpec",
    "RoadClassDefaults",
    "add_connector_edges",
    "assert_graph_ready",
    "build_simulator_graph",
    "is_routeable_vehicle_highway",
    "load_graphml",
    "load_region_spec",
    "map_edge_attributes",
    "osm_graph_to_simulator_graph",
    "realworld_network_config",
    "snap_region_points",
    "to_simulator_graph",
]
