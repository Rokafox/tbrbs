# typingtest.py

class Dog():
    def __init__(self, name: str, age: int):
        self.name: str = name
        self.age: int = age

    def bark(self):
        print("Woof! Woof!")

    def wag_tail(self):
        print("Wagging tail")

    def play_with_other_dog(self, other_dog: 'Dog'): # dog is not defined
        print(f"{self.name} is playing with {other_dog.name}")