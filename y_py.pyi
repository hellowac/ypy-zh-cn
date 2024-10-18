from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

class SubscriptionId:
    """
    跟踪观察者回调。将其传递给 `unobserve` 方法以取消其相关的回调。
    """

Event = Union[YTextEvent, YArrayEvent, YMapEvent, YXmlTextEvent, YXmlElementEvent]

class YDoc:
    """
    Ypy 文档类型。文档是协作资源管理中最重要的单位。
    所有共享集合都位于其对应文档的范围内。所有更新都是基于每个文档生成的（而不是单个共享类型）。所有对共享集合的操作都通过 :class:`YTransaction` 进行，其生命周期也与文档相关。

    文档管理所谓的根类型(root types)，这些是 顶层共享类型定义(top-level shared types definitions)（与递归嵌套类型相对）。

    Example::

        from y_py import YDoc

        doc = YDoc()
        with doc.begin_transaction() as txn:
            text = txn.get_text('name')
            text.extend(txn, 'hello world')

        print(str(text))
    """

    client_id: int
    def __init__(
        self,
        client_id: Optional[int] = None,
        offset_kind: str = "utf8",
        skip_gc: bool = False,
    ):
        """
        创建一个新的 Ypy 文档。如果传递了 `client_id` 参数，则将其用作该文档的全局唯一标识符（由调用者确保该要求）。
        否则，将分配一个随机生成的数字。
        """
    def begin_transaction(self) -> YTransaction:
        """

        Returns:
            此文档的新事务。Ypy 共享数据类型在给定事务的上下文中执行其操作。
            每个文档一次只能有一个活动事务 - 后续尝试将导致异常被抛出。

        使用 :meth:`~YDoc.begin_transaction` 开始的事务可以通过删除事务对象来释放。

        Example::

            from y_py import YDoc
            doc = YDoc()
            text = doc.get_text('name')
            with doc.begin_transaction() as txn:
                text.insert(txn, 0, 'hello world')

        """
    def transact(self, callback: Callable[[YTransaction]]): ...
    def get_map(self, name: str) -> YMap:
        """
        Returns:
            一个 :class:`YMap` 共享数据类型，可以使用给定的 :arg:`name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。

        如果之前存在该名称的实例，但它是不同的类型，将投影到 `YMap` 实例上。
        """
    def get_xml_element(self, name: str) -> YXmlElement:
        """
        Returns:
            一个 :class:`YXmlElement` 共享数据类型，可以使用给定的 `name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。

        如果之前存在该名称的实例，但它是不同的类型，将投影到 :class:`YXmlElement` 实例上。
        """
    def get_xml_text(self, name: str) -> YXmlText:
        """
        Returns:
            一个 :class:`YXmlText` 共享数据类型，可以使用给定的 `name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。

        如果之前存在该名称的实例，但它是不同的类型，将投影到 :class:`YXmlText` 实例上。
        """
    def get_xml_fragment(self, name: str) -> YXmlFragment:
        """
        Returns:
            一个 :class:`YXmlFragment` 共享数据类型，可以使用给定的 `name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。

        如果之前存在该名称的实例，但它是不同的类型，将投影到 :class:`YXmlFragment` 实例上。
        """
    def get_array(self, name: str) -> YArray:
        """
        Args:
            一个 :class:`YArray` 共享数据类型，可以使用给定的 `name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。

        如果之前存在该名称的实例，但它是不同的类型，将投影到 :class:`YArray` 实例上。
        """
    def get_text(self, name: str) -> YText:
        """

        Args:
            name: 用于检索文本的标识符
        Returns:
            一个 :class:`YText` 共享数据类型，可以使用给定的 `name` 进行后续访问。

        如果之前没有该名称的实例，将创建并返回它。
        如果之前存在该名称的实例，但它是不同的类型，将投影到 :class:`YText` 实例上。
        """
    def observe_after_transaction(
        self, callback: Callable[[AfterTransactionEvent]]
    ) -> SubscriptionId:
        """
        订阅回调函数以接收 :class:`YDoc` 的更新。当文档事务被提交时，回调将接收编码的状态更新和删除。

        参数:
            callback: 接收事务影响的 :py:class:`~y_py.YDoc` 状态信息的函数。

        Returns:
            一个可以用于取消回调的订阅标识符。
        """

EncodedStateVector = bytes
EncodedDeleteSet = bytes
YDocUpdate = bytes

class AfterTransactionEvent:
    """
    保存事务更新信息，来自状态向量压缩后的提交。
    """

    before_state: EncodedStateVector
    """
    事务之前的 :class:`YDoc` 编码状态。
    """
    after_state: EncodedStateVector
    """
    事务之后的 :class:`YDoc` 编码状态。
    """
    delete_set: EncodedDeleteSet
    """
    由相关事务删除的元素。
    """

    def get_update(self) -> YDocUpdate:
        """
        Returns:
            由事务产生的所有更新的编码有效负载。
        """

