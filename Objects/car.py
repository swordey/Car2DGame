import math

import numpy as np
import pyglet

# from Brains.simplebrain import SimpleBrain
from Game.Objects.physical_objects import PhysicalObject
from Game.Utils import utils

pyglet.resource.path = ['./Game/resources']
pyglet.resource.reindex()

# Images
car_image = pyglet.resource.image("car.jpg")
utils.center_image(car_image)


class Car(PhysicalObject):
    def __init__(self,f_ray_angles,f_brain,f_track,f_ray_length = 100, *args, **kwargs):
        super().__init__(img=car_image, *args, **kwargs)
        # Car properties
        self.orig_x = self.x
        self.orig_y = self.y
        self.orig_rotation = self.rotation
        self.length = self.image.width
        self.width2 = self.image.height
        self.color = (0, 255, 0)

        self.died = False
        self.won = False

        self.track = f_track
        self.num_of_gates = len(self.track.gates)

        # Car moving properties
        self.speed = 5000
        self.rotate_speed = 150

        # State params
        self.ray_length = f_ray_length
        self.ray_angles = f_ray_angles
        self.ray_endpoints = []
        self.cur_state = []
        self.last_state = []

        self.next_gate_to_reach = 0

        self.score = 0
        self.reward = 0
        self.steps = 0

        self.brain = f_brain

    def reset(self):
        self.x = self.orig_x
        self.y = self.orig_y
        self.rotation = -90
        self.score = 0
        self.reward = 0
        self.steps = 0
        self.cur_state = []
        self.last_state = []
        self.next_gate_to_reach = 0
        self.died = False
        self.won = False

    def incrementScore(self):
        self.score += 1

    def getPoints(self):
        angle_rad = math.radians(self.rotation)
        right_edge = [self.x + self.length * math.cos(angle_rad) / 2 + self.width2 * math.sin(angle_rad) / 2,
                      self.y - self.width2 * math.cos(angle_rad) / 2 + self.length * math.sin(angle_rad) / 2]
        points = [[right_edge[0],
                   right_edge[1]],
                  [right_edge[0]-self.width2*math.sin(angle_rad),
                   right_edge[1]+self.width2*math.cos(angle_rad)],
                  [right_edge[0]-self.width2*math.sin(angle_rad)-self.length*math.cos(angle_rad),
                   right_edge[1]+self.width2*math.cos(angle_rad)-self.length*math.sin(angle_rad)],
                  [right_edge[0]-self.length*math.cos(angle_rad),
                   right_edge[1]-self.length*math.sin(angle_rad)]]
        return points

    def getLines(self):
        points = self.getPoints()
        lines = [[points[0],points[1]],
                 [points[1], points[2]],
                 [points[2], points[3]],
                 [points[3], points[0]]]
        return lines

    def stop(self):
        self.velocity_x = 0
        self.velocity_y = 0

    def calcState(self):
        self.last_state = self.cur_state
        self.cur_state = np.ones([len(self.ray_angles)])
        for idx,ang in enumerate(self.ray_angles):
            real_ang = self.rotation-ang
            real_ang_rad = -math.radians(real_ang)
            ray_line = [self.x, self.y, int(self.x + self.ray_length * np.cos(real_ang_rad) + 0.5),
                        int(self.y + self.ray_length * np.sin(real_ang_rad) + 0.5)]
            for line in self.track.track_lines:
                dist, point = utils.calcIntersectionPoint2(np.array(line), np.array(ray_line))
                if point is not None and point[0] >= 0 and point[1] >= 0:
                    self.ray_endpoints.append(list(np.array([self.x,self.y]).astype(int))+list(np.array(point).astype(int)))
                    self.cur_state[idx] = dist/self.ray_length
        self.cur_state = np.reshape(self.cur_state, [1, len(self.cur_state)])

    def getState(self):
        self.calcState()
        return self.cur_state

    def nextGatePassed(self):
        cur_line = self.track.gates[self.next_gate_to_reach]
        for player_line in self.getLines():
            if utils.doIntersect(cur_line[:2], cur_line[2:4], player_line[0], player_line[1]):
                self.next_gate_to_reach += 1
                self.next_gate_to_reach = self.next_gate_to_reach % self.num_of_gates
                self.incrementScore()
                return True
        return False

    # # Rewards
    def calcReward(self):
        self.reward -= 0.2
        if self.nextGatePassed():
            self.reward += 1

    def getReward(self):
        self.calcReward()
        return self.reward

    # # Dynamics
    def step(self,action):
        self.move(action, 0.04)

        # Get reward and new state for performed action
        new_state = self.getState()
        reward = self.getReward()

        if self.track.check_collision(self.getLines()):
            reward = -500

        # Check if we hit score 100 or we are below -500
        if self.score == 100 or reward <= -500:
            self.died = True

        if self.track.isOutOfGround(self):
            self.died = True

        return reward, new_state, self.died

    def move(self,key_pressed, dt):
        '''
        The function that moves the car on the screen
        :param key_pressed: [up, left, right] if 1, they are pushed, if 0 they are not
        :return:
        '''
        if 1 == key_pressed[1]:
            self.rotation -= self.rotate_speed * dt
        if 1 == key_pressed[2]:
            self.rotation += self.rotate_speed * dt
        if 1 == key_pressed[0]:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.speed * dt
            force_y = math.sin(angle_radians) * self.speed * dt
            self.velocity_x = force_x
            self.velocity_y = force_y
        else:
            self.stop()
        super(Car, self).update(dt)
        self.steps += 1