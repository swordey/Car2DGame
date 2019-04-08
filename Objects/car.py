import math

import numpy as np

from Game.Objects.base_sprite import BaseSprite
from Game.Utils import utils


class Car(BaseSprite):
    def __init__(self, parent, car_image, x, y, ray_length, ray_angles, id, lapse_to_won,  batch, subgroup):
        super().__init__(car_image,x,y,batch,subgroup)
        self.id = id
        self.track = parent.track
        self.num_of_gates = len(self.track.gate_lines)
        self.lapse_to_won = lapse_to_won
        self.batch = batch

        # Car properties
        self.velocity_x, self.velocity_y = 0.0, 0.0
        self.rotation = -90
        self.orig_x = x
        self.orig_y = y
        self.orig_rotation = self.rotation
        self.length = self.image.width
        self.width2 = self.image.height

        self.died = False
        self.won = False

        # Car moving properties
        self.speed = 5000
        self.rotate_speed = 150

        # State params
        self.ray_length = ray_length
        self.ray_angles = ray_angles
        self.ray_endpoints = []
        self.ray_points_draw = []
        self.cur_state = []
        self.last_state = []

        self.next_gate_to_reach = 0

        self.score = 0
        self.last_reward = 0
        self.reward = 0
        self.steps = 0

        self.time_punishment = False

    # Basic functionality
    def reset(self):
        """Reset values to initial one"""
        self.x = self.orig_x
        self.y = self.orig_y
        self.rotation = -90
        self.score = 0
        self.last_reward = 0
        self.reward = 0
        self.steps = 0
        self.cur_state = []
        self.last_state = []
        self.next_gate_to_reach = 0
        self.died = False
        self.won = False

    def _get_points(self):
        """Get the 4 corner points of the car
        :return 4 corner points"""
        angle_rad = math.radians(self.rotation)
        right_edge = [self.x + self.length * np.cos(angle_rad) / 2 + self.width2 * np.sin(angle_rad) / 2,
                      self.y - self.width2 * np.cos(angle_rad) / 2 + self.length * np.sin(angle_rad) / 2]
        points = [[right_edge[0],
                   right_edge[1]],
                  [right_edge[0]-self.width2*np.sin(angle_rad),
                   right_edge[1]+self.width2*np.cos(angle_rad)],
                  [right_edge[0]-self.width2*np.sin(angle_rad)-self.length*np.cos(angle_rad),
                   right_edge[1]+self.width2*np.cos(angle_rad)-self.length*np.sin(angle_rad)],
                  [right_edge[0]-self.length*np.cos(angle_rad),
                   right_edge[1]-self.length*np.sin(angle_rad)]]
        return points

    def get_lines(self):
        """Returns with the lines of the car
        :return lines of car"""
        points = self._get_points()
        lines = [[points[0],points[1]],
                 [points[1], points[2]],
                 [points[2], points[3]],
                 [points[3], points[0]]]
        return lines

    def step(self,action):
        """Steps with the car, and calculate reward and next state
        :argument action: which direction to move
        """
        self._set_speed(action, 0.04)
        self._move(0.04)

        # Get reward and new state for performed action
        new_state = self.get_state()
        reward = self.get_reward()

        if self.track.check_collision(self.get_lines(), self.next_gate_to_reach):
            reward = -10
            self.reward = reward

        # Check if we hit score 100 or we are below -10
        if self.score == self.num_of_gates * self.lapse_to_won:
            self.reward = reward
            self.won = True

        if reward <= -10:
            reward = -10
            self.reward = reward
            self.died = True


        if self.track.is_out_of_ground(self):
            reward = max(-10,reward)
            self.reward = reward
            self.died = True

        return reward, new_state, self.died or self.won

    def get_state(self):
        """Get the state of the car
        It returns the distance in the preset directions to the closest object.
        Note: if distance is bigger then the maximum ray length, it returns the maximum.
        :return direction array
        """
        self._calc_state()
        return self.cur_state

    def get_reward(self):
        """Get the reward
        Reward is the point, that the car gets for proceeding in the playground
        :return reward
        """
        self._calc_reward()
        return self.reward

    def set_lapse_to_won(self,lapse_to_won):
        """Set after how many lapse does the car win
        :argument lapse_to_won: value to set"""
        self.lapse_to_won = lapse_to_won

    def cancel_time_punishment(self):
        """Turn off time punishment
        Time reduces reward, which can kill car."""
        self.time_punishment = False

    # Helper functions
    def _move(self, dt):
        """Moves the car with its speed with the provided time increment
        :argument dt: time increment to calc position difference from speed"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.steps += 1

    def _set_speed(self, key_pressed, dt):
        """Based on direction and time increment, set the speed of the car
        :argument key_pressed: selected directions [up, left, down] array, if 1 it is selected else it is not
        :argument dt: time increment to calculate the rotation
        """
        if 1 == key_pressed[1]:
            self.rotation -= self.rotate_speed * dt
        if 1 == key_pressed[2]:
            self.rotation += self.rotate_speed * dt
        if 1 == key_pressed[0]:
            angle_radians = -math.radians(self.rotation)
            force_x = np.cos(angle_radians) * self.speed * dt
            force_y = np.sin(angle_radians) * self.speed * dt
            self.velocity_x = force_x
            self.velocity_y = force_y
        else:
            self._stop()

    def _calc_reward(self):
        """Calculate the reward helper function
        It is calculated from the passed reward gates and the used step number
        """
        self.last_reward = self.reward
        if self.time_punishment:
            self.reward -= 0.2
        if self._next_gate_passed():
            self.reward += 10

    def _calc_state(self):
        """Calculate the current state helper function
        :return current state
        """
        self.last_state = self.cur_state
        self.cur_state = np.ones([len(self.ray_angles)])
        self.ray_endpoints = []
        for idx,ang in enumerate(self.ray_angles):
            real_ang = self.rotation-ang
            real_ang_rad = -np.radians(real_ang)
            ray_line = [self.x, self.y, int(self.x + self.ray_length * np.cos(real_ang_rad) + 0.5),
                        int(self.y + self.ray_length * np.sin(real_ang_rad) + 0.5)]
            for line in self.track._get_relevant_tracklines(self.next_gate_to_reach):
                dist, point = utils.calcIntersectionPoint2(np.array(line), np.array(ray_line))
                if point is not None and point[0] >= 0 and point[1] >= 0:
                    self.ray_endpoints.append(list(np.array([self.x,self.y]).astype(int))+list(np.array(point).astype(int)))
                    self.cur_state[idx] = dist/self.ray_length
        self.cur_state = np.reshape(self.cur_state, [1, len(self.cur_state)])

    def _stop(self):
        """Stop the motion of the car
        It zeros the velocities
        """
        self.velocity_x = 0
        self.velocity_y = 0

    def _next_gate_passed(self):
        """Checks if the following gate is passed
        Note: it increments the next gate counter in case of passing.
        :return if next gate is passe true, else false
        """
        cur_line = self.track.gate_lines[self.next_gate_to_reach]
        for player_line in self.get_lines():
            if utils.doIntersect(cur_line[:2], cur_line[2:4], player_line[0], player_line[1]):
                self.next_gate_to_reach += 1
                self.next_gate_to_reach = self.next_gate_to_reach % self.num_of_gates
                self.score += 1
                return True
        return False