def encode_state_vector(doc: YDoc) -> EncodedStateVector:
    """
    将给定 Ypy 文档的状态向量编码为其二进制表示，使用 lib0 v1 编码。状态向量是对在给定文档上执行的更新的紧凑表示，可以在远程对等体上使用 :meth:`encode_state_as_update` 生成增量更新有效负载，以同步对等体之间的更改。

    示例::

        from y_py import YDoc, encode_state_vector, encode_state_as_update, apply_update from y_py

        # 机器 A 上的文档
        local_doc = YDoc()
        local_sv = encode_state_vector(local_doc)

        # 机器 B 上的文档
        remote_doc = YDoc()
        remote_delta = encode_state_as_update(remote_doc, local_sv)

        apply_update(local_doc, remote_delta)

    """

def encode_state_as_update(
    doc: YDoc, vector: Optional[Union[EncodedStateVector, List[int]]] = None
) -> YDocUpdate:
    """
    将自给定版本 `vector` 以来发生的所有更新编码为紧凑的增量表示，使用 lib0 v1 编码。
    如果未提供 `vector` 参数，则生成的增量有效负载将包含当前 Ypy 文档的所有更改，
    有效地作为其状态快照。

    示例::

        from y_py import YDoc, encode_state_vector, encode_state_as_update, apply_update

        # 机器 A 上的文档
        local_doc = YDoc()
        local_sv = encode_state_vector(local_doc)

        # 机器 B 上的文档
        remote_doc = YDoc()
        remote_delta = encode_state_as_update(remote_doc, local_sv)

        apply_update(local_doc, remote_delta)
    """

def apply_update(doc: YDoc, diff: Union[YDocUpdate, List[int]]):
    """
    将由远程文档副本生成的增量更新应用于当前文档。此方法假定有效负载保持 lib0 v1 编码格式。

    示例::

        from y_py import YDoc, encode_state_vector, encode_state_as_update, apply_update

        # 机器 A 上的文档
        local_doc = YDoc()
        local_sv = encode_state_vector(local_doc)

        # 机器 B 上的文档
        remote_doc = YDoc()
        remote_delta = encode_state_as_update(remote_doc, local_sv)

        apply_update(local_doc, remote_delta)
    """

class YTransaction:
    """
    作为文档块存储的代理的事务。Ypy 共享数据类型在给定事务的上下文中执行其操作。
    每个文档一次只能有一个活动事务——后续尝试将导致异常被抛出。

    使用 :meth:`~YDoc.begin_transaction` 启动的事务可以通过删除事务对象来释放。

    示例::

        from y_py import YDoc
        doc = YDoc()
        text = doc.get_text('name')
        with doc.begin_transaction() as txn:
            text.insert(txn, 0, 'hello world')
    """

    before_state: Dict[int, int]

    def get_text(self, name: str) -> YText:
        """
        Returns:
            一个可使用给定 `name` 进行后续访问的 :class:`YText` 共享数据类型。

        如果之前没有该名称的实例，则会创建并返回它。

        如果该名称已有实例，但其类型不同，则会将其投影到 :class:`YText` 实例上。
        """

    def get_array(self, name: str) -> YArray:
        """
        Returns:
            一个可使用给定 `name` 进行后续访问的 :class:`YArray` 共享数据类型。

        如果之前没有该名称的实例，则会创建并返回它。

        如果该名称已有实例，但其类型不同，则会将其投影到 :class:`YArray` 实例上。
        """

    def get_map(self, name: str) -> YMap:
        """
        Returns:
            一个可使用给定 `name` 进行后续访问的 :class:`YMap` 共享数据类型。

        如果之前没有该名称的实例，则会创建并返回它。

        如果该名称已有实例，但其类型不同，则会将其投影到 :class:`YMap` 实例上。
        """

    def commit(self):
        """
        在不释放事务的情况下触发一系列更新后操作。这包括内部更新表示的压缩和优化，触发事件等。
        Ypy 事务在被 `free` 时自动提交。
        """

    def state_vector_v1(self) -> EncodedStateVector:
        """
        将给定事务文档的状态向量编码为其二进制表示，使用 lib0 v1 编码。
        状态向量是对在给定文档上执行的更新的紧凑表示，可以在远程对等体上使用 :meth:`encode_state_as_update` 生成增量更新有效负载，以同步对等体之间的更改。

        示例::

            from y_py import YDoc

            # 机器 A 上的文档
            local_doc = YDoc()
            local_txn = local_doc.begin_transaction()

            # 机器 B 上的文档
            remote_doc = YDoc()
            remote_txn = local_doc.begin_transaction()

            try:
                local_sv = local_txn.state_vector_v1()
                remote_delta = remote_txn.diff_v1(local_sv)
                local_txn.apply_v1(remote_delta)
            finally:
                del local_txn
                del remote_txn

        """

    def diff_v1(self, vector: Optional[EncodedStateVector] = None) -> YDocUpdate:
        """
        将自给定版本 `vector` 以来发生的所有更新编码为紧凑的增量表示，使用 lib0 v1 编码。
        如果未提供 `vector` 参数，则生成的增量有效负载将包含当前 Ypy 文档的所有更改，有效地作为其状态快照。

        示例::

            from y_py import YDoc

            # 机器 A 上的文档
            local_doc = YDoc()
            local_txn = local_doc.begin_transaction()

            # 机器 B 上的文档
            remote_doc = YDoc()
            remote_txn = local_doc.begin_transaction()

            try:
                local_sv = local_txn.state_vector_v1()
                remote_delta = remote_txn.diff_v1(local_sv)
                local_txn.apply_v1(remote_delta)
            finally:
                del local_txn
                del remote_txn
        """

    def apply_v1(self, diff: YDocUpdate):
        """
        将由远程文档副本生成的增量更新应用于当前事务的文档。此方法假定有效负载保持 lib0 v1 编码格式。

        示例::

            from y_py import YDoc

            # 机器 A 上的文档
            local_doc = YDoc()
            local_txn = local_doc.begin_transaction()

            # 机器 B 上的文档
            remote_doc = YDoc()
            remote_txn = local_doc.begin_transaction()

            try:
                local_sv = local_txn.state_vector_v1()
                remote_delta = remote_txn.diff_v1(local_sv)
                local_txn.apply_v1(remote_delta)
            finally:
                del local_txn
                del remote_txn
        """
    def __enter__(self) -> YTransaction: ...
    def __exit__(self) -> bool: ...

