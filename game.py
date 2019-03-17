import pyglet

from Game.Objects.car import Car
from Game.Track.track import Track


class Game:
    def __init__(self, f_window,f_brain, f_ray_angles, f_maxEpisode, f_car_number = 1):
        self.window = f_window
        self.maxEpisode = f_maxEpisode

        self.track = Track(self.window)
        self.starting_point = self.track.getStartingPoint()
        self.cars = []
        for idx in range(f_car_number):
            car = Car(f_ray_angles,f_brain,self.track,x=self.starting_point[0], y=self.starting_point[1])
            self.cars.append(car)
            self.window.push_handlers(car)

        self.episode = 1

        # # Labels
        self.epi_label = pyglet.text.Label(text="Episode: 0", x=10, y=35)
        self.reward_label = pyglet.text.Label(text="Reward: 0", x=10, y=20)
        self.score_label = pyglet.text.Label(text="Score: 0", x=10, y=5)

    def reset(self):
        for car in self.cars:
            car.reset()

    def getCars(self):
        return self.cars

    def isGameEnded(self):
        game_ended = False
        if self.allCarsDied():
            game_ended = True
            self.episode += 1
            self.epi_label.text = "Episode: " + str(self.episode) + " / " + str(self.maxEpisode)
            if self.episode >= self.maxEpisode:
                self.stop()

        if len(self.cars) == 1:
            # Update screen values
            self.reward_label.text = "Reward: "+str(self.cars[0].reward)
            self.score_label.text = "Score: "+str(self.cars[0].score)

        return game_ended

    def allCarsDied(self):
        dies = [car.died for car in self.cars]
        if len(dies)>1:
            return (dies == True).all()
        else:
            return dies[0] is True

    def getStates(self):
        states = [car.getState() for car in self.cars]
        return states

    def update(self,dt):
        raise Exception("You should define an update function, how the objects should behave.")

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 30.0)

    def stop(self):
        pyglet.clock.unschedule(self.update)

    def getEpisode(self):
        return self.episode

    def drawCars(self):
        for car in self.cars:
            car.draw()

    def draw(self):
        self.window.clear()
        self.drawCars()
        self.track.draw()

        self.score_label.draw()
        self.reward_label.draw()
        self.epi_label.draw()
