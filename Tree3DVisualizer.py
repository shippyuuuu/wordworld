import json
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def draw_arrow(ax, start, end, width=0.08, length=0.08, color='#ffb300', offset=0.12):
    start = np.array(start)
    end = np.array(end)
    vec = end - start
    vec = vec / np.linalg.norm(vec)
    # 箭头尖端往后退 offset
    tip = end - vec * offset
    # 箭头长度
    arrow_len = length
    # 箭头底部中心
    base = tip - vec * arrow_len
    # 构造垂直向量
    if np.allclose(vec, [0,0,1]):
        ortho = np.array([1,0,0])
    else:
        ortho = np.cross(vec, [0,0,1])
        ortho = ortho / np.linalg.norm(ortho)
    # 箭头底部两个点（等腰三角形）
    p1 = base + ortho * width
    p2 = base - ortho * width
    # 三角面
    verts = [
        [tip, p1, p2]
    ]
    arrow = Poly3DCollection(verts, color=color, alpha=0.9)
    ax.add_collection3d(arrow)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_levels(data):
    levels = {}
    roots = [n for n, v in data.items() if not v['parent']]
    queue = deque([(r, 0) for r in roots])
    while queue:
        node, level = queue.popleft()
        if node in levels:
            continue
        levels[node] = level
        for child in data[node]['children']:
            queue.append((child, level + 1))
    return levels

def assign_positions(data, levels):
    from collections import defaultdict
    max_level = max(levels.values())
    positions = {}
    angle_map = {}

    # 根节点在圆心
    roots = [n for n, v in data.items() if not v['parent']]
    for i, root in enumerate(roots):
        angle = 2 * np.pi * i / len(roots)
        positions[root] = (0, 0, max_level)
        angle_map[root] = angle

    # 按层遍历
    for lvl in range(1, max_level + 1):
        nodes = [n for n, l in levels.items() if l == lvl]
        for node in nodes:
            parent = data[node]['parent'][0] if data[node]['parent'] else None
            if parent is None:
                angle = 0
            else:
                # 父节点的角度
                parent_angle = angle_map[parent]
                siblings = [c for c in data[parent]['children']]
                idx = siblings.index(node)
                # 在父节点角度附近均匀分布
                spread = np.pi / 4  # 控制同层兄弟节点的分散角度
                if len(siblings) > 1:
                    angle = parent_angle - spread/2 + spread * idx / (len(siblings)-1)
                else:
                    angle = parent_angle
            radius = 0.9 * lvl
            x = np.cos(angle) * radius
            y = np.sin(angle) * radius
            z =max_level - lvl
            positions[node] = (x, y, z)
            angle_map[node] = angle
    return positions, max_level

def plot_tree(data, levels, positions, max_level):
    fig = plt.figure(figsize=(8, 6))
    fig.patch.set_facecolor('#23272e')  # 柔和深灰蓝背景
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#23272e')  # 让坐标区背景色和画布一致
    ax.tick_params(colors='#66ff99')
    #ax.set_facecolor('black')
    ax.grid(False)

    # 画xyz轴箭头
    axis_z = max_level + 0.5
    axis_len = 2
    ax.quiver(0, 0, 0, axis_len, 0, 0, color='r', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, axis_len, 0, color='g', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, 0, axis_len, color='b', arrow_length_ratio=0.15)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-1, max_level + 1)
    ax.text(axis_len, 0, 0, 'X', color='r', fontsize=14, weight='bold')
    ax.text(0, axis_len, 0, 'Y', color='g', fontsize=14, weight='bold')
    ax.text(0, 0, axis_len, 'Z', color='b', fontsize=14, weight='bold')
    # 隐藏三维坐标轴的背景面
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)

    for node, (x, y, z) in positions.items():
        ax.scatter(x, y, z, s=300, c='#00eaff', edgecolors='white', linewidths=1, alpha=0.95)
        ax.text(x, y, z, node, fontsize=12, color='white', ha='center', va='center', weight='bold')
    # 画连线和箭头
    for node, (x, y, z) in positions.items():
        ax.scatter(x, y, z, s=300, c='#00eaff', edgecolors='white', linewidths=1, alpha=0.95)
        ax.text(x, y, z, node, fontsize=12, color='white', ha='center', va='center', weight='bold')
    for node, info in data.items():
        x1, y1, z1 = positions[node]
        for child in info['children']:
            x2, y2, z2 = positions[child]
            ax.plot([x1, x2], [y1, y2], [z1, z2], c='#ffb300', linewidth=2, alpha=0.8)
            draw_arrow(ax, (x2, y2, z2), (x1, y1, z1))
    plt.tight_layout()
    ax.view_init(elev=30, azim=45)  # elev为仰角，azim为方位角
    plt.show()

if __name__ == '__main__':
    data = load_json('ParentsAndChildren.json')
    levels = build_levels(data)
    positions, max_level = assign_positions(data,levels)
    plot_tree(data, levels, positions, max_level)