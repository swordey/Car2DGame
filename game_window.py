import pyglet
from Game.Objects.car import Car
from Game.Track.track import Track
from Game.Utils import utils
import os

# To load the resources aka images
pyglet.resource.path = [os.path.dirname(os.path.realpath(__file__))+'/resources']
pyglet.resource.reindex()


class GameWindow(pyglet.window.Window):
    def __init__(self, update_screen, width, height):
        self.update_screen = update_screen
        if self.update_screen:
            super(GameWindow, self).__init__(width, height, fullscreen=False)

        self.batches = {}
        self.subgroups = {}

        self._handles = []

        self.batches['main'] = pyglet.graphics.Batch()
        self.subgroups['base'] = pyglet.graphics.OrderedGroup(0)

        # Create Track
        self.track = None
        self.car_starting_point = None  # This is needed to know where cars will be inited

        # Create car instances
        self.car_number = 0
        self.car_image = pyglet.resource.image("car.jpg")
        utils.center_image(self.car_image)

        # Game params
        self.max_frames_of_game = 1000
        self.episode = 1
        self.time = 0
        self.species_per_population = 0

        # Note: We put the sprites in `_handles` because they will be rendered via
        # the `self.batches['main']` batch, and placing them in `self.sprites` will render
        # them twice. But we need to keep the handle so we can use `.move` and stuff
        # on the items later on in the game making process ;)

        self.alive = 1

    # Important GameWindow functions
    def render(self):
        """Render display
        If a window is created, this function renders it.
        """
        self.clear()

        for batch_name, batch in self.batches.items():
            batch.draw()

        # for sprite_name, sprite in self.sprites.items():
        #     sprite._draw()

        self.flip() # This updates the screen, very much important.

    def on_draw(self):
        """What to do during drawing
        """
        self.render()

    def on_close(self):
        """What to do when application is closed
        """
        self.alive = 0

    def run(self):
        """ Game loop
        This is the function, that will run 'forever', and calls the game functions functions.
        """
        while self.alive == 1:
            self.update()

            # -----------> This is key <----------
            # This is what replaces pyglet.app.run()
            # but is required for the GUI to not freeze.
            # Basically it flushes the event pool that otherwise
            # fill up and block the buffers and hangs stuff.
            if self.update_screen:
                self.render()
                event = self.dispatch_events()

            self.time += 1

            # Fun fact:
            #   If you want to limit your FPS, this is where you do it
            #   For a good example check out this SO link:
            #   http://stackoverflow.com/questions/16548833/pyglet-not-running-properly-on-amd-hd4250/16548990#16548990

    def update(self):
        """Update function
        The function that actually realizes what happens in the game.
        UserDefined, otherwise it will throw an error.
        """
        raise Exception("You should define an update function, how the objects should behave.")

    def create_window(self, width, height):
        """Creates the game window
        This will create the actual window, where you can see the game.
        Note: it generates the track, as it depends on the window size.
        :argument width: the width of the window
        :argument height: the height of the window
        """
        self.update_screen = True
        super(GameWindow, self).__init__(width, height, fullscreen=False)
        self.width = width
        self.height = height

    def set_playground_size(self, width, height):
        """Set the size of the playground
        Note: it has to be called if we don't call create_window
        :argument width: width of playground
        :argument height: height of playground
        """
        self.width = width
        self.height = height

    # Game setup functions
    def generate_track(self, draw_gates=False):
        """Generates track
        Basically, it will create the playground for the cars.
        """
        if self.width is 0 and self.height is 0:
            raise Exception("'create_window(width, height)' or 'set_playground_size(width, height)' has to be called"
                            " before 'generate_track' method")
        self.track = Track(self.batches['main'], self.width, self.height, draw_gates)
        self.car_starting_point = self.track.get_starting_point()

    def set_car_number(self, car_number, light_ray_angles, lapse_until_won=4, max_light_ray_length=100):
        """Creates the cars
        This function will create the desired number of car instances with the provided light ray angles.
        :argument car_number: number of cars to produce
        :argument light_ray_angles: the directions of the separate light rays, which the car will see from the 'world'
        :argument lapse_until_won: after how many lapse will the car won
        :argument max_light_ray_length: the maximum distance the light rays can see ahead (if the wall is farther,
        it will result in the max number)
        """
        self.species_per_population = car_number
        for car_id in range(car_number):
            self.car_number += 1
            self._handles.append(Car(self, self.car_image, self.car_starting_point[0],
                                     self.car_starting_point[1], max_light_ray_length,
                                     light_ray_angles,
                                     self.car_number - 1,
                                     lapse_until_won,
                                     self.batches['main'],
                                     self.subgroups['base']))
            print("\rCar {0}/{1} is generated.".format(car_id+1, car_number),end='')

    def set_game_length(self,game_length):
        """Set the length of the game
        Sets how many generations or episodes will we have.
        :argument game_length: the length of the game that should be set
        """
        self.max_frames_of_game = game_length

    def cancel_die_by_time(self):
        """Turn off die by time
        Time reduces the car reward, so if car does not do anything, it will die."""
        for car in self.get_cars():
            car.cancel_time_punishment()

    # Game Logic Functions
    def reset(self):
        """Resets the game
        Resets everything, and put everything in its initial position.
        """
        self.time = 0
        for car in self._handles:
            car.reset()

    def regenerate_track(self):
        """Regenerate track
        The track is regeneratable during the game"""
        self.track.GenTrack()

    def get_cars(self,ids=None):
        """Returns with cars
        :argument ids: [a, b] the start and end id of cars to return, if not provided all cars will be returned
        :return cars"""
        if ids is None:
            return self._handles
        else:
            return self._handles[ids[0]:ids[1]]

    def is_game_ended(self):
        """Returns if the game is over
        Stops game, if the last game is over.
        :return it returns true if all cars are died, else false"""
        game_ended = False
        if self._cars_died():
            game_ended = True
            if self.episode >= self.max_frames_of_game:
                self.alive = 0
        return game_ended

    def set_lapse_to_won(self, lapse_to_won):
        """Set after how many lapse should the cars win
        :argument lapse_to_won: value to set
        """
        for car in self.get_cars():
            car.set_lapse_to_won(lapse_to_won)

    # Helper functions
    def _cars_died(self,ids=None):
        """Checks if specified id cars are died
        :argument ids which cars to check, if none is provided all cars will be checked
        :return true if the specified cars are died, else false"""
        dies = [car.died or car.won for car in self.get_cars(ids)]
        return sum(dies) == len(dies)
