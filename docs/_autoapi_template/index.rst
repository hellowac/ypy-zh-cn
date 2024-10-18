API 参考
=============

此页面包含自动生成的 API 参考文档 [#f1]_ 。

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] 使用 `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_ 创建。