import pyglet
from Game.game import Game
from pyglet.window import key

'''Params begin'''
# After how many does should the running stop
episodes = 50000
# Angles of the lidar rays as the current state of the car
# 0 points forward -180 or 180 backwards
f_ray_angles = [-180,-135,-90,-60,-30,0,30,60,90,135]
# Which move is done for which action
# [up, left, right]
f_action2movetable = [[0,0,0],[0,1,0],[1,1,0],[1,0,0],[1,0,1],[0,0,1]]
# A brain/agent to give to a player what to do
# In case of multiple instances, every one will get one...
brain = []
'''Params end'''


class MyGame(Game):
    def update(self,dt):
        for car in self.getCars():
            if not car.died:
                state = car.getState()
                action = [keys[key.UP],keys[key.LEFT],keys[key.RIGHT]]
                reward, new_state, done = car.step(action)

        if self.isGameEnded():
            self.reset()


window = pyglet.window.Window()
keys = key.KeyStateHandler()
window.push_handlers(keys)

@window.event
def on_draw():
    game.draw()


game = MyGame(window,brain, f_ray_angles, episodes)
game.reset()

if __name__ == "__main__":
    game.start()
    pyglet.app.run()


