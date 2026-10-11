import numpy as np

from common.types import Instance, Schedule, ScheduledOp

N_FEATURES = 10
_BIG = 1 << 60


class BatchSim:
    def __init__(self, instance: Instance, batch: int = 1, mask_mode: str = "gt"):
        if mask_mode not in ("any", "gt"):
            raise ValueError("mask_mode must be 'any' or 'gt'")
        self.inst, self.B, self.mask_mode = instance, int(batch), mask_mode
        n, M = instance.n_jobs, instance.n_machines
        self.n, self.M = n, M
        self.lens = np.array([len(r) for r in instance.machines], dtype=np.int64)
        K = int(self.lens.max())
        self.K = K
        mach = np.zeros((n, K + 1), dtype=np.int64) 
        dur = np.zeros((n, K + 1), dtype=np.int64)
        for j in range(n):
            mach[j, :self.lens[j]] = instance.machines[j]
            dur[j, :self.lens[j]] = instance.durations[j]
        self.mach_flat, self.dur_flat = mach.ravel(), dur.ravel()
        self.base = (np.arange(n, dtype=np.int64) * (K + 1))[None, :]     
        self.boffM = (np.arange(self.B, dtype=np.int64) * M)[:, None]
        self.ar = np.arange(self.B)
        self.total_ops = int(self.lens.sum())
        self._work0 = np.array([sum(d) for d in instance.durations], dtype=np.int64)
        load = np.zeros(M, dtype=np.int64)
        for mm, d in zip(instance.machines, instance.durations):
            for a, b in zip(mm, d):
                load[a] += b
        self._load0 = load
        self.reset()

    def reset(self):
        B, n, M = self.B, self.n, self.M
        self.nxt = np.zeros((B, n), dtype=np.int64)
        self.jr = np.zeros((B, n), dtype=np.int64)    
        self.mf = np.zeros((B, M), dtype=np.int64)             
        self.rw = np.tile(self._work0, (B, 1))          
        self.rl = np.tile(self._load0, (B, 1))             
        self.starts = np.zeros((B, n, self.K), dtype=np.int64)
        self.nm = np.tile(self.mach_flat[self.base[0]], (B, 1))   
        self.nd = np.tile(self.dur_flat[self.base[0]], (B, 1))
        self.ready = np.tile(self.lens > 0, (B, 1))             
        self.jb = self.jr + self.rw                            
        self.mb = self.mf + self.rl                               
        self.steps = 0
        return self

    def done(self) -> bool:
        return self.steps >= self.total_ops

    def observe(self):
        """Return (features float32 (B,n,10), ready bool (B,n), action_mask bool (B,n))."""
        nm, nd, ready = self.nm, self.nd, self.ready
        mf_flat, rl_flat = self.mf.ravel(), self.rl.ravel()
        mfj = mf_flat[nm + self.boffM]                    
        est = np.maximum(self.jr, mfj)                

        lb = np.maximum(self.jb.max(1), self.mb.max(1))
        lbc = np.maximum(lb, 1)[:, None].astype(np.float64)
        now = np.where(ready, est, _BIG).min(1)[:, None]
        max_next = np.where(ready, nd, 0).max(1)[:, None]
        max_work = np.where(ready, self.rw, 0).max(1)[:, None]

        f = np.empty((N_FEATURES, self.B, self.n), dtype=np.float64)
        np.divide(self.rw, lbc, out=f[0])
        np.divide(self.lens - self.nxt, self.M, out=f[1])
        np.divide(nd, lbc, out=f[2])
        np.divide(est - now, lbc, out=f[3])
        np.divide(np.maximum(mfj - now, 0), lbc, out=f[4])
        np.divide(np.maximum(self.jr - now, 0), lbc, out=f[5])
        np.divide(rl_flat[nm + self.boffM], lbc, out=f[6])
        np.divide(nd, np.maximum(max_next, 1), out=f[7])
        np.divide(self.rw, np.maximum(max_work, 1), out=f[8])
        f[9] = est == now
        f *= ready                                       
        feats = np.clip(f.astype(np.float32).transpose(1, 2, 0), -10.0, 10.0)

        if self.mask_mode == "any":
            mask = ready
        else:                                         
            ect = est + nd
            best = np.where(ready, ect, _BIG).argmin(1)     
            mstar = nm[self.ar, best][:, None]
            ec = ect[self.ar, best][:, None]
            mask = ready & (nm == mstar) & (est < ec)
            mask[self.ar, best] = True
        return feats, ready.copy(), (ready.copy() if self.mask_mode == "any" else mask)

    def step(self, jobs):
        ar = self.ar
        k = self.nxt[ar, jobs]
        idx = jobs * (self.K + 1) + k
        m = self.mach_flat[idx]
        d = self.dur_flat[idx]
        start = np.maximum(self.jr[ar, jobs], self.mf[ar, m])
        end = start + d
        self.starts[ar, jobs, k] = start
        self.jr[ar, jobs] = end
        self.mf[ar, m] = end
        self.rw[ar, jobs] -= d
        self.rl[ar, m] -= d
        k1 = k + 1
        self.nxt[ar, jobs] = k1
        idx1 = jobs * (self.K + 1) + k1
        self.nm[ar, jobs] = self.mach_flat[idx1]
        self.nd[ar, jobs] = self.dur_flat[idx1]
        self.ready[ar, jobs] = k1 < self.lens[jobs]
        self.jb[ar, jobs] = end + self.rw[ar, jobs]
        self.mb[ar, m] = end + self.rl[ar, m]
        self.steps += 1

    def makespans(self):
        return self.jr.max(1)

    def to_schedule(self, b=0, method="SIM", solve_time=0.0) -> Schedule:
        ops = []
        for j in range(self.n):
            for k in range(int(self.lens[j])):
                s = int(self.starts[b, j, k])
                ops.append(ScheduledOp(j, k, int(self.inst.machines[j][k]), s,
                                       s + int(self.inst.durations[j][k])))
        return Schedule(ops, method, solve_time, False)