class YText:
    """
    用于协作文本编辑的共享数据类型。它使多个用户能够高效地添加和删除文本块。
    此类型在内部表示为能够双向链接的文本块列表——在 :meth:`YTransaction.commit` 期间会进行优化，
    允许将多个连续插入的字符压缩为单个文本块，即使在事务边界之间，以保持更高效的内存模型。

    :class:`YText` 结构在内部使用 UTF-8 编码，其长度以字节数而非单个字符表示（单个 UTF-8 码点可以由多个字节组成）。

    与所有 Yrs 共享数据类型一样， :class:`YText` 对交错问题具有抗性（即一个字符后接另一个字符的插入可能与其他对等体的并发插入交错，合并所有更新后）。在 Yrs 中，冲突解决通过使用唯一文档 ID 来确定正确和一致的顺序。
    """

    prelim: bool
    """如果该元素尚未集成到 YDoc 中，则为 True 。"""

    def __init__(self, init: str = ""):
        """
        创建一个新的 `YText` 共享数据类型的初步实例，其状态初始化为提供的参数。

        初步实例可以嵌套到其他共享数据类型中，如 :class:`YArray` 和 :class:`YMap`。
        一旦以这种方式插入，便会集成到 Ypy 文档存储中，无法再次嵌套：尝试这样做将导致异常。
        """

    def __str__(self) -> str:
        """
        Returns:
            存储在此数据类型中的底层共享字符串。
        """

    def __repr__(self) -> str:
        """
        Returns:
            用 :class:`YText` 包装的字符串表示。
        """

    def __len__(self) -> int:
        """
        Returns:
            存储在此 :class:`YText` 实例中的底层字符串的长度，理解为 UTF-8 编码字节的数量。
        """

    def to_json(self) -> str:
        """
        Returns:
            存储在此数据类型中的底层共享字符串。
        """

    def insert(
        self,
        txn: YTransaction,
        index: int,
        chunk: str,
        attributes: Dict[str, Any] = {},
    ):
        """
        在给定的 `index` 开始位置将一段文本插入到 :class:`YText` 实例中。
        属性是可选的样式修饰符（`{"bold": True}`），可以附加到插入的字符串。
        属性仅支持已集成到文档存储中的 `YText` 实例。
        """

    def insert_embed(
        self,
        txn: YTransaction,
        index: int,
        embed: Any,
        attributes: Dict[str, Any] = {},
    ):
        """
        在提供的索引位置插入嵌入内容到 :class:`YText` 中。属性是与嵌入内容相关的用户定义元数据。
        属性仅支持已集成到文档存储中的 :class:`YText` 实例。
        """

    def format(
        self, txn: YTransaction, index: int, length: int, attributes: Dict[str, Any]
    ):
        """
        用包含提供的 `attributes` 元数据的格式块包装现有文本片段，该片段由 `index`-`length` 参数描述。
        此方法仅对已集成到文档存储中的 :class:`YText` 实例有效。
        """

    def extend(self, txn: YTransaction, chunk: str):
        """
        在当前 :class:`YText` 实例的末尾附加给定的 `chunk` 文本。
        """

    def delete(self, txn: YTransaction, index: int):
        """
        删除指定 `index` 处的字符。
        """

    def delete_range(self, txn: YTransaction, index: int, length: int):
        """
        删除从给定 `index` 开始的指定范围内的字符。
        `index` 和 `length` 的计数以 UTF-8 字节数为单位。
        """

    def observe(self, f: Callable[[YTextEvent]]) -> SubscriptionId:
        """
        将回调函数分配给监听 :class:`YText` 更新。

        Args:
            f: 当文本对象收到更新时运行的回调函数。
        Returns:
            对回调订阅的引用。
        """

    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        将回调函数分配给监听 :class:`YText` 实例及其嵌套属性的更新。
        目前，这将监听与 :meth:`YText.observe` 相同的事件，但将来也将监听嵌入值的事件。

        Args:
            f: 当文本对象或其嵌套属性收到更新时运行的回调函数。
        Returns:
            对回调订阅的引用。
        """

    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 关联的观察者回调。

        Args:
            subscription_id: :meth:`~YText.observe` 方法提供的订阅引用。
        """

