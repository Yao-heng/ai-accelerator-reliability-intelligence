from app.models.schemas import CorrelatedEvent, ValidationGap, ValidationScenario


class ValidationGapAnalyzer:
    """Finds where observed incidents are not covered by validation scenarios."""

    def analyze(
        self,
        correlated_events: list[CorrelatedEvent],
        validation_rows: list[dict],
    ) -> list[ValidationGap]:
        scenarios = [ValidationScenario(**row) for row in validation_rows]
        gaps: list[ValidationGap] = []

        for event in correlated_events:
            matching = [
                scenario
                for scenario in scenarios
                if scenario.failure_mode == event.likely_failure_mode
            ]

            if not matching:
                gaps.append(self._build_gap(event, "No validation scenario covers this failure mode."))
                continue

            covered = any(self._scenario_covers_event(scenario, event) for scenario in matching)
            if not covered:
                gaps.append(
                    self._build_gap(
                        event,
                        "Existing validation does not cover this firmware and workload condition.",
                    )
                )

        return gaps

    def _scenario_covers_event(
        self,
        scenario: ValidationScenario,
        event: CorrelatedEvent,
    ) -> bool:
        firmware_match = (
            event.firmware_version in scenario.firmware_versions
            or "*" in scenario.firmware_versions
        )
        phase_match = (
            event.workload_phase in scenario.workload_phases
            or "*" in scenario.workload_phases
        )
        return firmware_match and phase_match and scenario.coverage_level != "none"

    def _build_gap(self, event: CorrelatedEvent, reason: str) -> ValidationGap:
        missing_conditions = [
            f"firmware={event.firmware_version or 'unknown'}",
            f"workload_phase={event.workload_phase or 'unknown'}",
            f"failure_mode={event.likely_failure_mode}",
        ]

        return ValidationGap(
            gap_id=f"GAP-{event.incident_id.removeprefix('INC-')}",
            incident_id=event.incident_id,
            failure_mode=event.likely_failure_mode,
            reason=reason,
            missing_conditions=missing_conditions,
            suggested_validation=(
                "Add accelerated stress coverage that replays the observed telemetry "
                "envelope with firmware instrumentation enabled."
            ),
            priority="high" if event.severity.value in {"ERROR", "CRITICAL"} else "medium",
        )
