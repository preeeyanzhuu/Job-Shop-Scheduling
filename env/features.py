import numpy as np

FEATURE_NAMES = [
    "remaining_work/LB",    
    "remaining_ops/n_machines", 
    "next_duration/LB",          
    "earliest_start-now /LB",    
    "machine_busy_until-now/LB", 
    "job_ready-now /LB",         
    "machine_remaining_load/LB",
    "next_duration/max_next",   
    "remaining_work/max_work",  
    "is_candidate",         
]
N_FEATURES = len(FEATURE_NAMES)


def build_job_features(sim) -> np.ndarray:

    n = sim.inst.n_jobs
    feats = np.zeros((n, N_FEATURES), dtype=np.float32)
    ready = sim.ready_jobs()
    if not ready:
        return feats

    lb = max(sim.lower_bound(), 1)
    est = {j: sim.earliest_start(j) for j in ready}
    now = min(est.values())
    max_next = max(sim.next_duration(j) for j in ready)
    max_work = max(sim.remaining_work[j] for j in ready)
    n_mach = sim.inst.n_machines

    for j in ready:
        m = sim.next_machine(j)
        d = sim.next_duration(j)
        feats[j] = (
            sim.remaining_work[j] / lb,
            (len(sim.inst.machines[j]) - sim.next_op[j]) / n_mach,
            d / lb,
            (est[j] - now) / lb,
            max(sim.machine_free[m] - now, 0) / lb,
            max(sim.job_ready[j] - now, 0) / lb,
            sim.remaining_load[m] / lb,
            d / max_next,
            sim.remaining_work[j] / max_work,
            1.0 if est[j] == now else 0.0,
        )
    return feats