class Grandparent:
    pass

class Parent(Grandparent):
    pass

class Child(Parent):
    pass
def is_indirect_subclass(child, parent):
    return issubclass(child, parent) and parent not in child.__bases__
# This will print True - Child is an indirect subclass of Grandparent
print(is_indirect_subclass(Child, Grandparent))

# This will print False - Child is a direct subclass of Parent
print(is_indirect_subclass(Child, Parent))

# This will print False - Parent is a direct subclass of Grandparent
print(is_indirect_subclass(Parent, Grandparent))