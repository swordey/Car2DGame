from Game.Objects.base_sprite import BaseSprite


class PhysicalObject(BaseSprite):
    def __init__(self,img,x,y,batch, subgroup, *args, **kwargs):
        super().__init__(img, x, y, batch, subgroup, *args, **kwargs)
        self.velocity_x, self.velocity_y = 0.0, 0.0

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt