// Edmonds-Karp C++17 doc lap: doc Nodes.csv / Edges.csv, KHONG goi ma Python.
// Dich: g++ -std=c++17 -O2 -Wall -Wextra cpp_edmonds_karp.cpp -o ek_cpp
// Chay: ./ek_cpp --all  (khi dang trong thu muc du an)
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

struct Arc { int to, rev; long long residual; };
struct Original { string id; int from, to, arc_index; long long capacity; };

vector<string> split_csv(const string &line) {
    vector<string> fields;
    string cur;
    bool quoted = false;
    for (size_t i = 0; i < line.size(); ++i) {
        char ch = line[i];
        if (ch == '"') {
            if (quoted && i + 1 < line.size() && line[i+1] == '"') {cur += '"'; ++i;}
            else quoted = !quoted;
        } else if (ch == ',' && !quoted) {fields.push_back(cur); cur.clear();}
        else if (ch != '\r') cur += ch;
    }
    if (quoted) throw runtime_error("CSV co nhay kep chua dong");
    fields.push_back(cur);
    return fields;
}

struct Table { vector<string> names; vector<vector<string>> rows; };
Table read_csv(const string &filename) {
    ifstream f(filename);
    if (!f) throw runtime_error("Khong mo duoc file: " + filename);
    string line;
    if (!getline(f, line)) throw runtime_error("CSV rong: " + filename);
    // Remove UTF-8 BOM if present.
    if (line.size() >= 3 && (unsigned char)line[0] == 0xef &&
        (unsigned char)line[1] == 0xbb && (unsigned char)line[2] == 0xbf)
        line.erase(0, 3);
    Table t;
    t.names = split_csv(line);
    while (getline(f, line)) {
        if (line.empty() || line == "\r") continue;
        auto row = split_csv(line);
        if (row.size() != t.names.size()) throw runtime_error("Sai so cot: " + filename);
        t.rows.push_back(row);
    }
    return t;
}
string field(const Table &t, const vector<string> &r, const string &name) {
    auto it = find(t.names.begin(), t.names.end(), name);
    if (it == t.names.end()) throw runtime_error("Thieu cot " + name);
    return r[it - t.names.begin()];
}

struct Network {
    map<string, int> ids;
    vector<vector<Arc>> adj;
    vector<Original> original;
    int get_node(const string &name) const {
        auto it = ids.find(name);
        if (it == ids.end()) throw runtime_error("Dinh khong ton tai: " + name);
        return it->second;
    }
    void add_node(const string &name) {
        if (name.empty() || ids.count(name)) throw runtime_error("ID dinh rong/trung");
        ids[name] = (int)adj.size();
        adj.emplace_back();
    }
    void add_edge(const string &id, const string &from, const string &to, long long c) {
        int u = get_node(from), v = get_node(to);
        if (u == v || c < 0) throw runtime_error("Canh tu noi hoac capacity am: " + id);
        for (const auto &x : original) if (x.id == id) throw runtime_error("Trung id canh: " + id);
        int i = (int)adj[u].size(), j = (int)adj[v].size();
        adj[u].push_back({v, j, c});
        adj[v].push_back({u, i, 0});
        original.push_back({id, u, v, i, c});
    }
    long long solve(const string &source, const string &target, int &count) {
        int s = get_node(source), t = get_node(target);
        if (s == t) throw runtime_error("Source trung Sink");
        long long total = 0; count = 0;
        while (true) {
            vector<int> parent(adj.size(), -1), which(adj.size(), -1);
            queue<int> q;
            q.push(s); parent[s] = s;
            while (!q.empty() && parent[t] == -1) {
                int u = q.front(); q.pop();
                for (int i = 0; i < (int)adj[u].size(); ++i) {
                    const Arc &a = adj[u][i];
                    if (a.residual > 0 && parent[a.to] == -1) {
                        parent[a.to] = u;
                        which[a.to] = i;
                        q.push(a.to);
                    }
                }
            }
            if (parent[t] == -1) break;
            long long delta = (1LL << 60);
            for (int v = t; v != s; v = parent[v])
                delta = min(delta, adj[parent[v]][which[v]].residual);
            for (int v = t; v != s; v = parent[v]) {
                Arc &forward = adj[parent[v]][which[v]];
                adj[v][forward.rev].residual += delta;
                forward.residual -= delta;
            }
            total += delta;
            ++count;
        }
        return total;
    }
    long long verify(int s, int t, long long total) const {
        vector<long long> balance(adj.size(), 0);
        for (const auto &e : original) {
            long long flow = e.capacity - adj[e.from][e.arc_index].residual;
            if (flow < 0 || flow > e.capacity) throw runtime_error("Capacity constraint failed");
            balance[e.from] -= flow; balance[e.to] += flow;
        }
        for (int v = 0; v < (int)adj.size(); ++v) {
            if (v != s && v != t && balance[v] != 0)
                throw runtime_error("Flow conservation failed");
        }
        if (balance[s] != -total || balance[t] != total)
            throw runtime_error("Source/Sink flow mismatch");
        vector<bool> reachable(adj.size(), false);
        queue<int> q; q.push(s); reachable[s] = true;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (const auto &a : adj[u]) if (a.residual > 0 && !reachable[a.to]) {
                reachable[a.to] = true; q.push(a.to);
            }
        }
        if (reachable[t]) throw runtime_error("Van con duong tang");
        long long cut = 0;
        for (const auto &e : original) if (reachable[e.from] && !reachable[e.to])
            cut += e.capacity;
        if (cut != total) throw runtime_error("MaxFlow != MinCut");
        return cut;
    }
};

Network read_network(const string &root, const string &sid) {
    Network g;
    Table nodes = read_csv(root + "/Nodes.csv");
    for (const auto &r : nodes.rows) g.add_node(field(nodes, r, "node_id"));
    Table edges = read_csv(root + "/scenarios/" + sid + "/Edges.csv");
    for (const auto &r : edges.rows) {
        const string ctext = field(edges, r, "capacity");
        size_t pos = 0;
        long long c = stoll(ctext, &pos);
        if (pos != ctext.size()) throw runtime_error("Capacity khong phai so nguyen");
        g.add_edge(field(edges, r, "edge_id"), field(edges, r, "from_node_id"),
                   field(edges, r, "to_node_id"), c);
    }
    if (g.ids.size() != 34 || g.original.size() != 44)
        throw runtime_error("Sai 34 dinh/44 canh");
    return g;
}

int main(int argc, char **argv) {
    try {
        string root = "data", sid = "SC02";
        bool all = false;
        for (int i = 1; i < argc; ++i) {
            string arg = argv[i];
            if (arg == "--all") all = true;
            else if (arg == "--scenario" && i+1 < argc) sid = argv[++i];
            else if (arg == "--data" && i+1 < argc) root = argv[++i];
            else throw runtime_error("Tham so khong hop le: " + arg);
        }
        vector<string> cases = all ? vector<string>{"SC01", "SC02", "SC03", "SC04", "SC05"}
                                   : vector<string>{sid};
        cout << "scenario_id,max_flow,min_cut,bfs_iterations\n";
        for (const auto &id : cases) {
            Network g = read_network(root, id);
            int count = 0;
            long long max_flow = g.solve("SS", "TT", count);
            long long mincut = g.verify(g.get_node("SS"), g.get_node("TT"), max_flow);
            cout << id << ',' << max_flow << ',' << mincut << ',' << count << '\n';
        }
    } catch (const exception &e) {
        cerr << "ERROR: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
