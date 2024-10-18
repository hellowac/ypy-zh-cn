Ypy 文档
================================

Ypy 是一个高性能的 CRDT，允许 Python 开发者轻松地在进程之间同步状态。它建立在 Y-CRDT 之上：一个强大的分布式数据类型库，使用 Rust 编写。借助 Ypy，开发者可以创建健壮的、最终一致的应用程序，实现用户之间的状态共享。所有更改会自动在应用实例之间解决，因此您的代码可以专注于表示状态，而不是同步状态。这个共享状态可以超越 Python 程序，与由 Y-Wasm 支持的 web 应用程序进行接口。这允许前端用户界面与 Python 应用逻辑之间无缝通信。

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   tutorial






索引表
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