class YTextEvent:
    """
    传达在 :class:`YText` 实例的事务期间发生的更新。
    :attr:`~YTextEvent.target` 引用接收更新的 :class:`YText` 元素。
    :attr:`~YTextEvent.delta` 是事务应用的更新列表。
    """

    target: YText
    delta: List[YTextDelta]

    def path(self) -> List[Union[int, str]]:
        """
        Returns:
            从根类型到当前共享类型实例的路径数组（可通过 :attr:`~YTextEvent.target` 获取器访问）。
        """

YTextDelta = Union[YTextChangeInsert, YTextChangeDelete, YTextChangeRetain]

class YTextChangeInsert(TypedDict):
    insert: str
    attributes: Optional[Any]

class YTextChangeDelete(TypedDict):
    delete: int

class YTextChangeRetain(TypedDict):
    retain: int
    attributes: Optional[Any]

class YArray:
    prelim: bool
    """如果该元素尚未集成到 :class:`YDoc` 中，则为 True。"""

    def __init__(self, init: Optional[Iterable[Any]] = None):
        """
        创建一个新的 :class:`YArray` 共享数据类型的初步实例，其状态初始化为提供的参数。

        初步实例可以嵌套到其他共享数据类型中，如 :class:`YArray` 和 :class:`YMap`。
        一旦初步实例以这种方式插入，它将集成到 Ypy 文档存储中，无法再次嵌套：尝试这样做将导致异常。
        """
    def __len__(self) -> int:
        """
        Returns:
            :class:`YArray` 中元素的数量。
        """
    def __str__(self) -> str:
        """
        Returns:
            :class:`YArray` 的字符串表示。
        """
    def __repr__(self) -> str:
        """
        Returns:
            包裹在 :class:`YArray` 中的 `YArray` 的字符串表示。
        """
    def to_json(self) -> str:
        """
        将此 :class:`YArray` 实例的底层内容转换为其 JSON 表示。
        """
    def insert(self, txn: YTransaction, index: int, item: Any):
        """
        在 :class:`YArray` 中的指定索引处插入一个项。
        """
    def insert_range(self, txn: YTransaction, index: int, items: Iterable):
        """
        在给定的 `index` 处将指定范围的 `items` 插入到此 :class:`YArray` 实例中。
        """
    def append(self, txn: YTransaction, item: Any):
        """
        将单个项添加到 :class:`YArray` 的末尾。
        """
    def extend(self, txn: YTransaction, items: Iterable):
        """
        将一系列 `items` 附加到此 :class:`YArray` 实例的末尾。
        """
    def delete(self, txn: YTransaction, index: int):
        """
        从数组中删除单个项。

        Args:
            txn: 正在修改数组的事务。
            index: 要删除的元素的索引。
        """
    def delete_range(self, txn: YTransaction, index: int, length: int):
        """
        从当前 :class:`YArray` 实例中删除给定 `length` 的项范围，从给定的 `index` 开始。
        """
    def move_to(self, txn: YTransaction, source: int, target: int):
        """
        将在 `source` 索引处找到的单个项移动到 `target` 索引位置。

        Args:
            txn: 正在修改数组的事务。
            source: 要移动的元素的索引。
            target: 元素的新位置。
        """
    def move_range_to(self, txn: YTransaction, start: int, end: int, target: int):
        """
        将 `start`..`end` 索引范围内的所有元素（两端均包含）移动到 `target` 索引指向的新位置。
        同时插入的其他对等体在移动范围内的元素也将被移动，经过同步后（尽管可能需要多次同步往返才能实现收敛）。

        Args:
            txn: 正在修改数组的事务。
            start: 范围第一个元素的索引（包含）。
            end: 范围最后一个元素的索引（包含）。
            target: 元素的新位置。

        示例::

            import y_py as Y
            doc = Y.Doc()
            array = doc.get_array('array')

            with doc.begin_transaction() as t:
                array.insert_range(t, 0, [1,2,3,4])

            # 将元素 2 和 3 移动到 4 之后
            with doc.begin_transaction() as t:
                array.move_range_to(t, 1, 2, 4)
        """
    def __getitem__(self, index: Union[int, slice]) -> Any:
        """
        Returns:
            存储在给定 `index` 下的元素或从切片范围生成的新元素列表。
        """
    def __iter__(self) -> Iterator:
        """
        Returns:
            可用于遍历此 :class:`YArray` 实例中存储的值的迭代器。

        示例::

            from y_py import YDoc

            # 在机器 A 上的文档
            doc = YDoc()
            array = doc.get_array('name')

            for item in array:
                print(item)
        """
    def observe(self, f: Callable[[YArrayEvent]]) -> SubscriptionId:
        """
        分配一个回调函数以监听 :class:`YArray` 更新。

        Args:
            f: 在数组对象接收到更新时运行的回调函数。
        Returns:
            与回调订阅相关联的标识符。
        """
    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        分配一个回调函数以监听 :class:`YArray` 及其子元素的聚合更新。

        Args:
            f: 在数组对象或组件接收到更新时运行的回调函数。
        Returns:
            与回调订阅相关联的标识符。
        """
    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 相关联的观察者回调。

        Args:
            subscription_id: 由 :meth:`~YArray.observe` 方法提供的订阅引用。
        """

