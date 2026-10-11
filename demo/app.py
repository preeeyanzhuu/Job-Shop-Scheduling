import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))        

import streamlit as st

from common.generator import random_instance
from common.validate import validate_schedule
from demo.gantt import make_gantt
from evaluation.benchmark import get_solver, load_benchmarks
from evaluation.metrics import machine_idle_time
import numpy as np

st.set_page_config(page_title="Instant Factory Scheduling", layout="wide")
st.title("Job Shop Scheduling with RL")
st.caption("Near-best job shop schedules in a fraction of a second.")

METHODS = ["SPT", "MWKR", "FIFO", "RL", "RLBEST@20", "HYBRID@1", "HYBRID@5", "HYBRID@10",
           "CPSAT@1", "CPSAT@5", "CPSAT@10", "CPSAT@60"]

with st.sidebar:
    st.header("Instance")
    source = st.radio("Source", ["Benchmark", "Random"])
    if source == "Benchmark":
        bench = {i.name: i for i in load_benchmarks()}
        if not bench:
            st.error("No benchmark files in data/benchmarks/")
            st.stop()
        instance = bench[st.selectbox("Instance", list(bench))]
    else:
        nj = st.slider("Jobs", 3, 30, 8)       
        nm = st.slider("Machines", 3, 30, 6)
        seed = st.number_input("Seed", 0, 9999, 0)
        instance = random_instance(nj, nm, np.random.default_rng(int(seed)))
    st.header("Methods")
    left = st.selectbox("Left chart", METHODS, index=0)
    right = st.selectbox("Right chart", METHODS, index=METHODS.index("HYBRID@10"))
    model_files = sorted(p.name for p in (ROOT / "models").glob("*.zip"))
    if model_files:
        prefer = [f for f in ("ppo_large_gt_best.zip", "ppo_v5_best.zip", "ppo_v2_best.zip") if f in model_files]
        default = model_files.index(prefer[0]) if prefer else 0
        model_path = "models/" + st.selectbox("RL model", model_files, index=default)
    else:
        model_path = "models/none.zip"
        st.warning("No .zip files found in the models/ folder.")
    run = st.button("Schedule", type="primary")

st.write(f"**{instance.name}**: {instance.n_jobs} jobs x {instance.n_machines} machines")

if run:
    results = []
    for name in (left, right):
        try:
            with st.spinner(f"Running {name} ..."):
                solver, label = get_solver(name, str(ROOT / model_path))
                sch = solver.solve(instance)
                validate_schedule(instance, sch)
            results.append((label, sch))
        except Exception as e:                            
            st.error(f"{name} failed: {e}")
    if len(results) == 2:
        st.session_state["results"] = (instance, results)

if "results" in st.session_state:
    inst, results = st.session_state["results"]
    x_max = max(s.makespan for _, s in results)     
    cols = st.columns(2)
    for idx, (col, (label, sch)) in enumerate(zip(cols, results)):
        with col:
            st.plotly_chart(make_gantt(inst, sch, label, x_max), width="stretch",
                            key=f"gantt_{idx}")
            a, b, c = st.columns(3)
            a.metric("Makespan", sch.makespan)
            b.metric("Solve time", f"{sch.solve_time:.3f}s")
            c.metric("Idle time", machine_idle_time(inst, sch))
            if label == "RL(stub)":
                st.warning("No trained model found: showing the random stub.")
else:
    st.info("Pick an instance and two methods, then press Schedule.")