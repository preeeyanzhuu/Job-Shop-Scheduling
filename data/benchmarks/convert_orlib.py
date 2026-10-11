import sys
from pathlib import Path
from common.types import Instance
from common.io import save_instance

KEEP = {"ft06", "ft10", "ft20", "la31", "la32", "la33", "la34", "la35", "la36", "yn1", "abz7"}


def parse(text):
    lines = [l.strip() for l in text.splitlines()]
    out, i = [], 0
    while i < len(lines):
        if lines[i].lower().startswith("instance"):
            name = lines[i].split()[1]
            i += 1
            while True:            
                p = lines[i].split()
                if len(p) == 2 and all(x.isdigit() for x in p):
                    break
                i += 1
            n, m = map(int, p)
            machines, durations = [], []
            for r in range(1, n + 1):
                v = list(map(int, lines[i + r].split()))
                machines.append(v[0::2])
                durations.append(v[1::2])
            out.append(Instance(name, n, m, machines, durations))
            i += n + 1
        else:
            i += 1
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m data.benchmarks.convert_orlib data\\benchmarks\\jobshop1.txt")
    src = Path(sys.argv[1])
    keep_all = "--all" in sys.argv
    for inst in parse(src.read_text()):
        if keep_all or inst.name in KEEP:
            save_instance(inst, src.parent / f"{inst.name}.json")
            print("saved", inst.name, inst.n_jobs, "x", inst.n_machines)