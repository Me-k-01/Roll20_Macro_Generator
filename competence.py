
from enum import Enum

class BonusTypes(float, Enum):
    ATT = 0.2
    DEF = 0.2

    INVU = 1

    COMP = 0.5 
    DEG = 0.5 
    INIT = 0.5 
    DEP = 0.5 
    DIST = 0.5 

    ZONE = 0.025  


def getTechBonus(bonus_type : BonusTypes, level : int, cond : float = 1, is_passive = False, is_contained=True) : 
    """Calculate the tech bonus for a martial art or a fruit

    bonus_type : Either BonusTypes
    level  : Either 1, 2, 3, 4,
    cond : Either 1, 1.25, 1.5, 2, 3, 4,
    is_passive : either true or false""" 
    bonus = str(bonus_type.value) +"*" + str(cond * 20 * level)
    if is_passive : 
        bonus += "*0.5"
    
    output = "round("+str(bonus) + "*@{ART})"

    if is_contained : 
        output = "[["+output+"]]"

    return output

class Competence : 
    def __init__(self, label : str, bonus :str, cost : int = 0, conditional = False, link = None, desc = '') : 
        self.label = label
        self.cost = str(cost)
        self.link = link
        self.conditional = conditional
        self.bonus = bonus
        self.desc = desc
    
    def getTitle(self) :
        return '(' + self.cost + ') ' + self.label
     