YArrayObserver = Any

class YArrayEvent:
    """
    传达在 :class:`YArray` 实例的事务期间发生的更新。
    `target`: 引用接收更新的 :class:`YArray` 元素。
    `delta`: 是事务应用的更新列表。
    """

    target: YArray
    delta: List[ArrayDelta]
    def path(self) -> List[Union[int, str]]:
        """
        返回:
            从根类型到当前共享类型实例的键和索引数组（通过 :attr:`~YArrayEvent.target` 获取）。
        """

ArrayDelta = Union[ArrayChangeInsert, ArrayChangeDelete, ArrayChangeRetain]
"""在事务期间对 :class:`YArray` 的修改。"""

class ArrayChangeInsert(TypedDict):
    """更新消息，表示元素已插入到 :class:`YArray` 中。"""

    insert: List[Any]

class ArrayChangeDelete:
    """更新消息，表示元素已从 :class:`YArray` 中删除。"""

    delete: int

class ArrayChangeRetain:
    """更新消息，表示元素在 :class:`YArray` 中未修改。"""

    retain: int

class YMap:
    prelim: bool
    """如果此元素尚未集成到 :class:`YDoc` 中，则为 True。"""

    def __init__(self, dict: dict):
        """
        创建一个新的 `YMap` 共享数据类型的初步实例，其状态初始化为提供的参数。

        初步实例可以嵌套到其他共享数据类型中，如 :class:`YArray` 和 :class:`YMap`。
        一旦以这种方式插入初步实例，它将集成到 Ypy 文档存储中，无法再次嵌套：尝试这样做将导致异常。
        """

    def __len__(self) -> int:
        """
        Returns:
            此 :class:`YMap` 实例中存储的条目数量。
        """

    def __str__(self) -> str:
        """
        Returns:
            :class:`YMap` 的字符串表示。
        """

    def __dict__(self) -> dict:
        """
        Returns:
            :class:`YMap` 的内容作为 Python 字典。
        """

    def __repr__(self) -> str:
        """
        Returns:
            :class:`YMap` 的字符串表示，包裹在 'YMap()' 中。
        """

    def to_json(self) -> str:
        """
        将此 :class:`YMap` 实例的内容转换为 JSON 表示。
        """

    def set(self, txn: YTransaction, key: str, value: Any):
        """
        在此 :class:`YMap` 实例中设置给定的 `key`-`value` 条目。如果已经存在给定 `key` 的条目，
        则将其覆盖为新的 `value`。
        """

    def update(
        self, txn: YTransaction, items: Union[Iterable[Tuple[str, Any]], Dict[str, Any]]
    ):
        """
        使用项目的内容更新 :class:`YMap`。

        Args:
            txn: 执行插入更新的事务。
            items: 生成要插入到 :class:`YMap` 中的键值元组的可迭代对象。
        """

    def pop(self, txn: YTransaction, key: str, fallback: Optional[Any] = None) -> Any:
        """
        从此 :class:`YMap` 实例中移除由给定 `key` 标识的条目（如果存在）。
        如果该键不存在且未提供后备值，则抛出 KeyError。

        Args:
            txn: 当前 :class:`YDoc` 的事务。
            key: 请求项目的标识符。
            fallback: 如果 :class:`YMap` 中不存在该键，则返回该值。

        Returns:
            键对应的项目。
        """

    def get(self, key: str, fallback: Any) -> Any | None:
        """
        Args:
            key: 请求数据的标识符。
            fallback: 如果该键不存在于映射中，则返回该后备值。

        Returns:
            请求的数据或提供的后备值。
        """

    def __getitem__(self, key: str) -> Any:
        """
        Args:
            key: 请求数据的标识符。

        Returns:
            存储在此 :class:`YMap` 实例中给定 `key` 下的条目的值。如果提供的键未分配，将抛出 :py:exc:`KeyError`。
        """

    def __iter__(self) -> Iterator[str]:
        """
        Returns:
            遍历 :class:`YMap` 所有键的迭代器，顺序不确定。
        """

    def items(self) -> YMapItemsView:
        """
        Returns:
            一个视图，可用于迭代此 :class:`YMap` 实例中存储的所有条目。条目的顺序未指定。

        示例::

            from y_py import YDoc

            # 机器 A 上的文档
            doc = YDoc()
            map = doc.get_map('name')
            with doc.begin_transaction() as txn:
                map.set(txn, 'key1', 'value1')
                map.set(txn, 'key2', True)
            for (key, value) in map.items():
                print(key, value)
        """

    def keys(self) -> YMapKeysView:
        """
        Returns:
            :class:`YMap` 中所有键标识符的视图。键的顺序不稳定。
        """

    def values(self) -> YMapValuesView:
        """
        Returns:
            :class:`YMap` 中所有值的视图。值的顺序不稳定。
        """

    def observe(self, f: Callable[[YMapEvent]]) -> SubscriptionId:
        """
        分配一个回调函数，以监听 :class:`YMap` 更新。

        Args:
            f: 当映射对象接收更新时运行的回调函数。
        Returns:
            与回调订阅相关的引用。删除此观察者以擦除关联的回调函数。
        """

    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        分配一个回调函数，以监听 :class:`YMap` 和子元素的更新。

        Args:
            f: 当映射对象或其任何跟踪元素接收更新时运行的回调函数。
        Returns:
            与回调订阅相关的引用。删除此观察者以擦除关联的回调函数。
        """

    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 相关的观察者回调。

        Args:
            subscription_id: 由 :meth:`~YMap.observe` 方法提供的订阅引用。
        """

