from app.models.schemas import DependencyMap, FirmwareComponent


class FirmwareDependencyMapper:
    """Builds dependency and blast-radius views for accelerator firmware stacks."""

    def map_dependencies(self, dependency_document: dict) -> DependencyMap:
        components = [
            FirmwareComponent(**component)
            for component in dependency_document.get("components", [])
        ]
        adjacency = {component.name: component.depends_on for component in components}
        blast_radius = {
            component.name: self._collect_impacted_surfaces(component.name, components)
            for component in components
        }

        return DependencyMap(
            platform=dependency_document["platform"],
            generated_from=dependency_document["generated_from"],
            components=components,
            adjacency=adjacency,
            blast_radius=blast_radius,
        )

    def _collect_impacted_surfaces(
        self,
        component_name: str,
        components: list[FirmwareComponent],
    ) -> list[str]:
        direct_impacts = set()
        dependents = set()

        for component in components:
            if component.name == component_name:
                direct_impacts.update(component.impacts)
            if component_name in component.depends_on:
                dependents.add(component.name)
                direct_impacts.update(component.impacts)

        return sorted(direct_impacts | dependents)
