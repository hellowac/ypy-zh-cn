教程
========

每个使用 Ypy 数据的用户都可以通过共享文档实例读取和更新信息。添加到文档中的任何内容都将被跟踪并在所有文档实例之间同步。这些文档可以包含常见的数据类型，包括数字、布尔值、字符串、列表、字典和 XML 树。修改文档状态是在事务内进行的，以确保健壮性和线程安全。使用这些构建块，您可以安全地在用户之间共享数据。以下是一个基本的 hello world 示例：

.. code-block:: python

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