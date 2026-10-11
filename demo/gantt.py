import plotly.express as px
import plotly.graph_objects as go

PALETTE = px.colors.qualitative.Dark24  


def make_gantt(instance, schedule, title, x_max=None):
    fig = go.Figure()
    for j in range(instance.n_jobs):
        ops = sorted((o for o in schedule.ops if o.job == j), key=lambda o: o.op)
        fig.add_trace(go.Bar(
            name=f"Job {j}", orientation="h",
            y=[f"M{o.machine}" for o in ops],
            x=[o.end - o.start for o in ops],
            base=[o.start for o in ops],
            marker=dict(color=PALETTE[j % len(PALETTE)], line=dict(color="white", width=1)),
            hovertext=[f"Job {j}, op {o.op}<br>M{o.machine}: {o.start} to {o.end}" for o in ops],
            hoverinfo="text"))
    machines = [f"M{m}" for m in range(instance.n_machines)]
    fig.update_layout(
        title=f"{title} (makespan {schedule.makespan})", barmode="overlay",
        xaxis=dict(title="Time", range=[0, (x_max or schedule.makespan) * 1.02]),
        yaxis=dict(categoryorder="array", categoryarray=machines[::-1], title=""),
        legend=dict(orientation="h", y=-0.25), height=420, margin=dict(l=40, r=20, t=60, b=40))
    return fig