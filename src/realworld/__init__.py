"""Real-world and quasi-real regional transport pipeline helpers.

Round-2 cleanup removed the acceptance / review-packet / decision-packet
research-integrity scaffolding. This package now exposes only the modules on the
canonical Goseong 1000-pax experiment run path plus their transitive deps.
Access submodules directly (``from src.realworld.pilot_experiments import ...``);
the names re-exported below are kept for the few package-level import sites.
"""

# Import every kept submodule so attribute/submodule access keeps working
# (e.g. ``from src.realworld import osm_network``).
from . import (
    adapter,
    artifact_invalidation_matrix,
    attributes,
    claim_language_guard,
    disruption_scenarios,
    manifest_timestamp,
    nodelink_network,
    osm_network,
    parameters,
    phase_gate_ledger,
    pilot_experiments,
    plausibility,
    policy_alternatives,
    regions,
    road_overrides,
    source_artifacts,
    types,
    validation,
    vds_calibration,
    zones,
)

from .adapter import build_simulator_graph, realworld_network_config
from .attributes import map_edge_attributes, map_osm_edge_attributes
from .disruption_scenarios import (
    DisruptionScenario,
    ScenarioEdge,
    build_scenario_disruption_map,
    build_scenario_edge_map,
    load_disruption_scenarios,
    mark_scenario_edges,
)
from .osm_network import (
    extract_bbox_graph,
    load_graphml,
    load_or_extract_bbox_graph,
    normalize_osm_graph,
    save_graphml,
)
from .parameters import (
    ParameterRecord,
    load_shipped_parameter_tables,
    validate_shipped_parameter_tables,
)
from .phase_gate_ledger import (
    ALLOWED_PHASE_GATE_DECISIONS,
    ALLOWED_PHASE_GATE_STATUSES,
    CANONICAL_PHASE_GATE_SPECS,
    DEFAULT_PHASE_GATE_DECISION_AUTHORITY,
    DEFAULT_PHASE_GATE_LEDGER_AUDIT_DOC,
    DEFAULT_PHASE_GATE_LEDGER_AUDIT_MANIFEST,
    DEFAULT_PHASE_GATE_LEDGER_DIR,
    DEFAULT_PHASE_GATE_LEDGER_SCHEMA,
    PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
    PhaseGateSpec,
    audit_phase_gate_ledgers,
    build_phase_gate_ledger_audit_markdown,
    build_phase_gate_template,
    load_phase_gate_ledger,
    phase_gate_ledger_schema,
    summarize_phase_gate_ledger_audit,
    validate_phase_gate_ledger_mapping,
    write_phase_gate_ledgers,
)
from .pilot_experiments import (
    DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
    DEFAULT_ROUTE_CORRIDOR_PAIRS,
    GRAPH_REDUCTION_MULTI_CORRIDOR,
    GRAPH_REDUCTION_SINGLE_CORRIDOR,
    GRAPH_REDUCTION_STRATEGIES,
    PilotDisruptionCase,
    PilotInputs,
    pilot_experiment_multi_corridor_subgraph,
    pilot_experiment_subgraph,
    reduce_pilot_analysis_graph,
    run_pilot_experiments,
    summarize_pilot_rows,
)
from .plausibility import (
    PlausibilityRecord,
    RouteCheck,
    evaluate_graph_plausibility,
    status_counts,
)
from .policy_alternatives import (
    PolicyAlternative,
    PolicyConfigVariant,
    build_policy_config_variant,
    config_for_policy_alternative,
    load_policy_alternatives,
)
from .regions import (
    REGION_REGISTRY,
    get_region_spec,
    load_region_registry,
    load_region_spec,
)
from .road_overrides import (
    RoadClassOverride,
    build_highway_defaults_with_overrides,
    build_road_class_override_metadata,
    load_road_class_overrides,
    validate_road_class_overrides,
)
from .source_artifacts import (
    file_sha256 as source_artifact_file_sha256,
    resolve_artifact_path as resolve_source_artifact_path,
    validate_loaded_source_matches_metadata,
    validate_sha256 as validate_source_artifact_sha256,
    validate_source_artifact_metadata,
)
from .types import (
    ALLOWED_BOUNDARY_TYPES,
    ALLOWED_FUEL_TYPES,
    ALLOWED_SENSITIVITY_LEVELS,
    ALLOWED_SERVICE_MODES,
    BoundarySpec,
    Metadata,
    MetadataValue,
    PortPointSpec,
    PUBLIC_COORDINATE_LEVELS,
    RailPointSpec,
    RailSpec,
    RegionServiceSpec,
    RegionSpec,
    SourceRefSpec,
    ZoneSpec,
    assert_public_coordinate_policy,
    validate_metadata,
)
from .validation import assert_graph_ready, validate_graph_readiness
from .zones import nearest_road_node, snap_region_points

__all__ = [
    "BoundarySpec",
    "DisruptionScenario",
    "Metadata",
    "MetadataValue",
    "ParameterRecord",
    "PhaseGateSpec",
    "PilotDisruptionCase",
    "PilotInputs",
    "PlausibilityRecord",
    "PolicyAlternative",
    "PolicyConfigVariant",
    "PortPointSpec",
    "RailPointSpec",
    "RailSpec",
    "RegionServiceSpec",
    "RegionSpec",
    "RouteCheck",
    "RoadClassOverride",
    "ScenarioEdge",
    "SourceRefSpec",
    "ZoneSpec",
    "assert_graph_ready",
    "assert_public_coordinate_policy",
    "build_policy_config_variant",
    "build_scenario_disruption_map",
    "build_scenario_edge_map",
    "build_simulator_graph",
    "config_for_policy_alternative",
    "evaluate_graph_plausibility",
    "extract_bbox_graph",
    "get_region_spec",
    "load_disruption_scenarios",
    "load_graphml",
    "load_or_extract_bbox_graph",
    "load_policy_alternatives",
    "load_region_registry",
    "load_region_spec",
    "load_shipped_parameter_tables",
    "map_edge_attributes",
    "map_osm_edge_attributes",
    "mark_scenario_edges",
    "nearest_road_node",
    "normalize_osm_graph",
    "realworld_network_config",
    "reduce_pilot_analysis_graph",
    "run_pilot_experiments",
    "save_graphml",
    "snap_region_points",
    "status_counts",
    "summarize_pilot_rows",
    "validate_graph_readiness",
    "validate_metadata",
    "validate_shipped_parameter_tables",
]
