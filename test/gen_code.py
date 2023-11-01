import ast
import astunparse
a ="""
class Test(object):
    a =1
    b =2
"""
# 定义树状结构 
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = [] 

    def add_child(self, child_node):
        self.children.append(child_node)

# 定义 class 模板
# test = ast.parse(a)
# print(ast.dump(test))


class_name = "MyClass"
attributes = {"name": "John", "age": 30}

class_ast = ast.ClassDef(
    name=class_name,
    bases=[ast.Name(id='object', ctx=ast.Load(), lineno=2,col_offset=4)],
    keywords=[],
    body=[
        ast.Assign(
            targets=[ast.Name(id=attr, ctx=ast.Store())],
            value=ast.Constant(value=value),
            lineno=2,
            col_offset=4
            
            )
            
         for attr, value in attributes.items()
    ],
    decorator_list=[],
    type_ignores=[],
    lineno=6,
    col_offset=4
    
)

module_ast = ast.Module(body=[class_ast],lineno=2)
source_code = astunparse.unparse(module_ast)
print(ast.dump(module_ast))
print(source_code)

# compiled_code = compile(module_ast, filename='<ast>', mode='exec')
# namespace = {}
# exec(compiled_code, namespace)

# # 创建类实例
# MyClass = namespace["MyClass"]
# my_instance = MyClass()
# print(my_instance.name)  # 输出: John
# print(my_instance.age)   # 输出: 30