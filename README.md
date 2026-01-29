# OthelloAI

本项目是一个基于 Python 的黑白棋（Othello/Reversi）AI 对战平台，支持人机对战、双AI对战和棋局复盘。项目包含了多种AI算法（如贪心算法、极大极小算法），并提供了基于 Tkinter 的图形用户界面。

## 目录结构

```
ai_greedy.py         # 贪心AI实现
ai_minimax.py        # 极大极小AI实现
board.py             # 棋盘逻辑
player.py            # 玩家与AI接口
ui.py                # 通用UI逻辑
ui_tkinter.py        # Tkinter图形界面
experiment.py        # 实验与对局脚本
evaluate.py          # 棋局评估函数
main.py              # 程序入口
utils.py             # 工具函数
replays/             # 棋局复盘文件夹，保存对局回放（.json）
build/               # 打包相关文件夹
dist/                # 已打包好的可执行程序目录
```

## 主要功能

- 支持人机对战、双AI对战
- 支持AI难度选择（如贪心、极大极小等）
- 棋局复盘与保存，可在 `replays/` 文件夹中查看和加载历史对局
- 图形化界面，操作简便
- 提供已打包的独立应用程序（见 `dist/` 文件夹）

## 环境依赖

- Python 3.7 及以上
- Tkinter（标准库自带）

## 运行方法

### 方式一：源码运行

1. 安装 Python 3.7 及以上版本。
2. 进入项目目录：
   ```powershell
   cd D:\desktop\OthelloAI
   ```
3. 运行主程序：
   ```powershell
   python main.py
   ```

### 方式二：使用已打包应用程序

1. 进入 `dist/` 文件夹。
2. 直接双击运行可执行文件（如 `ui_tkinter.exe`）。

## 文件说明

- `ai_greedy.py`：实现了贪心算法的AI。
- `ai_minimax.py`：实现了极大极小算法的AI。
- `board.py`：棋盘状态与操作逻辑。
- `player.py`：玩家与AI的统一接口。
- `ui.py`：通用UI逻辑。
- `ui_tkinter.py`：基于Tkinter的图形界面。
- `experiment.py`：用于AI对战实验和性能测试。
- `evaluate.py`：棋局评估函数。
- `main.py`：程序入口，负责启动UI。
- `utils.py`：工具函数。
- `replays/`：保存对局复盘文件（.json），可用于回放历史对局。
- `build/`：打包生成的相关文件。
- `dist/`：已打包好的可执行程序，便于直接运行。

## 贡献

由Tony142857独立开发完成

## License

本项目仅供学习交流使用。