class YMapItemsView:
    """跟踪 :class:`YMap` 内的键/值。类似于 Python 字典的 dict_items 功能。"""

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """生成视图内元素的键值元组。"""

    def __contains__(self, item: Tuple[str, Any]) -> bool:
        """检查键值元组是否在视图中。"""

    def __len__(self) -> int:
        """检查视图中的项目数量。"""

class YMapKeysView:
    """跟踪 :class:`YMap` 内的键标识符。"""

    def __iter__(self) -> Iterator[str]:
        """生成视图的键。"""

    def __contains__(self, key: str) -> bool:
        """检查键是否在视图中。"""

    def __len__(self) -> int:
        """检查视图中的键数量。"""

class YMapValuesView:
    """跟踪 :class:`YMap` 内的值。"""

    def __iter__(self) -> Iterator[Any]:
        """生成视图的值。"""

    def __contains__(self, value: Any) -> bool:
        """检查值是否在视图中。"""

    def __len__(self) -> int:
        """检查视图中的值数量。"""

class YMapEvent:
    """
    通信在 :class:`YMap` 实例的事务期间发生的更新。
    `target` 引用接收更新的 `YMap` 元素。
    `delta` 是事务应用的更新列表。
    `keys` 是特定键的更改值列表。
    """

    target: YMap
    """在此事件中修改的元素。"""

    keys: Dict[str, YMapEventKeyChange]
    """按键对 :class:`YMap` 的修改列表。
    包括修改类型以及修改前后的状态。"""

    def path(self) -> List[Union[int, str]]:
        """
        Returns:
            如果此 :class:`YMap` 嵌套在另一个数据结构中，则从根到此元素的路径。
        """

class YMapEventKeyChange(TypedDict):
    action: Literal["add", "update", "delete"]
    oldValue: Optional[Any]
    newValue: Optional[Any]

YXmlAttributes = Iterator[Tuple[str, str]]
"""生成 XML 元素的键/值属性序列。"""

Xml = Union[YXmlElement, YXmlText]
YXmlTreeWalker = Iterator[Xml]
"""访问 XML 树中的元素。"""
EntryChange = Dict[Literal["action", "newValue", "oldValue"], Any]

