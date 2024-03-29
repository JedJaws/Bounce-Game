#! /usr/bin/env python3
# Christian Verry
# CPSC 386-03
# 2022-03-07
# CJVerry@csu.fullerton.edu
# @JedJaws
#
# Lab 05-00
#
# This module is my first visual game
#


"""
Imports the Bounce demo and executes the main function.
"""


import sys
from game import game

if __name__ == "__main__":
    NUM_BALLS = 5
    if len(sys.argv) > 1:
        NUM_BALLS = int(sys.argv[1])
    if NUM_BALLS >= 50:
        NUM_BALLS = 49
    if NUM_BALLS < 3:
        NUM_BALLS = 3
    video_game = game.BounceDemo(NUM_BALLS)
    video_game.build_scene_graph()
    video_game.run()
