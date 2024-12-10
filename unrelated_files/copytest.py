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
    def lose_icecream(self):
        self.items.remove('icecream')


doge = Dog('doge', 5, ['banana', 'apple', 'kiwi', 'icecream'])
cate = copy.copy(doge)

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")

doge.aging()

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")

doge.add_orange()

print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")

doge.lose_icecream()
print(f"doge: {doge.name}, {doge.age}, {doge.items}")
print(f"cate: {cate.name}, {cate.age}, {cate.items}")


# Output:
"""
doge: doge, 5, ['banana', 'apple', 'kiwi', 'icecream']
cate: doge, 5, ['banana', 'apple', 'kiwi', 'icecream']
doge: doge, 6, ['banana', 'apple', 'kiwi', 'icecream']
cate: doge, 5, ['banana', 'apple', 'kiwi', 'icecream']
doge: doge, 6, ['banana', 'apple', 'kiwi', 'icecream', 'orange']
cate: doge, 5, ['banana', 'apple', 'kiwi', 'icecream', 'orange']
doge: doge, 6, ['banana', 'apple', 'kiwi', 'orange']
cate: doge, 5, ['banana', 'apple', 'kiwi', 'orange']
"""