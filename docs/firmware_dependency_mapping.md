# Firmware Dependency Mapping

## Purpose

Firmware dependency mapping identifies relationships between silicon
behavior, firmware components, BIOS/BMC/EC logic, power sequencing,
validation requirements, and production reliability.

Many platform failures occur because a patch or workaround is applied
without understanding its dependency chain. This stage turns a firmware
integration manifest into two machine-readable views an engineer can
act on: who depends on whom, and what breaks if a component is at fault
(its blast radius).

## Dependency types (conceptual background)

- Silicon stepping → firmware workaround
- Firmware patch → BIOS/BMC/EC interaction
- Power rail timing → platform boot sequence
- GPIO assertion → device initialization
- Reset flow → driver / OS behavior
- Errata → validation test requirement
- Telemetry event → RCA workflow

Only the component-level form of these relationships is implemented;
see below.

## As implemented

Implementation: `FirmwareDependencyMapper` in
`app/services/firmware_dependency_mapper.py`, exposed as
`GET /api/v1/firmware/dependencies`.

Input: `app/data/firmware_dependencies.json`, a manifest for the
fictional "AIX-9000" platform with 6 components (`platform-supervisor`,
`hbm-training`, `pcie-link-manager`, `fabric-transport`,
`thermal-governor`, `power-policy`). Each component declares `name`,
`version`, `owner`, `depends_on`, `impacts`, and `risk_notes`.

Transformation (`FirmwareDependencyMapper.map_dependencies`):

1. `adjacency` maps each component name to its declared `depends_on`
   list.
2. `blast_radius` for a component is the sorted union of:
   - its own declared `impacts`,
   - the `impacts` of every component that lists it in `depends_on`
     (its dependents), and
   - the names of those dependents.
3. Component records (including `risk_notes`) are passed through
   unchanged.

Example, from the bundled manifest: `power-policy` is a dependency of
`platform-supervisor`, `hbm-training`, `fabric-transport`, and
`thermal-governor`, so its blast radius spans those components'
impacts — voltage rails, boost states, and brownout protection, plus
memory scrubbing, collective operations, frequency scaling, fleet
health reporting, and more. See
`examples/sample_outputs/firmware_dependency_map.json` for the full
real output.

## Output

A `DependencyMap`:

- `platform` and `generated_from` (copied from the manifest)
- `components` — the manifest's component records
- `adjacency` — component name → list of components it depends on
- `blast_radius` — component name → sorted list of impacted surfaces
  and dependent component names

## Not implemented

The following are design context, not shipped behavior:

- A dependency graph derived from silicon errata → workaround → BIOS
  patch → validation test → telemetry rule chains; the mapper only
  reads the declared component manifest.
- Missing-patch dependency warnings, telemetry rule suggestions, or a
  production risk assessment — `risk_notes` are carried through as
  text, never evaluated.
- Validation impact analysis beyond what the recommendation engine
  does with the blast radius (it attaches the blast radius of a
  failure-mode's component hint to each recommendation's
  `affected_components`).
