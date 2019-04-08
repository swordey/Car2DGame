import pyglet
from Game.game_window import GameWindow
from pyglet.window import key

'''Params begin'''
# After how many does should the running stop
episodes = 50000
# Angles of the lidar rays as the current state of the car
# 0 points forward -180 or 180 backwards
ray_angles = [-180,-135,-90,-60,-30,0,30,60,90,135]
# Which move is done for which action
# [up, left, right]
action2movetable = [[0,0,0],[0,1,0],[1,1,0],[1,0,0],[1,0,1],[0,0,1]]
# A brain/agent to give to a player what to do
# In case of multiple instances, every one will get one...
brain = []
'''Params end'''


class MyGame(GameWindow):
    def __init__(self, update_screen, width, height):
        super().__init__(update_screen, width, height)

        self.best_reward = 0

        # Labels
        self.epi_label = pyglet.text.Label(text="Episode: 1", x=10, y=35, batch=self.batches['main'],
                                           group=self.subgroups['base'])

        self.reward_label = pyglet.text.Label(text="Best reward: 0", x=10, y=20, batch=self.batches['main'],
                                              group=self.subgroups['base'])

    def update(self):
        for car in self.get_cars():
            if not car.died:
                state = car.get_state()
                action = [keys[key.UP],keys[key.LEFT],keys[key.RIGHT]]
                reward, new_state, done = car.step(action)

        if self.is_game_ended():
            self.episode += 1
            if self.get_cars()[0].last_reward > self.best_reward:
                self.best_reward = self.get_cars()[0].last_reward
            self.epi_label.text = "Episode: {0}".format(self.episode)
            self.reward_label.text = "Best reward: {0}".format(self.best_reward)
            self.reset()


game = MyGame(True, 800, 600)
keys = key.KeyStateHandler()
game.push_handlers(keys)

# Generate track
game.generate_track(draw_gates=False)

# Set player number
game.set_car_number(1, ray_angles, lapse_until_won=5)

# Set length of the game
game.set_game_length(episodes)

# Cancel die by time (time -> reduces reward -> below certain reward car dies)
game.cancel_die_by_time()

game.reset()

if __name__ == "__main__":
    game.run()


