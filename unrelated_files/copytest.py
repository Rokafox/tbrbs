import copy


class Dog:
    def __init__(self, name, age, items=None):
        self.name = name
        self.age = age
        self.items = items
    def bark(self):
        print(f'{self.name} is barking')
    def aging(self):
        self.age += 1
    def add_orange(self):
        self.items.append('orange')


doge = Dog('doge', 5, ['banana', 'apple'])
cate = copy.copy(doge)

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")

doge.aging()

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")

doge.add_orange()

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")


# Output:
"""
doge: doge, 5, ['banana', 'apple']
cate: doge, 5, ['banana', 'apple']
doge: doge, 6, ['banana', 'apple']
cate: doge, 5, ['banana', 'apple']
doge: doge, 6, ['banana', 'apple', 'orange']
cate: doge, 5, ['banana', 'apple', 'orange']
"""