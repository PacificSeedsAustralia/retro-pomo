"""The contract every screen (widget) follows.

To add a widget (e.g. weather): subclass Widget, then add an instance to
App.pages in main.py. Swipe left/right or use the arrow keys to move between
pages. Every page gets update() each frame, even when not on screen, so timers
keep running in the background.
"""


class Widget:
    name = "widget"

    def __init__(self, app):
        self.app = app

    def update(self, dt):
        pass

    def draw(self, surf):
        pass

    def on_tap(self, pos):
        pass

    def on_key(self, key):
        pass
