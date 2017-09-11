# from Game import *


class Grid(object):

    def __init__(self, length: int, width: int):
        self.length = length
        self.width = width
        self.pawns = []

        for nRow in range(0, self.length):
            if nRow == 0:
                raise NotImplementedError
                # TODO: implement init
            if nRow == self.length:
                raise NotImplementedError

    def FindPawn(self, x: int, y: int):
        for pawn in self.pawns:
            if (x, y) == pawn.GetPosition(x, y):
                return pawn


Grid(6, 6)


class Pawn(object):
    teams = ["Player", "AI"]

    def __init__(self, x: int, y: int, team: str):
        self.x = x
        self.y = y

        if team not in self.teams:
            TypeError("Invalid team value")
        else:
            self.team = team

    def Move(self, newX: int, newY: int):
        self.x = newX
        self.y = newY

    def GetPosition(self):
        return self.x, self.y

    def GetTeam(self):
        return self.team
