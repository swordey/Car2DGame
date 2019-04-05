import pyglet


class BaseSprite(pyglet.sprite.Sprite):
    def __init__(self, texture, x, y, batch, subgroup):
        self.texture = texture
        super(BaseSprite, self).__init__(self.texture, batch=batch, group=subgroup)
        self.x = x
        self.y = y

    # def move(self, x, y):
    #     """ This function is just to show you
    #         how you could improve your base class
    #         even further """
    #     self.x += x
    #     self.y += y

    def _draw(self):
        """
        Normally we call _draw() instead of .draw() on sprites
        because _draw() will contains so much more than simply
        drawing the object, it might check for interactions or
        update inline data (and most likely positioning objects).
        """
        self.draw()