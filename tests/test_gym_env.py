import numpy as np
import pytest

gym = pytest.importorskip("gymnasium")
from gymnasium.utils.env_checker import check_env
from common.generator import random_instance
from common.validate import validate_schedule
from env.features import N_FEATURES, build_job_features
from env.gym_env import JobShopEnv
from env.simulator import JobShopSimulator


def rollout(env, rng):
    obs, _ = env.reset()
    total, steps, info = 0.0, 0, {}
    while True:
        a = int(rng.choice(np.flatnonzero(env.action_masks())))
        obs, r, done, trunc, info = env.step(a)
        total += r
        steps += 1
        if done:
            return total, steps, info


class _MapInvalidToValid(gym.Wrapper):
    def step(self, action):
        mask = self.env.unwrapped.action_masks()
        if not mask[action]:
            action = int(np.flatnonzero(mask)[0])
        return self.env.step(action)


def test_gymnasium_checker():
    check_env(_MapInvalidToValid(JobShopEnv(seed=0)), skip_render_check=True)


def test_obs_shapes_and_mask():
    env = JobShopEnv(pad_jobs=16, seed=1)
    obs, info = env.reset()
    n = info["n_jobs"]
    assert obs["jobs"].shape == (16, N_FEATURES) and obs["mask"].shape == (16,)
    assert obs["mask"][:n].all() and not obs["mask"][n:].any()
    assert np.isfinite(obs["jobs"]).all()
    assert not obs["jobs"][n:].any()         


def test_mask_false_exactly_for_finished_jobs():
    env = JobShopEnv(pad_jobs=16, seed=2)
    env.reset()
    sim = env.sim
    while not sim.done():
        mask = env.action_masks()
        for j in range(sim.inst.n_jobs):
            assert mask[j] == (sim.next_op[j] < len(sim.inst.machines[j]))
        env.step(int(np.flatnonzero(mask)[0]))


def test_episode_return_equals_minus_gap_to_initial_lb():
    rng = np.random.default_rng(0)
    env = JobShopEnv(seed=3)
    for _ in range(20):
        total, steps, info = rollout(env, rng)
        assert steps == sum(len(r) for r in env.sim.inst.machines)
        assert info["makespan"] == validate_schedule(env.sim.inst, env.sim.to_schedule())
        assert total == pytest.approx(-(info["makespan"] - info["lb0"]) / info["lb0"])


def test_same_seed_same_instance_and_sizes_in_range():
    a, b = JobShopEnv(seed=7), JobShopEnv(seed=7)
    for _ in range(5):
        a.reset(); b.reset()
        assert a.sim.inst == b.sim.inst
        assert 5 <= a.sim.inst.n_jobs <= 12 and 4 <= a.sim.inst.n_machines <= 12


def test_reset_with_given_instance_and_too_large():
    env = JobShopEnv(pad_jobs=8)
    inst = random_instance(6, 4, np.random.default_rng(0))
    env.reset(options={"instance": inst})
    assert env.sim.inst is inst
    with pytest.raises(ValueError):
        env.reset(options={"instance": random_instance(9, 3, np.random.default_rng(0))})


def test_invalid_action_raises():
    env = JobShopEnv(pad_jobs=16, seed=4)
    _, info = env.reset()
    with pytest.raises(ValueError):
        env.step(15)                      


def test_features_bounded_on_random_instances():
    rng = np.random.default_rng(9)
    for _ in range(20):
        inst = random_instance(int(rng.integers(2, 12)), int(rng.integers(2, 9)), rng)
        sim = JobShopSimulator().reset(inst)
        while not sim.done():
            f = build_job_features(sim)
            assert np.isfinite(f).all() and f.min() >= 0 and f.max() <= 10
            sim.step(int(rng.choice(sim.ready_jobs())))



def test_size_mix_sampling():
    mix = [[10, 10, 0.3], [12, 12, 0.3], [15, 15, 0.3], [20, 15, 0.1]]
    env = JobShopEnv(size_mix=mix, pad_jobs=32, seed=0)
    seen = set()
    for _ in range(200):
        _, info = env.reset()
        seen.add((info["n_jobs"], info["n_machines"]))
    assert seen == {(10, 10), (12, 12), (15, 15), (20, 15)}
    rng = np.random.default_rng(1)
    total, steps, info = rollout(env, rng)
    assert steps == info["n_jobs"] * info["n_machines"]