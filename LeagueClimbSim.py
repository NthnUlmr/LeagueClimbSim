# <GPLv3_Header>
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# \copyright
#                    Copyright (c) 2024 Nathan Ulmer.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# <\GPLv3_Header>

##
# \file LeagueClimbSim.py
#
# \author Nathan Ulmer
#
# \date \showdate "%A %d-%m-%Y"
#
# \brief

# Win boosts MMR based on some base amount plus some function of if you were expected to win.
# You gain LP based on the difference between MMR and rank. There seems to be phase lag in the system.
# You can win a bunch in a row and then lose one


import matplotlib.pyplot as plt
import random
import math
import cmath

class Team:
    def __init__(self, isRed, expectedAverageMMR, expectedSigmaMMR, myMMR = 0.0):
        self.membersMMR = []
        self.averageMMR = 0
        if(myMMR == 0.0):
            for i in range(5):
                self.membersMMR.append(random.gauss(expectedAverageMMR,expectedSigmaMMR))
                self.averageMMR += self.membersMMR[-1]
        else:
            for i in range(4):
                self.membersMMR.append(random.gauss(expectedAverageMMR,expectedSigmaMMR))
                self.averageMMR += self.membersMMR[-1]
            self.membersMMR.append(myMMR)
            self.averageMMR += self.membersMMR[-1]
        self.averageMMR /= 5



class Game:
    def __init__(self, expectedAverageMMR, expectedSigmaMMR, myMMR):
        self.AllyTeamIsRed = bool(round(random.uniform(0.0,1.0)))
        self.AllyTeam = Team(self.AllyTeamIsRed, expectedAverageMMR, expectedSigmaMMR, myMMR)
        self.EnemyTeam = Team(not self.AllyTeamIsRed, expectedAverageMMR, expectedSigmaMMR)



    def resolve(self):
        xroleResults = [0,0,0,0,0]
        xlaneResults = [0,0,0]
        likelyhoodScalar = 300 # Assume If you have an MMR 300 lp above the enemy you have autowin on your lane
        for ii in range(5):
            xroleResults[ii] = self.AllyTeam.membersMMR[ii] - self.EnemyTeam.membersMMR[ii]
            xroleResults[ii] /= likelyhoodScalar
            xroleResults[ii] = max(xroleResults[ii], -1.0) # Clamp results between -1 and 1
            xroleResults[ii] = min(xroleResults[ii], 1.0)
            xroleResults[ii] = xroleResults[ii] / 2 + 0.5 # Rescale to 0 to 1
        xlaneResults[0] = ( xroleResults[0] + xroleResults[1] ) / 2 # Bot/Supp
        xlaneResults[1] = xroleResults[2] # Mid
        xlaneResults[2] = (xroleResults[3] + xroleResults[4]) / 2  # Top/Jgl

        botDraw = random.uniform(0,1)
        midDraw = random.uniform(0,1)
        topDraw = random.uniform(0,1)

        laneResults = [ xlaneResults[0] - botDraw, xlaneResults[1] - midDraw,  xlaneResults[2] - topDraw]

        xmidGameResults = (laneResults[0] + laneResults[1] + laneResults[2]) / 3 / 2 + 0.5
        midGameDraw = random.uniform(0,1)

        midGameResults = xmidGameResults - midGameDraw

        xEndGameResults = midGameResults / 2 + 0.5
        endGameDraw = random.uniform(0,1)

        endGameResults = xEndGameResults - endGameDraw

        didAllyTeamWin = endGameResults > 0.0

        teamMMRDiff = self.AllyTeam.averageMMR - self.EnemyTeam.averageMMR

        #if didAllyTeamWin and teamMMRDiff > 0:
        #    # Won on expected win
        #elif didAllyTeamWin and teamMMRDiff < 0:
        #    # Won on expected loss
        #elif not didAllyTeamWin and teamMMRDiff > 0:
        #    # Lost on Expected Win
        #elif not didAllyTeamWin and teamMMRDiff < 0:
        #    # Lost on Expected Loss

        lpScalar = teamMMRDiff / 300 * 10 # Get 10 extra LP if winning on expected guarunteed loss
        lpBase = 25
        if didAllyTeamWin:
            lpGain = lpBase + lpScalar
        else:
            lpGain = -1 * ( lpBase + lpScalar)
        roundLP = round(lpGain)
        return roundLP

def run(nGames,startingLP,startingLPGain,startingLPLoss,WRLast10):

    MMRTm = []
    LPTm = [startingLP]
    WinTM = []


    MMREstimate = startingLP + (WRLast10 - 0.5) * 2 * 300 # Assume if WR last 10 is 100%, they belong a tier higher
    totalMMR = MMREstimate
    expectedSigmaMMR = 100
    TotalLP = startingLP
    for ii in range(nGames):
        game = Game(TotalLP, expectedSigmaMMR, totalMMR)
        result = game.resolve()

        LPTm.append(LPTm[-1] + result)


    plt.plot(LPTm)


if __name__ == "__main__":
    random.seed(0)
    print(random.gauss(0.0,1.0))
    nRealities = 30
    for nn in range(nRealities):
        run(nGames=500, startingLP=1466, startingLPGain=28, startingLPLoss=21, WRLast10=0.80)

    plt.show()


# <GPLv3_Footer>
################################################################################
#                      Copyright (c) 2024 Nathan Ulmer.
################################################################################
# <\GPLv3_Footer>