#!/usr/bin/env bash
# Strictly gated JLCPCB Rev B manufacturing export; refuses unapproved boards.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_dir="${repo_root}/hardware/Rev_B"
base="FT2D_PD20V_12V5_3A_评审原理图"
manufacturing_dir="${repo_root}/manufacturing/Rev_B"
preflight_dir="${manufacturing_dir}/PREFLIGHT"
approved_bom="${manufacturing_dir}/BOM_APPROVED.csv"
approved_cpl="${manufacturing_dir}/CPL_APPROVED.csv"
signoff="${manufacturing_dir}/RELEASE_APPROVAL.txt"

mkdir -p "${preflight_dir}"
echo 'Running KiCad 10/ERC/DRC + parity release gates...'
kicad-cli sch erc --format json -o "${preflight_dir}/erc.json" "${project_dir}/${base}.kicad_sch"
kicad-cli pcb drc --schematic-parity --refill-zones --format json -o "${preflight_dir}/drc.json" "${project_dir}/${base}.kicad_pcb"

python3 - "${preflight_dir}/erc.json" "${preflight_dir}/drc.json" <<'PY'
import json, sys
with open(sys.argv[1],encoding='utf8') as f: erc=json.load(f)
with open(sys.argv[2],encoding='utf8') as f: drc=json.load(f)
counts={
    'ERC':len(erc.get('violations',[])),
    'PCB DRC violations':len(drc.get('violations',[])),
    'PCB unconnected':len(drc.get('unconnected_items',[])),
    'Schematic parity':len(drc.get('schematic_parity',[])),
}
for name,count in counts.items(): print(f'  {name}: {count}')
if any(counts.values()):
    sys.exit('NO-GO: manufacturing export refused until all check counts are zero')
PY

if [[ ! -f "${approved_bom}" || ! -f "${approved_cpl}" ]]; then
    echo 'NO-GO: JLC-part-number-complete BOM_APPROVED.csv and visually checked CPL_APPROVED.csv required.' >&2
    exit 3
fi
if [[ ! -f "${signoff}" ]]; then
    echo 'NO-GO: engineering signoff missing (3A copper, return paths, footprint land patterns, and assembly).' >&2
    exit 3
fi
for phrase in 'POWER_AND_THERMAL_APPROVED' 'FOOTPRINTS_AND_SMT_APPROVED' 'NVM_TEST_PLAN_APPROVED'; do
    if ! grep -Fxq "${phrase}" "${signoff}"; then
        echo "NO-GO: engineering signoff missing ${phrase}" >&2
        exit 3
    fi
done

release_dir="${manufacturing_dir}/RELEASE_READY"
mkdir -p "${release_dir}/gerbers" "${release_dir}/drill"
kicad-cli pcb export gerbers \
    --layers 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts' \
    --subtract-soldermask \
    -o "${release_dir}/gerbers" \
    "${project_dir}/${base}.kicad_pcb"
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th \
    -o "${release_dir}/drill" "${project_dir}/${base}.kicad_pcb"
cp "${approved_bom}" "${release_dir}/BOM_APPROVED.csv"
cp "${approved_cpl}" "${release_dir}/CPL_APPROVED.csv"
echo "Release files exported to ${release_dir}. Confirm Gerber/CPL visual previews before JLCPCB submission."