class YXmlElementEvent:
    target: YXmlElement
    keys: Dict[str, EntryChange]
    delta: List[Dict]

    def path(self) -> List[Union[int, str]]:
        """
        返回当前共享类型实例，当前事件更改所指。
        """

class YXmlElement:
    """
    XML 元素数据类型。它表示一个 XML 节点，可以包含键值属性（解释为字符串），
    以及其他嵌套的 XML 元素或富文本（由 `YXmlText` 类型表示）。

    在冲突解决方面，:class:`YXmlElement` 使用以下规则：

    - 属性更新使用逻辑的最后写入优先原则，意味着过去的更新会被新的更新
      自动覆盖并丢弃，而不同节点的并发更新将通过文档 ID 的优先级来建立
      顺序，解析为单个值。
    - 子节点插入使用其他 Yrs 集合的序列化规则——元素通过抗交错算法插入，
      在相同索引的并发插入顺序通过节点的文档 ID 优先级来建立。
    """

    name: str
    first_child: Optional[Xml]
    next_sibling: Optional[Xml]
    prev_sibling: Optional[Xml]
    parent: Optional[YXmlElement]

    def __len__(self) -> int:
        """
        返回此 :class:`YXmlElement` 实例中存储的子 XML 节点数量。
        """

    def insert_xml_element(
        self,
        txn: YTransaction,
        index: int,
        name: str,
    ) -> YXmlElement:
        """
        将一个新的 :class:`YXmlElement` 实例作为此 XML 节点的子节点插入并返回它。
        """

    def insert_xml_text(self, txn: YTransaction, index: int) -> YXmlText:
        """
        将一个新的 :class:`YXmlText` 实例作为此 XML 节点的子节点插入并返回它。
        """

    def delete(self, txn: YTransaction, index: int, length: int):
        """
        从此 :class:`YXmlElement` 实例中移除一范围的子 XML 节点，
        从给定的 `index` 开始。
        """

    def push_xml_element(self, txn: YTransaction, name: str) -> YXmlElement:
        """
        将一个新的 :class:`YXmlElement` 实例附加为此 XML 节点的最后一个子节点并返回它。
        """

    def push_xml_text(self, txn: YTransaction) -> YXmlText:
        """
        将一个新的 :class:`YXmlText` 实例附加为此 XML 节点的最后一个子节点并返回它。
        """

    def __str__(self) -> str:
        """
        Returns:
            此 XML 节点的字符串表示。
        """

    def __repr__(self) -> str:
        """
        Returns:
            用 :class:`YXmlElement` 包裹的字符串表示。
        """

    def set_attribute(self, txn: YTransaction, name: str, value: str):
        """
        将 `name` 和 `value` 设置为此 XML 节点的新属性。
        如果节点上已存在同名的属性，其值将被提供的值覆盖。
        """

    def get_attribute(self, name: str) -> Optional[str]:
        """
        Returns:
            返回给定 `name` 的属性值。如果没有该名称的属性，将返回 ``null`` 。
        """

    def remove_attribute(self, txn: YTransaction, name: str):
        """
        根据其 `name` 从此 XML 节点移除一个属性。
        """

    def attributes(self) -> YXmlAttributes:
        """
        Returns:
            返回一个迭代器，使其能够以未指定的顺序遍历此 XML 节点的所有属性。
        """

    def tree_walker(self) -> YXmlTreeWalker:
        """
        Returns:
            返回一个迭代器，使其能够对该 XML 节点进行深度遍历——
            从第一个子节点开始，使用深度优先策略遍历此 XML 节点的后续节点。
        """

    def observe(self, f: Callable[[YXmlElementEvent]]) -> SubscriptionId:
        """
        订阅对此 :class:`YXmlElement` 实例发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        Args:
            f: 接收更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        订阅对此 `YXmlElement` 实例及其子节点发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        Args:
            f: 接收 XML 元素及其子元素更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 相关的观察者回调。

        Args:
            subscription_id: :meth:`~YXmlElement:observe` 方法提供的订阅引用。
        """

