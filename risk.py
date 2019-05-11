import random
import itertools
from enum import Enum

class RollResult(Enum):
    Defender = 0
    Attacker = 1
    Tie = 2

class DieComparison(Enum):
    Higher = 1
    Equal = 0
    Lower = -1


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    return itertools.starmap(func, itertools.repeat(args, times))


#
# Returns -1, 0, 1 depending on if attacker roll is above, equal to, or below defender roll.
#
def compareDice(dice):
    attacker, defender = dice
    if attacker > defender:
        return DieComparison.Higher
    elif attacker < defender:
        return DieComparison.Lower
    return DieComparison.Equal


#
# @param attackerArmies The initial number of armies for the attacker
# @param attackUntil Keep attacking until the attacker's armies drops at or below this number.
# @param defenderArmies The initial number of armies for the defender
# @param defendUntil Keep attacking until the defender's armies drops at or below this number
# @param ruleset The set of rules that describe how the simulation should run
#   {
#       attackerDice: int           - Maximum amount of dice attacker may use
#       attackerDieSize: Tuple      - Describes (min, max) faces of the attacker die
#       minArmiesForAttack: int     - Minimum number of armies attacker must have to use at least 1 die.
#       defenderDice: int           - Maximum amount of dice defender may use
#       defenderDieSize: Tuple      - Describes (min, max) faces of the defender die
#       minArmiesForDefend: int     - Minimum number of armies defender must have to use at least 1 die.
#       tieBehavior: RollResult     - Describes how to handle a tie on a die roll. 0 == defender wins, 1 == attacker wins, 2 == nobody wins
#   }
def run_simulation(attackerArmies: int, attackUntil: int, defenderArmies: int, defendUntil: int, ruleset: dict):
    # Roll the supplied die. Die has a min and max face value
    roll = lambda dieType: random.randint(dieType[0], dieType[1])

    # Setup the function to compare dice. Comparison is from attacker's point of view.
    #
    # Default behavior is highest roll wins, defender wins on ties.
    rollResult = {
        DieComparison.Higher: RollResult.Attacker,
        DieComparison.Lower: RollResult.Defender,
        DieComparison.Equal: ruleset['tieBehavior']
    }

    # Keep simulating while both the attacker and defenders have armies above the 
    while attackerArmies > ruleset['minArmiesForAttack'] and attackerArmies > attackUntil and defenderArmies > ruleset['minArmiesForDefend'] and defenderArmies > defendUntil:
        # generate attacker dice
        numAttackerDice = attackerArmies - ruleset['minArmiesForAttack']
        attackerDice = repeatfunc(lambda: ruleset['attackerDieSize'], min(numAttackerDice, ruleset['attackerDice']))

        # generate defender dice
        numDefenderDice = defenderArmies - ruleset['minArmiesForDefend']
        defenderDice = repeatfunc(lambda: ruleset['defenderDieSize'], min(numDefenderDice, ruleset['defenderDice']))

        # for both attackers and defenders:
        #   [dieType, ...] => [roll, ...]
        # then sort and zip them together for easy comparison
        # then convert the zipped die rolls into booleans (True if attacker won)
        rolls =                                             \
            map(                                            \
                lambda result: rollResult[compareDice(result)], \
                zip(                                        \
                    sorted(                                 \
                        map(roll, attackerDice),            \
                        reverse=True),                      \
                    sorted(                                 \
                        map(roll, defenderDice),            \
                        reverse=True)))

        # Count the wins and losses
        winRolls, lossRolls = itertools.tee(rolls)
        wins = len(list(filter(lambda x: x == RollResult.Attacker, winRolls)))
        losses = len(list(filter(lambda x: x == RollResult.Defender, lossRolls)))
        
        # update simulation
        attackerArmies -= losses
        defenderArmies -= wins
    print(f"attackerArmies: {attackerArmies}\ndefenderArmies: {defenderArmies}")

if __name__ == "__main__":
    ruleset = {}
    ruleset['attackerDice'] = 3
    ruleset['attackerDieSize'] = (1,6)
    ruleset['minArmiesForAttack'] = 1
    ruleset['defenderDice'] = 2
    ruleset['defenderDieSize'] = (1,6)
    ruleset['minArmiesForDefend'] = 0
    ruleset['tieBehavior'] = RollResult.Defender

    run_simulation(30, 0, 30, 0, ruleset)
