[![PyPI version](https://badge.fury.io/py/y-py.svg)](https://badge.fury.io/py/y-py)

# Ypy

Ypy 是 Y-CRDT 的 Python 绑定。它提供分布式数据类型，使设备之间能够实时协作。Ypy 可以与任何其他具有 Y-CRDT 绑定的平台同步数据，从而实现无缝的跨域通信。该库是 Yrs 的一个轻量级封装，利用了 Rust 的安全性和性能。

> [我们正在寻找维护者 👀](https://github.com/y-crdt/ypy/issues/148)

## 安装

```
pip install y-py
```

## 开始使用

Ypy 提供了许多与 [Yjs](https://docs.yjs.dev/) 相同的共享数据类型。所有对象都在 `YDoc` 内共享，并在事务块内进行修改。

```python
import y_py as Y

d1 = Y.YDoc()
# 在 YDoc 中创建一个新的 YText 对象
text = d1.get_text('test')
# 开始一个事务以更新文本
with d1.begin_transaction() as txn:
    # 添加文本内容
    text.extend(txn, "hello world!")

# 创建另一个文档
d2 = Y.YDoc()
# 与原始文档共享状态
state_vector = Y.encode_state_vector(d2)
diff = Y.encode_state_as_update(d1, state_vector)
Y.apply_update(d2, diff)

value = str(d2.get_text('test'))

assert value == "hello world!"
```

## 开发设置

0. 安装 [Rust](https://www.rust-lang.org/tools/install) 和 [Python](https://www.python.org/downloads/)
1. 安装 `maturin` 以构建 Ypy: `pip install maturin`
2. 创建库的开发版本: `maturin develop`

## 测试

所有测试位于 `/tests`。要运行测试，请安装 `pytest` 并从项目根目录运行命令行工具：

```
pip install pytest
pytest
```

## 使用 Hatch

如果您使用 `hatch`，则在 `pyproject.toml` 中定义了一个 `test` 环境矩阵，将在 `py37` 到 `py312` 的虚拟环境中运行命令。

```
hatch run test:maturin develop
hatch run test:pytest
```

## 构建 Ypy

将库构建为 wheel，并存储在 `target/wheels` 中：

```
maturin build
```

## Ypy 在 WASM (Pyodide) 中

作为一个基于 Rust 的库，Ypy 无法构建“纯 Python” wheel。CI 过程会构建并上传多个 wheel 到 PyPI，但 PyPI 不支持托管 `emscripten` / `wasm32` wheel，这对于在 Pyodide 中导入是必要的（有关更多信息和更新，请参见 https://github.com/pypi/warehouse/issues/10416 ）。目前，Ypy 将构建 `emscripten` wheels，并将二进制文件作为资产附加到相应的 [Releases](https://github.com/y-crdt/ypy/releases) 条目中。不幸的是，直接从 Github 下载链接安装会导致 CORS 错误，因此您需要使用代理来获取二进制文件，并从 emscripten 文件系统进行写入/安装，或者将二进制文件托管在您的应用程序可以访问的 CORS 位置。

您可以使用 [pyodide.org 的终端模拟器](https://pyodide.org/en/stable/console.html) 在 Pyodide 中试用 Ypy：

```
欢迎来到 Pyodide 终端模拟器 🐍
Python 3.10.2 (main, Sep 15 2022 23:28:12) 在 WebAssembly/Emscripten 上
输入 "help", "copyright", "credits" 或 "license" 获取更多信息。
>>> wheel_url = 'https://github.com/y-crdt/ypy/releases/download/v0.5.5/y_py-0.5.5-cp310-cp310-emscripten_3_1_14_wasm32.whl'
>>> wheel_name = wheel_url.split('/')[-1]
>>> wheel_name
'y_py-0.5.5-cp310-cp310-emscripten_3_1_14_wasm32.whl'
>>> 
>>> proxy_url = f'https://api.allorigins.win/raw?url={wheel_url}'
>>> proxy_url
'https://api.allorigins.win/raw?url=https://github.com/y-crdt/ypy/releases/download/v0.5.5/y_py-0.5.5-cp310-cp310-emscripten_3_1_14_wasm32.whl'
>>> 
>>> import pyodide
>>> resp = await pyodide.http.pyfetch(proxy_url)
>>> resp.status
200
>>> 
>>> content = await resp.bytes()
>>> len(content)
360133
>>> content[:50]
b'PK\x03\x04\x14\x00\x00\x00\x08\x00\xae\xb2}U\x92l\xa7E\xe6\x04\x00\x00u\t\x00\x00\x1d\x00\x00\x00y_py-0.5.5.dist-info'
>>>
>>> with open(wheel_name, 'wb') as f:
...   f.write(content)
... 
360133
>>> 
>>> import micropip
>>> await micropip.install(f'emfs:./{wheel_name}')
>>> 
>>> import y_py as Y
>>> Y
<module 'y_py' from '/lib/python3.10/site-packages/y_py/__init__.py'>
>>> 
>>> d1 = Y.YDoc()
>>> text = d1.get_text('test')
>>> with d1.begin_transaction() as txn:
    text.extend(txn, "hello world!")
... 
>>> d2 = Y.YDoc()
>>> state_vector = Y.encode_state_vector(d2)
>>> diff = Y.encode_state_as_update(d1, state_vector)
>>> Y.apply_update(d2, diff)
>>> d2.get_text('test')
YText(hello world!)
```
