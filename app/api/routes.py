from fastapi import APIRouter

from app.models.schemas import (
    AcceleratorLogEntry,
    CorrelatedEvent,
    DependencyMap,
    ReliabilityRecommendation,
    ValidationGap,
)
from app.services.data_repository import DataRepository
from app.services.firmware_dependency_mapper import FirmwareDependencyMapper
from app.services.log_parser import LogParser
from app.services.recommendation_engine import RecommendationEngine
from app.services.telemetry_correlator import TelemetryCorrelator
from app.services.validation_gap_analyzer import ValidationGapAnalyzer

router = APIRouter(tags=["reliability"])

repository = DataRepository()
log_parser = LogParser()
correlator = TelemetryCorrelator()
gap_analyzer = ValidationGapAnalyzer()
dependency_mapper = FirmwareDependencyMapper()
recommendation_engine = RecommendationEngine()


@router.get("/logs/parsed", response_model=list[AcceleratorLogEntry])
def get_parsed_logs() -> list[AcceleratorLogEntry]:
    """Parse fictional accelerator firmware and platform logs."""
    return log_parser.parse(repository.load_raw_logs())


@router.get("/telemetry/correlated", response_model=list[CorrelatedEvent])
def get_correlated_telemetry() -> list[CorrelatedEvent]:
    """Correlate parsed logs with sampled accelerator telemetry windows."""
    parsed_logs = log_parser.parse(repository.load_raw_logs())
    telemetry = repository.load_telemetry()
    return correlator.correlate(parsed_logs, telemetry)


@router.get("/validation/gaps", response_model=list[ValidationGap])
def get_validation_gaps() -> list[ValidationGap]:
    """Detect uncovered or stale validation scenarios for observed failures."""
    parsed_logs = log_parser.parse(repository.load_raw_logs())
    telemetry = repository.load_telemetry()
    correlated_events = correlator.correlate(parsed_logs, telemetry)
    validation_matrix = repository.load_validation_matrix()
    return gap_analyzer.analyze(correlated_events, validation_matrix)


@router.get("/firmware/dependencies", response_model=DependencyMap)
def get_firmware_dependencies() -> DependencyMap:
    """Map firmware modules to dependent runtime, driver, and hardware surfaces."""
    return dependency_mapper.map_dependencies(repository.load_firmware_dependencies())


@router.get("/recommendations", response_model=list[ReliabilityRecommendation])
def get_recommendations() -> list[ReliabilityRecommendation]:
    """Generate reliability recommendations from correlated evidence."""
    parsed_logs = log_parser.parse(repository.load_raw_logs())
    telemetry = repository.load_telemetry()
    correlated_events = correlator.correlate(parsed_logs, telemetry)
    validation_gaps = gap_analyzer.analyze(
        correlated_events,
        repository.load_validation_matrix(),
    )
    dependency_map = dependency_mapper.map_dependencies(
        repository.load_firmware_dependencies(),
    )
    return recommendation_engine.recommend(
        correlated_events,
        validation_gaps,
        dependency_map,
    )
