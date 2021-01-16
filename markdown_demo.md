# 示例

# 标题

**粗体**

- 缩进
  - 缩进

行内高亮： `markdown`

按键：CTRL

> 多层引用
> > 多层引用

———— 

> 单层引用
> 单层引用

| 表格 | 表格 |
| -    |  -   |
| 表格 | 表格 |


图片： ![图片](https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fgss0.baidu.com%2F-Po3dSag_xI4khGko9WTAnF6hhy%2Fzhidao%2Fpic%2Fitem%2F8718367adab44aedd5018c82be1c8701a18bfb0d.jpg&refer=http%3A%2F%2Fgss0.baidu.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1612859424&t=d9156a8810c87a5339e656e05e9bd8da.jpg)



代码高亮：
```python
def login_required(route_function):
    @wraps(route_function)
    def f(*args, **kwargs):
        u = current_user()
        if u.username == 'guest':
            return redirect(url_for('index.index'))
        else:
            return route_function(*args, **kwargs)

    return f
```