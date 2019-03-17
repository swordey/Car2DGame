import math
from math import atan2
from random import randint

import numpy as np
import pyglet

from Game.Utils import utils


class Track:
    def __init__(self, window, f_draw_gates = False):
        self.window = window
        self.draw_gates = f_draw_gates

        self.batch = pyglet.graphics.Batch()
        self.gate = pyglet.graphics.Batch()
        self.intsecpoints = pyglet.graphics.Batch()
        self.vert_list = []
        self.gates = []
        self.dist = 100
        self.dist2 = 80

        # self.track_lines = [[10, 300, 350, 400]]
        self.track_lines, self.gates = self.generateTrack2()

        self.intersection_points = []

        for track_line in self.track_lines:
            self.batch.add(2, pyglet.gl.GL_LINES, None,
                           ('v2i', tuple(track_line)))

        for gate in self.gates:
            self.gate.add(2, pyglet.gl.GL_LINES, None,
                           ('v2i', tuple(gate)))

    def getStartingPoint(self):
        return self.player_sp

    def generateTrack3(self):
        num_points_to_gen = 5
        safety_zone = 50

        points = []
        for idx in range(num_points_to_gen):
            points.append([randint(safety_zone,self.window.width - safety_zone),randint(safety_zone,self.window.height - safety_zone)])

        points.sort(key=lambda c: atan2(self.window.width/2-c[0], self.window.height/2-c[1]))

        points2 = []
        center = np.array([np.mean(np.array(points)[:,0]),np.mean(np.array(points)[:,1])])
        for idx in range(len(points)):
            p = list((center + 1.5*(points[idx]-center)).astype(int))
            points2.append(p)

        lines = self.createLinesFromPoints(points)
        lines2 = self.createLinesFromPoints(points2)

        lines += lines2

        return lines

    def createLinesFromPoints(self,points):
        lines = []
        point = points[0]
        points.remove(point)
        while 0 < len(points):
            best_id = 0
            best_dist = self.distL2(point,points[best_id])
            for p_id in range(1,len(points)):
                cur_dist = self.distL2(point,points[p_id])
                if cur_dist < best_dist:
                    best_dist = cur_dist
                    best_id = p_id

            sel_point = points[best_id]
            points.remove(sel_point)
            lines.append([point[0],point[1],sel_point[0],sel_point[1]])
            point = sel_point
        lines.append([point[0],point[1],lines[0][0],lines[0][1]])
        return lines

    def distL2(self,point1,point2):
        return np.sqrt(sum((np.array(point1)-np.array(point2))**2))

    def genearateGates(self,points1,points2, width, side):
        res = 20
        gates = []
        for id in range(4):
            p1_1 = np.array(points1[id])
            p2_1 = np.array(points2[id])
            next_id = (id+1)%4
            p1_2 = np.array(points1[next_id])
            p2_2 = np.array(points2[next_id])
            for step in range(res+1):
                curr_p_1 = list(np.array(p1_1 + step * (p1_2-p1_1) / res).astype(int))
                curr_p_2 = list(np.array(p2_1 + step * (p2_2-p2_1) / res).astype(int))
                gates.append([curr_p_1[0], curr_p_1[1], curr_p_2[0], curr_p_2[1]])
                # if 1 == side[id]:
                #     gates.append([curr_p_1[0],curr_p_1[1],curr_p_2[0],curr_p_2[1]])
                # else:
                #     gates.append([curr_p[0] - width, curr_p[1] , curr_p[0] + width, curr_p[1]])
        return gates

    def generateTrack2(self):
        width = self.window.width-120*2
        height = self.window.height-120*2
        thickness = 80

        mid_points = list(np.array([[self.window.width/2-width/2,self.window.height/2-height/2],
                  [self.window.width/2-width/2,self.window.height/2+height/2],
                  [self.window.width/2+width/2,self.window.height/2+height/2],
                  [self.window.width/2+width/2,self.window.height/2-height/2]]).astype(int))

        self.player_sp = mid_points[0]

        pre = [[-1,-1],[-1,1],[1,1],[1,-1]]
        pre2 = -1*np.array(pre)

        points = []
        for p_id in range(len(mid_points)):
            p = list(np.array(mid_points[p_id]+np.array(pre[p_id])*np.array([thickness/2,thickness/2])).astype(int))
            points.append(p)

        points2 = []
        for p_id in range(len(mid_points)):
            p = list(np.array(mid_points[p_id]+np.array(pre2[p_id])*np.array([thickness/2,thickness/2])).astype(int))
            points2.append(p)

        gates = self.genearateGates(points,points2, int(thickness / 2), [0, 1, 0, 1])

        lines = self.createLinesFromPoints(points)
        lines2 = self.createLinesFromPoints(points2)

        lines += lines2

        return lines, gates

    def generateTrack(self):
        self.dist = 80
        self.dist2 = 160
        line_number = 20
        ran = 20

        basic_track = [[self.dist,self.dist,self.window.width-self.dist,self.dist],
                 [self.window.width-self.dist,self.dist,self.window.width-self.dist,self.window.height-self.dist],
                 [self.window.width-self.dist,self.window.height-self.dist,self.dist,self.window.height-self.dist],
                 [self.dist,self.window.height-self.dist,self.dist,self.dist],

                 [self.dist2, self.dist2, self.window.width - self.dist2, self.dist2],
                 [self.window.width - self.dist2, self.dist2, self.window.width - self.dist2, self.window.height - self.dist2],
                 [self.window.width - self.dist2, self.window.height - self.dist2, self.dist2, self.window.height - self.dist2],
                 [self.dist2, self.window.height - self.dist2, self.dist2, self.dist2]]

        track = []
        gate = []
        dir_to_modify = [1,0,1,0] # 1 - up-down, 0 left-right
        index = 0
        for line in basic_track:
            pushes = [randint(0,ran)-int(ran/2) for x in range(line_number)]
            pushes[0] = 0
            pushes[line_number-1] = 0
            for idx in range(line_number):
                short_line = np.array([line[0]+idx*(line[2]-line[0])/line_number,line[1]+idx*(line[3]-line[1])/line_number,
                 line[0] + (idx+1) * (line[2] - line[0])/line_number, line[1] + (idx+1) * (line[3] - line[1])/line_number]).astype(int)

                if 1 == dir_to_modify[index]:
                    short_line += np.array([0,pushes[idx-1],0,pushes[idx]])
                else:
                    short_line += np.array([pushes[idx-1], 0, pushes[idx],0])

                track.append(short_line)
            index += 1
            index = index % 4
        return track

    def draw(self):
        self.batch.draw()
        if self.draw_gates:
            self.gate.draw()

    def check_collision(self, player_lines):
        for track_line in self.track_lines:
            for player_line in player_lines:
                if utils.doIntersect(track_line[:2], track_line[2:4], player_line[0], player_line[1]):
                    return True
        return False

    def isOutOfGround(self,car):
        return not (10 <= car.x <= self.window.width-10 and 10 <= car.y <= self.window.height-10)

    def delDistPoints(self):
        for vert in self.vert_list:
            vert.delete()
        self.vert_list = []

    def calcIntSecPoints(self):
        self.delDistPoints()
        for point in self.intersection_points:
            self.vert_list.append(self.intsecpoints.add(2, pyglet.gl.GL_LINES, None,
                           ('v2i', tuple(point))))

    def getDistances(self,car,angle_step,max_angle = 360):
        x = car.x
        y = car.y
        start_angle = car.rotation
        line_length = 100
        self.intersection_points = []
        car.state = np.ones([int(max_angle/angle_step)])
        for idx in range(int(max_angle/angle_step)):
            angle = -math.radians(start_angle-max_angle/2+idx*angle_step)
            car_line = [x, y, int(x + line_length * np.cos(angle) + 0.5), int(y + line_length * np.sin(angle) + 0.5)]
            for line in self.track_lines:
                dist, point = utils.calcIntersectionPoint2(np.array(line), np.array(car_line))
                if point is not None and point[0] >= 0 and point[1] >= 0:
                    self.intersection_points.append(list(np.array([x,y]).astype(int))+list(np.array(point).astype(int)))
                    car.state[idx] = dist/line_length
        self.calcIntSecPoints()
