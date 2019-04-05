from random import randint
import random

import numpy as np
import pyglet

from Game.Utils import utils


class Track:
    """Track class
    It generates the track lines, the reward gates, checks if car is out of operation area,
    if collided with the track."""
    def __init__(self, batch, width, height, draw_gates):
        self.batch = batch
        self.width, self.height = width, height
        self.draw_gates = draw_gates

        # Create containers for lines and game elements
        self.track = []
        self.gates = []
        self.track_lines = []
        self.gate_lines = []
        self.gate_number_per_track_number = None
        self.inner_line_size = 0

        self.GenTrack()

    # Basic functions
    def GenTrack(self):
        """Generate tracks with corresponding reward gates and add to drawable items
        """

        # Delete tracks if they existed
        for track in self.track:
            track.delete()

        # Delete gates if they existed
        if self.draw_gates:
            for gate in self.gates:
                gate.delete()

        # Delete line arrays
        self.track_lines = None
        self.gate_lines = None

        # Draw new track
        self.track_lines, self.gate_lines = self._generateCircularTrack()

        self.track = []
        for track_line in self.track_lines:
            self.track.append(self.batch.add(2, pyglet.gl.GL_LINES, None,
                           ('v2i', tuple(track_line))))

        self.gates = []
        if self.draw_gates:
            for gate in self.gate_lines:
                self.gates.append(self.batch.add(2, pyglet.gl.GL_LINES, None,
                               ('v2i', tuple(gate))))

    def get_starting_point(self):
        """Give the start point for the car
        :return start coordinates for the car instace(s)
        """
        return self.player_sp

    def check_collision(self, player_lines, interesting_gate_number):
        """Check collision for the provided player lines
        :argument player_lines: player lines to check the collisions with
        :argument interesting_gate_number: id of the gate, which should be entered by the car. Therefore,
        track lines can be selected that is close to that gate line.
        :return true, if car collided with the track, else false"""
        for track_line in self._get_relevant_tracklines(interesting_gate_number):
            for player_line in player_lines:
                if utils.doIntersect(track_line[:2], track_line[2:4], player_line[0], player_line[1]):
                    return True
        return False

    def is_out_of_ground(self, car):
        """Check if car is outside of the operating area, which is the size of the window -10 in each side
        :argument car: car instance that holds the position of the car
        :return true, if car is not in the operating area, else false"""
        return not (10 <= car.x <= self.width-10 and 10 <= car.y <= self.height-10)

    # Helper funtions
    def _generateCircularTrack(self):
        """Generate circular track lines with gates lines
        :return track lines, gate lines"""
        cx = self.width / 2
        cy = self.height / 2
        scaler = 1
        step = 16
        safety_dist = 50
        lane_width = 90
        sine_amplitude = 25

        points_in = []
        points_out = []

        sine_length = []
        max_length = 360
        while max_length > 0:
            length = randint(50, 100)
            if max_length <= 50:
                if max_length < 30:
                    sine_length[-1] = np.array(sine_length[-1]) + max_length
                else:
                    sine_length.append(max_length)
                max_length -= max_length
                break
            if max_length - length > 0:
                sine_length.append(length)
                max_length -= length
        sine_idx = 0
        running_angle = 0

        for angle in range(0, 360 * scaler, step):
            rad = np.deg2rad(angle / scaler)
            if angle > running_angle + sine_length[sine_idx]:
                running_angle += sine_length[sine_idx]
                sine_idx += 1

            a = self.height / 2 - safety_dist - lane_width / 2 + sine_amplitude * \
                                                                      np.sin(
                                                                          (rad - np.deg2rad(running_angle)) * (
                                                                          360 / sine_length[sine_idx]))
            b = self.width / 2 - safety_dist - lane_width / 2 + sine_amplitude * \
                                                                     np.sin(
                                                                         (rad - np.deg2rad(running_angle)) * (
                                                                         360 / sine_length[sine_idx]))

            p = [int(np.cos(rad) * (b - lane_width / 2) + cx + 0.5),
                 int(np.sin(rad) * (a - lane_width / 2) + cy + 0.5)]
            p2 = [int(np.cos(rad) * (b + lane_width / 2) + cx + 0.5),
                  int(np.sin(rad) * (a + lane_width / 2) + cy + 0.5)]

            points_in.append([p[0], p[1]])
            points_out.append([p2[0], p2[1]])

        self.gate_number_per_track_number = int(len(points_in) / 45 + 0.5)
        gates = self._generate_gates_for_every_xth_point(points_in, points_out, self.gate_number_per_track_number)

        self.player_sp = (np.array(points_in[0]) + np.array(points_out[0])) / 2

        lines_in = self._create_lines_from_points(points_in)
        self.inner_line_size = len(lines_in)
        lines_out = self._create_lines_from_points(points_out)
        lines_in += lines_out
        return lines_in, gates

    def _generate_gates_for_every_xth_point(self, inner_points, outer_points, every_xth):
        """Generate gates for every xth point of track
        :argument inner_points: points of the inner part of the track
        :argument outer_points: points of the outer part of the track
        :argument every_xth: every which x should have gates from the track points
        Note: it has to be at least 1 and integer
        :return gate lines
        """
        gates = []
        cnt = 0
        for i, o in zip(inner_points, outer_points):
            if cnt % every_xth == 0:
                gates.append([i[0],i[1],o[0],o[1]])
            cnt += 1
        return gates

    def _create_lines_from_points(self, points):
        """Create lines from the provided points, which should create a closed loop
        :argument points: to create the lines from
        :return created closed loop lines
        """
        lines = []
        for idx in range(len(points)-1):
            lines.append([points[idx][0],points[idx][1],points[idx+1][0],points[idx+1][1]])
        lines.append([points[-1][0], points[-1][1], points[0][0], points[0][1]])
        return lines

    def _get_relevant_tracklines(self, gate_number):
        """Get the track lines that is close to the provided gate_number
        :argument gate_number: the gate id, where the track lines should be looked for.
        :return relevant track lines"""
        relevant_track_id = gate_number * self.gate_number_per_track_number
        first_id = (relevant_track_id - 2 * self.gate_number_per_track_number)%self.inner_line_size
        second_id = (relevant_track_id + 2 * self.gate_number_per_track_number)%self.inner_line_size
        if second_id > first_id:
            return self.track_lines[first_id:second_id] + \
                   self.track_lines[first_id + self.inner_line_size:second_id + self.inner_line_size]
        else:
            return self.track_lines[first_id:self.inner_line_size] + self.track_lines[:second_id] + \
                   self.track_lines[self.inner_line_size+first_id:] + \
                   self.track_lines[self.inner_line_size:second_id+self.inner_line_size]

