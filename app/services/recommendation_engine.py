from app.models.schemas import (
    CorrelatedEvent,
    DependencyMap,
    ReliabilityRecommendation,
    ValidationGap,
)


class RecommendationEngine:
    """Ranks reliability actions from correlated incidents and validation gaps."""

    def recommend(
        self,
        correlated_events: list[CorrelatedEvent],
        validation_gaps: list[ValidationGap],
        dependency_map: DependencyMap,
    ) -> list[ReliabilityRecommendation]:
        recommendations: list[ReliabilityRecommendation] = []

        for event in correlated_events:
            impacted_components = self._components_for_event(event, dependency_map)
            matching_gaps = [
                gap for gap in validation_gaps if gap.incident_id == event.incident_id
            ]

            recommendations.append(
                ReliabilityRecommendation(
                    recommendation_id=f"REC-{event.incident_id.removeprefix('INC-')}",
                    priority=self._priority(event, matching_gaps),
                    title=self._title(event),
                    rationale=self._rationale(event, matching_gaps),
                    evidence=[
                        event.summary,
                        *[
                            f"{metric.name}={metric.value} threshold={metric.threshold}"
                            for metric in event.correlated_metrics
                        ],
                    ],
                    affected_components=impacted_components,
                    expected_impact=self._expected_impact(event),
                    next_steps=self._next_steps(event, matching_gaps),
                )
            )

        return sorted(recommendations, key=lambda item: {"critical": 0, "high": 1, "medium": 2}[item.priority])

    def _components_for_event(
        self,
        event: CorrelatedEvent,
        dependency_map: DependencyMap,
    ) -> list[str]:
        keyword_map = {
            "hbm": "hbm-training",
            "pcie": "pcie-link-manager",
            "thermal": "thermal-governor",
            "fabric": "fabric-transport",
            "power": "power-policy",
        }
        component_hint = next(
            (
                component
                for keyword, component in keyword_map.items()
                if keyword in event.likely_failure_mode
            ),
            "platform-supervisor",
        )
        blast_radius = dependency_map.blast_radius.get(component_hint, [])
        return [component_hint, *blast_radius]

    def _priority(
        self,
        event: CorrelatedEvent,
        gaps: list[ValidationGap],
    ) -> str:
        if event.severity.value == "CRITICAL":
            return "critical"
        if gaps or event.confidence >= 0.85:
            return "high"
        return "medium"

    def _title(self, event: CorrelatedEvent) -> str:
        return f"Stabilize {event.likely_failure_mode.replace('_', ' ')} path"

    def _rationale(self, event: CorrelatedEvent, gaps: list[ValidationGap]) -> str:
        gap_clause = " A validation gap was detected." if gaps else ""
        return (
            f"{event.accelerator_id} showed {event.likely_failure_mode} during "
            f"{event.workload_phase or 'unknown'} workload execution with "
            f"{len(event.correlated_metrics)} anomalous telemetry signal(s)."
            f"{gap_clause}"
        )

    def _expected_impact(self, event: CorrelatedEvent) -> str:
        if event.likely_failure_mode == "hbm_ecc_escalation":
            return "Reduce uncorrectable memory events and avoid accelerator resets."
        if event.likely_failure_mode == "pcie_link_instability":
            return "Lower host-device retry pressure and prevent throughput collapse."
        if event.likely_failure_mode == "thermal_throttle_boundary":
            return "Improve sustained inference latency under high power density."
        return "Improve fleet-level fault isolation and incident triage speed."

    def _next_steps(
        self,
        event: CorrelatedEvent,
        gaps: list[ValidationGap],
    ) -> list[str]:
        steps = [
            "Replay the incident telemetry envelope in a controlled validation rack.",
            "Enable firmware tracepoints for the implicated subsystem.",
        ]
        if gaps:
            steps.append("Add the missing validation condition to the release gate.")
        if event.confidence >= 0.85:
            steps.append("Open a firmware owner review with correlated evidence attached.")
        return steps
