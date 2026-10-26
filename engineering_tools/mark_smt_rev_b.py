"""Mark Rev B custom copper-pad packages as SMT so JLC CPL includes them.

These are real SMD components. J2/J3 handwork and TP1 are excluded.
"""

import sys
import pcbnew as p


ASSEMBLY_SMD = {'L1', 'Q1', 'U2', 'U3', 'D1'}


def main(path):
    b = p.LoadBoard(path)
    found = set()
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if ref in ASSEMBLY_SMD:
            assert not fp.GetAttributes() & p.FP_THROUGH_HOLE, ref
            fp.SetAttributes(fp.GetAttributes() | p.FP_SMD)
            found.add(ref)
    assert found == ASSEMBLY_SMD, ('Missing SMT footprint', ASSEMBLY_SMD - found)
    p.SaveBoard(path, b)
    print('Updated custom SMD attributes:', ', '.join(sorted(found)))


if __name__ == '__main__':
    main(sys.argv[1])
