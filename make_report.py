
import csv
import html

with open("threshold_results.csv", newline="") as f:
    rows = list(csv.DictReader(f))

baseline = next(r for r in rows if r["threshold"] == "baseline")
base_ipc = float(baseline["ipc"])

def make_svg(title, key, ylabel, filename):
    selected = rows
    labels = [r["threshold"] for r in selected]
    values = [float(r[key]) for r in selected]
    width, height = 760, 340
    left, right, top, bottom = 80, 25, 50, 65
    plot_w, plot_h = width - left - right, height - top - bottom
    vmax = max(values) * 1.12
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="25" text-anchor="middle" font-size="17">{html.escape(title)}</text>',
        f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle">{html.escape(ylabel)}</text>',
    ]
    for i in range(5):
        val = vmax * i / 4
        y = top + plot_h * (1 - i / 4)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#ddd"/>')
        parts.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-size="11">{val:.4f}</text>')
    step = plot_w / len(values)
    bar_w = step * 0.55
    for i, (label, val) in enumerate(zip(labels, values)):
        x = left + i * step + (step - bar_w) / 2
        bar_h = plot_h * val / vmax
        y = top + plot_h - bar_h
        parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="#3478b8"/>')
        parts.append(f'<text x="{x+bar_w/2}" y="{y-5}" text-anchor="middle" font-size="10">{val:.5f}</text>')
        parts.append(f'<text x="{x+bar_w/2}" y="{top+plot_h+20}" text-anchor="middle" font-size="11">{html.escape(label)}</text>')
    parts.append("</svg>")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("".join(parts))

make_svg("IPC by Threshold", "ipc", "IPC", "ipc_plot.svg")
make_svg("Total L2C MPKI by Threshold", "total_mpki", "MPKI", "mpki_plot.svg")

with open("Summary.html", "w", encoding="utf-8") as f:
    f.write("""<!doctype html><html><head><meta charset="utf-8">
<title>CS683 PA2 Dynamic I-RRIP</title>
<style>
body{font-family:Arial,sans-serif;margin:32px;color:#202833;line-height:1.45}
h1,h2{color:#17365d}table{border-collapse:collapse;width:100%;font-size:12px}
th,td{border:1px solid #aaa;padding:7px;text-align:center}
th{background:#eaf0f7}img{width:100%;max-width:760px}
</style></head><body>
<h1>CS683 PA2: Dynamic I-RRIP</h1>
<p>Trace1.gz; single-core ChampSim; 25 million warmup and 25 million simulation instructions.</p>
<h2>Experimental results</h2>
<table><tr><th>Threshold</th><th>IPC</th><th>Speedup</th><th>Total MPKI</th>
<th>Data-load MPKI</th><th>Instruction-load MPKI</th><th>Follower policy</th></tr>
""")
    for r in rows:
        speedup = float(r["ipc"]) / base_ipc
        f.write(
            "<tr>" +
            "".join(f"<td>{html.escape(str(v))}</td>" for v in [
                r["threshold"], f'{float(r["ipc"]):.6f}',
                f'{speedup:.6f}x', r["total_mpki"],
                r["data_load_mpki"], r["instruction_load_mpki"],
                r["follower_policy"]
            ]) + "</tr>\n"
        )
    f.write("""</table>
<h2>IPC by threshold</h2><img src="ipc_plot.svg">
<h2>Total L2C MPKI by threshold</h2><img src="mpki_plot.svg">
<h2>Discussion</h2>
<p>Baseline SRRIP IPC is 0.232232. Threshold 0.25 has IPC 0.232396,
but total L2C MPKI rises from 23.7991 to 28.5162. Instruction-load MPKI
falls while data-load MPKI rises, indicating a trade-off rather than a
substantial overall performance improvement.</p>
<p>Thresholds 0.50, 0.75 and 0.90 have identical measured results and
finish with RRIP as the follower policy. Thresholds 0.10 and 0.25 finish
with I-RRIP. Only Trace1 was available for this sweep, so results should
not be generalized to other workloads.</p>
</body></html>""")

print("Created Summary.html, ipc_plot.svg, and mpki_plot.svg")