class YXmlFragment:
    """
    XML 片段数据类型。它表示一组 XML 节点。
    """

    first_child: Optional[Xml]
    parent: Optional[YXmlElement]

    def __len__(self) -> int:
        """
        返回此 :class:`YXmlFragment` 实例中存储的子 XML 节点数量。
        """

    def insert_xml_element(
        self,
        txn: YTransaction,
        index: int,
        name: str,
    ) -> YXmlElement:
        """
        将一个新的 :class:`YXmlElement` 实例作为此 XML 片段的子节点插入并返回它。
        """

    def insert_xml_text(self, txn: YTransaction, index: int) -> YXmlText:
        """
        将一个新的 :class:`YXmlText` 实例作为此 XML 片段的子节点插入并返回它。
        """

    def delete(self, txn: YTransaction, index: int, length: int):
        """
        从此 :class:`YXmlFragment` 实例中移除一范围的子 XML 节点，
        从给定的 `index` 开始。
        """

    def push_xml_element(self, txn: YTransaction, name: str) -> YXmlElement:
        """
        将一个新的 :class:`YXmlElement` 实例附加为此 XML 片段的最后一个子节点并返回它。
        """

    def push_xml_text(self, txn: YTransaction) -> YXmlText:
        """
        将一个新的 :class:`YXmlText` 实例附加为此 XML 片段的最后一个子节点并返回它。
        """

    def __str__(self) -> str:
        """
        Returns:
            此 XML 片段的字符串表示。
        """

    def __repr__(self) -> str:
        """
        Returns:
            此 :class:`YXmlFragment` 的字符串表示。
        """

    def get(self, index: int) -> Union[YXmlText, YXmlElement]:
        """
        返回指定索引处的子节点。
        """

    def tree_walker(self) -> YXmlTreeWalker:
        """
        返回一个迭代器，使其能够对该 XML 片段进行深度遍历——
        从第一个子节点开始，使用深度优先策略遍历此 XML 片段的后续节点。
        """

    def observe(self, f: Callable[[YXmlElementEvent]]) -> SubscriptionId:
        """
        订阅对此 :class:`YXmlFragment` 实例发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        Args:
            f: 接收更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        订阅对此 :class:`YXmlFragment` 实例及其子节点发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        Args:
            f: 接收 XML 片段及其子元素更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 相关的观察者回调。

        Args:
            subscription_id: :meth:`~YXmlFragment.observe` 方法提供的订阅引用。
        """

class YXmlText:
    next_sibling: Optional[Xml]
    prev_sibling: Optional[Xml]
    parent: Optional[YXmlElement]

    def __len__(self):
        """
        Returns:
            此 :class:`YXmlText` 实例中存储的底层字符串的长度，以 UTF-8 编码字节数表示。
        """

    def insert(self, txn: YTransaction, index: int, chunk: str):
        """
        将给定的 `chunk` 文本插入到此 :class:`YXmlText` 实例中，从给定的 `index` 开始。
        """

    def push(self, txn: YTransaction, chunk: str):
        """
        将给定的 `chunk` 文本附加到 :class:`YXmlText` 实例的末尾。
        """

    def delete(self, txn: YTransaction, index: int, length: int):
        """
        删除从给定 `index` 开始的指定范围的字符。
        `index` 和 `length` 都以 UTF-8 字符字节数为单位进行计数。
        """

    def __str__(self) -> str:
        """
        Returns:
            此 :class:`YXmlText` 实例中存储的底层字符串。
        """

    def __repr__(self) -> str:
        """
        Returns:
            用 'YXmlText()' 包裹的字符串表示。
        """

    def set_attribute(self, txn: YTransaction, name: str, value: str):
        """
        将 `name` 和 `value` 作为此 XML 节点的新属性设置。如果该节点上已经存在相同
        `name` 的属性，则其值将被提供的值覆盖。
        """

    def get_attribute(self, name: str) -> Optional[str]:
        """
        Returns:
            给定 `name` 的属性值。如果不存在该名称的属性，
            将返回 `None`。
        """

    def remove_attribute(self, txn: YTransaction, name: str):
        """
        从此 XML 节点中移除给定 `name` 的属性。
        """

    def attributes(self) -> YXmlAttributes:
        """
        Returns:
            一个迭代器，使其能够以不指定顺序遍历此 XML 节点的所有属性。
        """

    def observe(self, f: Callable[[YXmlTextEvent]]) -> SubscriptionId:
        """
        订阅对此 :class:`YXmlText` 实例发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        参数:
            f: 接收更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def observe_deep(self, f: Callable[[List[Event]]]) -> SubscriptionId:
        """
        订阅对此 `YXmlText` 实例及其子元素发生的所有操作。所有更改被
        批处理，并在事务提交阶段最终触发。

        参数:
            f: 接收此元素及其后代更新事件的回调函数。
        Returns:
            可用于取消观察者回调的 :class:`SubscriptionId`。
        """

    def unobserve(self, subscription_id: SubscriptionId):
        """
        取消与 `subscription_id` 相关的观察者回调。

        Args:
            subscription_id: :meth:`~YXmlText.observe` 方法提供的订阅引用。
        """

class YXmlTextEvent:
    target: YXmlText
    keys: List[EntryChange]
    delta: List[YTextDelta]

    def path(self) -> List[Union[int, str]]:
        """
        返回当前事件更改所指的当前共享类型实例。
        """
