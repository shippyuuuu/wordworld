import tkinter as tk
import json
import subprocess

def on_submit():
    parent = entries[0].get()
    children = [entry.get() for entry in entries[1:]]

    #txt文件存储
    # # 读取已有内容
    # data = {}
    # try:
    #     with open("ParentsAndChildren.txt", "r", encoding="utf-8") as f:
    #         for line in f:
    #             if ':' in line:
    #                 p, c = line.strip().split(':', 1)
    #                 data[p] = ast.literal_eval(c.strip())
    # except FileNotFoundError:
    #     pass
    #
    # # 合并子
    # if parent in data:
    #     for child in children:
    #         if child and child not in data[parent]:
    #             data[parent].append(child)
    # else:
    #     data[parent] = [c for c in children if c]
    #
    # # 写回文件
    # with open("ParentsAndChildren.txt", "w", encoding="utf-8") as f:
    #     for p, c in data.items():
    #         f.write(f"{p}: {c}\n")

    # 读取
    try:
        with open('ParentsAndChildren.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        #保证data总有值

    nodes = {} # 用于存储节点信息

    # 遍历已有数据，构建节点信息
    for node, info in data.items():
        p = info.get("parent")
        if isinstance(p, list):
            parents = p
        elif p is None:
            parents = []
        else:
            parents = [p]
        nodes[node] = {
            "parent": parents,
            "children": info.get("children", [])
        }

    # 更新新输入
    if parent not in nodes:
        nodes[parent] = {"parent": [], "children": []}
    for child in children:
        if child:
            if child not in nodes:
                nodes[child] = {"parent": [], "children": []}
            # 添加父节点到child的parent列表
            if parent not in nodes[child]["parent"]:
                nodes[child]["parent"].append(parent)
            # 添加子节点到parent的children列表
            if child not in nodes[parent]["children"]:
                nodes[parent]["children"].append(child)

    # 写回优化后的结构
    with open('ParentsAndChildren.json', 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    #代码完成后可以注释掉下面的print语句
    for idx, entry in enumerate(entries, 1):
        print(f"输入{idx}：", entry.get())

def run_visualizer():
    subprocess.Popen(['python', 'Tree3DVisualizer.py'])

def main():

    window = tk.Tk()
    window.title("Newlink")
    window.geometry("500x500")

    # 获取屏幕宽高
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算窗口左上角坐标
    x = (screen_width - 500) // 2
    y = (screen_height - 500) // 2
    window.geometry(f"500x500+{x}+{y}")
    #window.iconbitmap('your_icon.ico')

    entry_num = 2  # 只需改这里即可增加/减少输入框数量
    entry_labels = ["父", "子"]  # 标签数量需与entry_num一致

    global entries  # 声明为全局变量以便在on_submit函数中访问
    entries = []
    for i in range(entry_num):
        label = tk.Label(window, text=entry_labels[i], font=("SimHei", 16))
        label.pack()
        entry = tk.Entry(window, width=20, font=("SimHei", 20))
        entry.pack(pady=20)
        entries.append(entry)

    submit_btn = tk.Button(window, text="提交", command=on_submit)
    submit_btn.pack()

    vis_btn = tk.Button(window, text="显示3D树", command=run_visualizer)
    vis_btn.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()