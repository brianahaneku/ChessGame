#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 16:29:30 2021

@author: brianahaneku
"""
import random


def getRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def getBestMove(validMoves):
    return