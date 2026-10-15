
import csv
import html
from collections import OrderedDict

with open("threshold_results.csv", newline="") as f:
    rows = list(csv.DictReader(f))

traces = OrderedDict()
for r in rows:
    traces.setdefault(r["trace"], []).append(r)

for trace, group in traces.items():
    baseline = next(r for r in group if r["threshold"] == "baseline")
    base_ipc = float(baseline["ipc"])
    for r in group:
        r["speedup"] = float(r["ipc"]) / base_ipc

def make_svg(trace, metric, label, filename):
    group = [r for r in traces[trace] if r["threshold"] != "baseline"]
    values = [float(r[metric]) for r in group]
    labels = [r["threshold"] for r in group]
    width, height = 760, 340
    left, right, top, bottom = 85, 25, 50, 65
    pw, ph = width - left - right, height - top - bottom
    vmax = max(values) * 1.12

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="380" y="25" text-anchor="middle" font-size="17">{html.escape(trace + " - " + label)}</text>',
        f'<text x="20" y="170" transform="rotate(-90 20 170)" text-anchor="middle">{label}</text>'
    ]
    for i in range(5):
        y = top + ph * (1 - i / 4)
        v = vmax * i / 4
        out.append(f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#ddd"/>')
        out.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-size="11">{v:.4f}</text>')

    step = pw / len(values)
    bw = step * 0.55
    for i, (name, value) in enumerate(zip(labels, values)):
        x = left + i * step + (step - bw) / 2
        bh = ph * value / vmax
        y = top + ph - bh
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="#3478b8"/>')
        out.append(f'<text x="{x+bw/2}" y="{y-5}" text-anchor="middle" font-size="10">{value:.5f}</text>')
        out.append(f'<text x="{x+bw/2}" y="{top+ph+20}" text-anchor="middle" font-size="11">{name}</text>')
    out.append("</svg>")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("".join(out))

for trace in traces:
    name = trace.lower()
    make_svg(trace, "ipc", "IPC", name + "_ipc.svg")
    make_svg(trace, "total_mpki", "Total L2C MPKI", name + "_mpki.svg")

def td(value):
    return "<td>" + html.escape(str(value)) + "</td>"

with open("Summary.html", "w", encoding="utf-8") as f:
    f.write("""<!doctype html><html><head><meta charset="utf-8">
<title>CS683 PA2 Dynamic I-RRIP</title>
<style>
body{font-family:Arial,sans-serif;margin:30px;color:#202833;line-height:1.45}
h1,h2,h3{color:#17365d}
table{border-collapse:collapse;width:100%;font-size:12px;margin-bottom:25px}
th,td{border:1px solid #aaa;padding:7px;text-align:center}
th{background:#eaf0f7}
img{width:100%;max-width:760px;display:block;margin-bottom:25px}
</style></head><body>
<h1>CS683 PA2: Dynamic I-RRIP</h1>
<p>Single-core ChampSim evaluation using Trace1.gz, Trace2.gz and Trace3.gz.
Each run uses 25 million warmup instructions and 25 million simulation instructions.</p>
<h2>Methodology</h2>
<p><b>Set dueling:</b> L2 sets 0-15 are fixed SRRIP leaders, sets 16-31 are
fixed I-RRIP leaders, and all remaining sets are followers controlled by
the selector.</p>
<p><b>Selector statistic:</b> Counters are updated on accesses to either
leader group. Let I_A and I_M be instruction accesses and misses, and A
and M be total accesses and misses in leader sets. The score is
<b>(I_A + I_M) / (A + M)</b>. The selector chooses I-RRIP for followers
when the score exceeds the configured threshold; otherwise it chooses SRRIP.
The tested thresholds are 0.10, 0.25, 0.50, 0.75 and 0.90.</p>
<p><b>Insertion and replacement:</b> Hits reset RRPV to 0. Instruction
lines are inserted at RRPV 2. Under I-RRIP, data lines are inserted at
RRPV 3; otherwise lines are inserted at RRPV 2. Victim selection chooses
a line at RRPV 3, incrementing RRPVs when needed.</p>
<p><b>Measurement:</b> Each trace is evaluated independently with identical
warmup and simulation lengths. Speedup is configuration IPC divided by
that trace's baseline SRRIP IPC.</p>
<h2>Results</h2>
""")
    for trace, group in traces.items():
        f.write("<h3>" + html.escape(trace) + "</h3>")
        f.write("""<table><tr><th>Threshold</th><th>IPC</th><th>Speedup</th>
<th>Total MPKI</th><th>Data-load MPKI</th><th>Instruction-load MPKI</th>
<th>Follower policy</th></tr>""")
        group = sorted(group, key=lambda r: (
            r["threshold"] != "baseline",
            float(r["threshold"]) if r["threshold"] != "baseline" else -1
        ))
        for r in group:
            f.write("<tr>")
            for v in [
                r["threshold"], f'{float(r["ipc"]):.6f}',
                f'{r["speedup"]:.6f}x', f'{float(r["total_mpki"]):.5f}',
                f'{float(r["data_load_mpki"]):.5f}',
                f'{float(r["instruction_load_mpki"]):.5f}',
                r["follower_policy"]
            ]:
                f.write(td(v))
            f.write("</tr>")
        f.write("</table>")
        name = trace.lower()
        f.write(f'<h3>{trace}: IPC by threshold</h3><img src="{name}_ipc.svg">')
        f.write(f'<h3>{trace}: Total MPKI by threshold</h3><img src="{name}_mpki.svg">')

    f.write("<h2>Discussion</h2>")
    for trace, group in traces.items():
        base = next(r for r in group if r["threshold"] == "baseline")
        best = max((r for r in group if r["threshold"] != "baseline"),
                   key=lambda r: float(r["ipc"]))
        change = (best["speedup"] - 1) * 100
        f.write(
            f"<p><b>{trace}:</b> Baseline IPC is {float(base['ipc']):.6f}. "
            f"The highest measured IPC is {float(best['ipc']):.6f} at threshold "
            f"{best['threshold']} ({change:+.3f}% versus baseline). Total MPKI "
            f"changes from {float(base['total_mpki']):.4f} to "
            f"{float(best['total_mpki']):.4f}. These results show that the "
            "effect of the threshold depends on the workload.</p>"
        )
    f.write("</body></html>")

print(f"Created Summary.html and six SVG plots for {len(traces)} traces.")
print(f"Loaded {len(rows)} result rows.")
