#!/usr/bin/env python3
import itertools
import random
import sys


animals = [
    "fas fa-paw",
    "fas fa-otter",
    "fas fa-hippo",
    "fas fa-dog",
    "fas fa-kiwi-bird",
    "fas fa-horse-head",
    "fas fa-horse",
    "fas fa-spider",
    "fas fa-fish",
    "fas fa-feather-alt",
    "fas fa-crow",
    "fas fa-cat",
    "fas fa-dragon",
    "fas fa-dove",
    "fas fa-frog",
]

colors = [
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "brown",
    "black",
]


class Animal:
    icons = []
    def __init__(self, number, seed=42):
        '''
        Don't change the seed or you will change all the icons
        '''
        max_len = len(colors) * len(animals)
        self.number = number % max_len
        if self.icons:
            return
        random.seed(42)
        self.icons = random.sample(list(itertools.product(colors, animals)),
                                   max_len)

    def style(self):
        return f"<style>\n{self.css()}\n</style>"

    def css(self):
        color, icon = self.icons[self.number]
        icon = self.dot_class().split()[1]
        return f'{icon} {{\n  color: {color};\n}}'

    def color(self):
        color, icon = self.icons[self.number]
        return color

    def classes(self):
        color, icon = self.icons[self.number]
        return icon

    def dot_class(self):
        color, icon = self.icons[self.number]
        return ' '.join([f'.{i}' for i in icon.split()])


if __name__=="__main__":
    maxlen = len(animals) * len(colors)
    if len(sys.argv) < 2 or int(sys.argv[1]) > maxlen:
        sys.exit(f'Enter a number between 0 and {maxlen}')
    icon = Animal(int(sys.argv[1]))
    print(icon.style())
    print(icon.color())
    print(icon.classes())
