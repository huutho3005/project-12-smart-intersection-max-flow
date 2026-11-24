"""SMART INTERSECTION benchmark. Place in root of submitted source, run:
python benchmark.py --output outputs/benchmark --batches 9 --reps 1000 --large-reps 5 --warmup 20
Only algorithm is timed. Raw repetitions, machine info and batch medians saved.
"""
import argparse, csv, hashlib, json, platform, statistics, sys, time
from pathlib import Path
from graph import FlowGraph
from scenario import load_scenario
from ford_fulkerson import ford_fulkerson_dfs
from edmonds_karp import edmonds_karp


def small_graph():
    g = FlowGraph(['SS', 'A', 'B', 'C', 'D', 'TT'])
    for x in 'ABCD':
        g.add_edge('IN_' + x, 'SS', x, 3)
        g.add_edge('OUT_' + x, x, 'TT', 3)
    return g


def large_graph(base, n=10):
    nodes = ['SS', 'TT'] + [f'C{k}_{v}' for k in range(n) for v in base.nodes if v not in ('SS', 'TT')]
    g = FlowGraph(nodes)
    for k in range(n):
        for e in base.edges:
            u = e['u'] if e['u'] in ('SS', 'TT') else f'C{k}_{e["u"]}'
            v = e['v'] if e['v'] in ('SS', 'TT') else f'C{k}_{e["v"]}'
            g.add_edge(f'C{k}_{e["id"]}', u, v, e['capacity'])
    return g


def measure(g, func, label, method, repeats, batches, warmup, writer):
    exp, hist = func(g.clone())
    for _ in range(warmup):
        assert func(g.clone())[0] == exp
    meds = []
    for batch in range(1, batches+1):
        vals = []
        for rep in range(1, repeats+1):
            clean = g.clone()  # graph construction excluded from time
            t = time.perf_counter_ns()
            got, _ = func(clean)
            ms = (time.perf_counter_ns() - t)/1e6
            assert got == exp
            writer.writerow([label, method, batch, rep, f'{ms:.9f}', exp])
            vals.append(ms)
        meds.append(statistics.median(vals))
    return dict(graph=label, algorithm=method, vertices=len(g.nodes), edges=len(g.edges),
                max_flow=exp, iterations=len(hist), batches=batches, reps_per_batch=repeats,
                warmup=warmup, median_of_batch_medians_ms=round(statistics.median(meds),6),
                batch_medians_ms=[round(x,6) for x in meds])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', default='benchmark_out')
    parser.add_argument('--batches', type=int, default=9)
    parser.add_argument('--reps', type=int, default=1000)
    parser.add_argument('--large-reps', type=int, default=5)
    parser.add_argument('--warmup', type=int, default=20)
    args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    base01,*_=load_scenario('SC01'); base02,*_=load_scenario('SC02')
    cases=[('Small-6v-8e',small_graph(),args.reps), ('SC01',base01,args.reps),
           ('SC02',base02,args.reps),('Large-322v-440e',large_graph(base01),args.large_reps)]
    summary=[]
    with (out/'benchmark_raw.csv').open('w', newline='', encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow(['graph','algorithm','batch','repetition','algorithm_time_ms','max_flow'])
        for label,g,reps in cases:
            for name,fn in [('DFS',ford_fulkerson_dfs),('BFS',edmonds_karp)]:
                result=measure(g,fn,label,name,reps,args.batches,args.warmup,writer)
                summary.append(result)
                print(label,name,result['median_of_batch_medians_ms'],'ms',flush=True)
    cols=['graph','algorithm','vertices','edges','max_flow','iterations','batches','reps_per_batch','warmup','median_of_batch_medians_ms']
    with (out/'benchmark_summary.csv').open('w', newline='', encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=cols); writer.writeheader()
        for row in summary: writer.writerow({key:row[key] for key in cols})
    cpu='not recorded'
    cp=Path('/proc/cpuinfo')
    if cp.exists():
        for line in cp.read_text(errors='replace').splitlines():
            if line.startswith('model name'):
                cpu=line.split(':',1)[1].strip();break
    ram=None
    mem=Path('/proc/meminfo')
    if mem.exists():
        for line in mem.read_text().splitlines():
            if line.startswith('MemTotal:'):
                ram=int(line.split()[1])*1024;break
    record={'python':sys.version,'os':platform.platform(),'cpu':cpu,'ram_bytes':ram,
            'timer':'time.perf_counter_ns()', 'source':'source hien hanh sau toi uu edge_ids, tai do truc tiep',
            'source_sha256':{name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in
                ['graph.py','bfs.py','ford_fulkerson.py','edmonds_karp.py','scenario.py','benchmark.py']},
            'excluded_from_timer':['CSV load','graph construction','graph cloning','UI','Plotly'],
            'method':'median of 9 per-batch medians; one new graph for every run',
            'args':vars(args),'results':summary}
    (out/'benchmark_metadata.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
