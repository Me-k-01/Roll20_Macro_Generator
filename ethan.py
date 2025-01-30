from character_macro import StatBlock 
from roll20_format_lib import *
from competence import *
from typing import List, Optional
 
# fill correctly
style_head = 'background-color:#1f1f1f; color:#00ffcf;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:7px;text-decoration:none;'

# style_head_2 =  'background-color:rgba(10, 100, 10, 0.2);height:100%;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:7px;text-decoration:none;'

# transparency
style_head_2 =  'background-color:rgba(10, 100, 10, 0.2);height:100%;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:7px;text-decoration:none;'
 
# url("https://imgsrv.roll20.net/?src=http%3A//www.rw-designer.com/cursor-view/39703.png"), auto

style_blue = 'color:#00ffcf;text-decoration:none;cursor:pointer;'
style_red = 'color:#ff695a;text-decoration:none;cursor:pointer;'

# works
#background-color: #1f1f1f; color: #00ffcf; width: 100% ; display: block ; margin: -5px ; margin-bottom: -4px ; padding: 5px ; padding-top: 7px ; text-decoration: none ; cursor: url("https://imgsrv.roll20.net/?src=http%3A//www.rw-designer.com/cursor-view/39703.png") , auto
# &{template:default} {{name=[fez](#" style="background-color:white; color:red;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:7px;text-decoration:none;pointer:none;cursor:url&#40;https://imgsrv.roll20.net/?src=http%3A//www.rw-designer.com/cursor-view/39703.png&#41;,auto;)}}{{attack=[[1d20]]}}


# style_absolute = "background-color:rgba(10, 100, 10, 0.5);display:block;width:100%;height:100%;position:absolute;pointer-events:none;"
 

# style_head = 'background-color:white; color:red;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:7px;text-decoration:none;cursor:url&#40;http://www.rw-designer.com/cursor-extern.php?id=103989&#41;,auto;'

# text = "&{template:default} {{name=[fez](#" style="background-color:white; color:red;width:100%;display:block;margin:-5px;margin-bottom:-4px;padding:5px;padding-top:10px;text-decoration: none;pointer:none;  cursor:url&#40;https://img1.picmix.com/output/stamp/normal/1/4/0/2/1922041_4c561.gif&#41;, auto;)}}{{attack=[[1d20]]}}"

# style = "color: red ; background-color: white;&::after { content: '###'; color:red;}"
# style = "color: red ; background-color: white;&::after &lbrace content: '###'; color:red;&rbrace;"
 
def style_with_link(text, style, tooltip="") :
    add_tooltip = ""
    if tooltip != "" :
        add_tooltip = 'class="showtip" title = "' + tooltip + '" '
    return  '[' + text + '](#" '+add_tooltip+'style="' + formatNested(style, ["(",")"]) + ')'

# print('&{template:default} {{name=' + style_with_link("fez", style_head) + "}}{{attack=[[1d20]]}}")
# casse et a permis de creer un nouvelle element??
# current = '&{template:default} {{name=[Test](#"width:calc(100%+20px);display:block;margin:-5px;padding:5px;}} {{attack=[[1d20]]}} {{damage=[[2d6]]}}'
 
# text = "&{template:default} {{name=Test}} {{attack=[[1d20]]}} {{damage=[[2d6]]}}"

# print( "&{template:default} {{name="+style_with_link(" t ", style_head)+"Attaque : "+style_with_link("tech", style_head_blue)+"}} {{attack=[[1d20]]}} {{damage=[[2d6]]}}")

# print(style_with_link("byebye", "background:red;transform: perspective(75em) rotateX(18deg);", tooltip="fezfzefzfzefezefef"))

class Perso (StatBlock) :
    def __init__(self, name = None, comment=True) :
        super().__init__(name = name, comment=comment)

        # location of the variables in the sheet 
        self.bonus_init = "Bonus INIT / COMP"
        self.bonus_comp = "Bonus INIT / COMP|MAX"  
        self.bonus_att  = "Bonus ATT / DEG"
        self.bonus_deg  = "Bonus ATT / DEG|MAX"
        self.bonus_prd  = "Bonus PRD / ESQ"
        self.bonus_esq  = "Bonus PRD / ESQ|MAX"   
        self.bonus_eq   = "Charge Katana"

        self.specialization_bonus = {  
            "ATT" : self.bonus_att,
            "DEG" : self.bonus_deg,
            "PRD" : self.bonus_prd,
            "ESQ" : self.bonus_esq
        }

        self.split_dmg_electro = True
 
 
    def roll(self, stat_key, comp_key, spe_key=None, is_contained=True, add_optional_bonus=True) :
        output = super().roll(stat_key, comp_key, spe_key=None, is_contained=False, add_optional_bonus=True)

        # patch function with the campains bonus

        if self.bonus_comp is not None :
            output += "+@{" + self.ref_name+self.bonus_comp + "}[Bonus global COMP]"

        if is_contained : 
            output = "[["+output+"]]"

        return output

    def rollInit(self, ask_for_bonus=True, bonus="", bonus_passif=None, equipement_bonus_multiplier=0): 
        """Macro to calculate the initiative, and to add the currently selected token to the turn order.
        The AGI stat modifier is used in this macro.

        # Optional arguments
        ask_for_bonus : bool = Default to True; Does the macro query a initiative bonus?
        """

        if self.ref_name == "" :
            title = "Initiative"
        else :
            title = "Initiative de " + self.ref_name[:-1]

        add_bonus = "" 

        if self.bonus_init is not None : 
            add_bonus += "+@{"+self.ref_name + self.bonus_init+"}"
            if self.comment : 
                add_bonus += "[Bonus global INI]"

        if ask_for_bonus :
            add_bonus += "+?{Bonus INI |0}"
            if self.comment : 
                add_bonus += "[Bonus INI]"

        if bonus_passif is not None :
            add_bonus += "+" + bonus_passif  
            if self.comment :
                add_bonus += "[Passif]"

        # Bonus of the equipement (katana)
        bonus_eq_label = []
        bonus_eq_bonus = []
        if equipement_bonus_multiplier != 0 : 
            add_bonus += "+[[@{"+self.ref_name+self.bonus_eq+"}*"+str(equipement_bonus_multiplier)+"]]"
            if self.comment :
                add_bonus += "[Katana INIT]"
            bonus_eq_label = ["Charge katana :"]
            bonus_eq_bonus = ["[[@{"+self.ref_name+self.bonus_eq+"}]]"]

        label = bonus_eq_label + [ "🎲 :" ]  

        # Making the roll
        macro = self.d100 
        macro += "+[[2*(" + self.getModStat("AGI", is_contained=False)+")]]" 
        if self.comment : 
            macro += "[AGI * 2]"
        macro += add_bonus


        # contain   
        macro = "[["+macro+"&{tracker}]]" 

        return createTable(title=title,
            row_labels=label,
            row_contents = bonus_eq_bonus + [macro]
        ) 

    def getFatigue(self, is_contained=True): 
        """Retrieve the exchaustion penalty.
        
        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """ 
 
        endu = "@{"+self.ref_name+self.endu+"}"
        endu_cap = "@{"+self.ref_name + self.endu+"|MAX} * 0.75" # 50% ENDU 

        # MIN(ENDU, 50%) + 50%
        macro = "{"+endu+", -"+endu_cap+"}kl1 + " + endu_cap

        if is_contained : 
            macro = "[["+macro+"]]"

        if self.comment :
            macro += "[Fatigue]" 

        return macro
     
 


    def createTechDropdown(self, makeDisplay, techniques_art = [None], techniques_haki = [None]) :  
        """Create a tree of possibility using dropdown.
        
        Params :
        there should always at least be one element in techniques_art and in techniques_haki arrays. None signals that there is not technique"""
        
        art_output  = [] 
        art_labels  = [ '-' if t_art  is None else '(' + t_art.cost  + 'F) ' + t_art.label  for t_art in techniques_art ]
        haki_labels = [ '-' if t_haki is None else '(' + t_haki.cost + 'H) ' + t_haki.label for t_haki in techniques_haki ]
         
        for t_art in techniques_art :
            haki_output = []
            for t_haki in techniques_haki :
                haki_output.append(makeDisplay(t_art, t_haki))
            if len(techniques_haki) > 1 : 
                # Create the haki dropdown, nested in art dropdown
                art_output.append(createDropdown(
                    title         = "HAKI TECH ACTIVE", 
                    labels        = haki_labels,
                    outputs       = haki_output,
                    deeply_nested = True
                )) 
            # If there is only one haki tech
            else :
                # Directly use the only table in the array as the output of the first dropdown
                art_output.append(haki_output[0]) 
        if len(techniques_art) > 1 : 
            # Create the art dropdown
            return createDropdown(
                title   = "ART TECH ACTIVE ",
                labels  = art_labels,
                outputs = art_output
            )
        else :
            # Directly use the only table in the array as the output of the first dropdown
            return art_output[0]
 
    def rollTech(self, 
        roll_type : str,
        roll_type_acronyme : str,  
        comp : str,
        stat : str,
        techniques_art  : List[Competence] = [None],
        techniques_haki : List[Competence] = [None],
        technique_art_passive : Optional[Competence] = None,
        technique_haki_passive : Optional[Competence] = None,
        add_optional_bonus = True,  
        buttons = [],
        add_specialization_bonus = True, 
        equipement_bonus_multiplier : float = 0
    ) : 
        """
        params :
        roll_type = the type of a roll (the title of the roll in the table)
        roll_type_acronyme = the type of a roll abreviated (ESQ | PRD ...)
        techniques_art = the art martial techniques
        techniques_haki = the haki techniques
        comp = the competence used for the roll
        stat = the stat used for the roll
        techniques_art_passive = the art martial passive techniques, if is not conditional, will not prompt the user
        techniques_haki_passive = the haki passive techniques, if is not conditional, will not prompt the user
        add_optional_bonus = Manual prompt bonus
        buttons = buttons added at the end of the table
        add_specialization_bonus = Do we fetch a specialized bonus from the sheet
        """

        add_to_limit = "+" + self.getFatigue() 

        # Add the passif of art martial 
        if technique_art_passive is not None :
            # as a prompt if it's conditional
            if technique_art_passive.conditional :
                add_to_limit += "+?{ART TECH PASSIVE "+roll_type_acronyme+" : "+technique_art_passive.label+"?}"
            # directly if not
            else :
                add_to_limit += "+"+technique_art_passive.bonus

            if self.comment :
                add_to_limit += "[Passif "+technique_art_passive.label+"]"

        # Add the passif of Haki
        if technique_haki_passive is not None :
            # as a prompt if it's conditional
            if techniques_haki_passive.conditional :
                add_to_limit += "+?{HAKI TECH PASSIVE "+roll_type_acronyme+" : "+technique_haki_passive.label+"?}"
            # directly if not
            else :
                add_to_limit += "+"+technique_haki_passive.bonus

            if self.comment :
                add_to_limit += "[Passif "+technique_haki_passive.label+"]"
        
        # Global bonus competence 
        add_to_limit += "+@{" + self.ref_name + self.bonus_comp + "}"  
        if self.comment :
            add_to_limit += "[Bonus global COMP]"

        # Specialized bonus
        if add_specialization_bonus :
            # Fetch a global bonus frol the sheet
            add_to_limit += "+@{" + self.ref_name + self.specialization_bonus[roll_type_acronyme] + "}"
            if self.comment :
                add_to_limit += "[Bonus global "+roll_type_acronyme+"]" 
  
        if add_optional_bonus :
            # bonus punctual 
            add_to_limit += "+?{Bonus "+roll_type_acronyme+"|0}"
            if self.comment :
                add_to_limit += "[Bonus prompt "+roll_type_acronyme+"]"

        # Bonus of the equipement (katana)
        bonus_eq_label = []
        bonus_eq_bonus = []
        if equipement_bonus_multiplier != 0 : 
            add_to_limit += "+[[@{"+self.ref_name+self.bonus_eq+"}*"+str(equipement_bonus_multiplier)+"]]"
            if self.comment :
                add_to_limit += "[Katana"+roll_type_acronyme+"]"
            bonus_eq_label = ["Charge katana :"]
            bonus_eq_bonus = ["[[@{"+self.ref_name+self.bonus_eq+"}]]"]

        # The macro without the active techniques
        macro = "{" + \
            self.d100 + "+" + \
            self.getModStat(stat) + "+" + \
            self.getComp(comp) + \
            "," + "0d0+" + self.getAbilityLimit(stat) + \
        "}kl1" + add_to_limit
 

        # Function to create a table to display the roll
        def createRollDisplay(t_art : Optional[Competence], t_haki : Optional[Competence]) :
            label = bonus_eq_label + [ "🎲 :" ]  
            if len(buttons) > 0 : 
                label.append("🔗 :")


            """Create a table for rolls""" 
            if t_art is None and t_haki is None : 
                return createTable(
                    title        = roll_type,
                    row_labels   = label,
                    row_contents = bonus_eq_bonus + [ "[[" + macro + "]]" ] + buttons
                )
            elif t_art is None : 
                return createTable(
                    title        = roll_type + " : " +\
                        style_with_link('(' + t_haki.cost + 'H) ' + t_haki.label, style_red, t_haki.desc),
                    row_labels   = label,
                    row_contents = bonus_eq_bonus + [ "[[" + macro +\
                        "+" + t_haki.bonus + "[" + t_haki.label + "]" +\
                        "]]" ] + buttons
                )
            elif t_haki is None : 
                return createTable(
                        title        = roll_type + " : " +\
                            style_with_link('(' + t_art.cost + 'F) ' + t_art.label, style_blue, t_art.desc),
                        row_labels   = label,
                        row_contents = bonus_eq_bonus + [ "[[" + macro +\
                            "+" + t_art.bonus + "[" + t_art.label + "]" +\
                            "]]" ] + buttons
                    ) 
            else :
                # Both art martial and haki technique
                return createTable(
                        title        = roll_type + " : " +\
                            style_with_link('(' + t_art.cost + 'F) ' + t_art.label, style_blue, t_art.desc) +\
                            style_with_link('(' + t_haki.cost + 'H) ' + t_haki.label, style_red, t_haki.desc),
                        row_labels   = label,
                        row_contents = bonus_eq_bonus + [ "[[" + macro + 
                            "+" + t_art.bonus + "[" + t_art.label + "]" +\
                            "+" + t_haki.bonus + "[" + t_haki.label + "]" +\
                            "]]" ] + buttons
                    )

        # prompt passif Art
        passif = ""
        if technique_art_passive is not None and technique_art_passive.conditional :
            passif += "?{ART TECH PASSIVE "+roll_type_acronyme+" : "+technique_art_passive.label+"?|" + \
                "Oui," + technique_art_passive.bonus + \
                "|Non,0}+"

        # prompt passif Haki
        if technique_haki_passive is not None and technique_haki_passive.conditional :
            passif += "?{HAKI TECH PASSIVE "+roll_type_acronyme+" : "+technique_haki_passive.label+"?|" + \
                "Oui," + technique_haki_passive.bonus + \
                "|Non,0}+"

        # Combinaison des macro en un dropdown
        return passif + self.createTechDropdown(createRollDisplay, techniques_art, techniques_haki)
 
    def damageTable(self, title, dmg_output, dmg_electro_output, hidden_roll = "") :   
        if self.split_dmg_electro  : 
            return createTable(title=title,
                hidden_roll = hidden_roll, 
                row_labels=["DEF",
                    "🎲 ≤ [[?{Jet d'attaque}-1]] 🡆%NEWLINE%"+\
                    "🎲 ≤ [[?{Jet d'attaque}-50-1]] 🡆%NEWLINE%"+\
                    "🎲 ≤ [[?{Jet d'attaque}-100-1]] 🡆",
                    "⚡  :  "
                ], row_contents=["    DEGATS",
                    "[[round(("+dmg_output+")/4)]] 🗡️ + [[round(("+dmg_electro_output+")/4)]] ⚡%NEWLINE%"+\
                    "[[round(" + dmg_output + ")]] 🗡️ + [[round("+dmg_electro_output+  ")]] ⚡%NEWLINE%"+\
                    "[[round(("+dmg_output+")*2)]] 🗡️ + [[round(("+dmg_electro_output+")*2)]] ⚡",
                    "Passe l'invu"
                ] 
            ) 
        else :  
            return createTable(title=title,     
                hidden_roll = hidden_roll, 
                row_labels=["Défense",
                    "DEF ≤ [[?{Jet d'attaque}-1]]%NEWLINE%"+\
                    "DEF ≤ [[?{Jet d'attaque}-50-1]]%NEWLINE%"+\
                    "DEF ≤ [[?{Jet d'attaque}-100-1]]"
                ], row_contents=["Dégâts",
                    "🡆 [[round(("+dmg_output+"+"+dmg_electro_output+")/4)]] 🗡️%NEWLINE%"+\
                    "🡆 [[round(" + dmg_output+"+"+dmg_electro_output + ")]] 🗡️%NEWLINE%"+\
                    "🡆 [[round(("+dmg_output+"+"+dmg_electro_output+")*2)]] 🗡️"
                ] 
            ) 

    def damageMacro(self,  
        techniques_art  : List[Competence] = [None],
        techniques_haki : List[Competence] = [None],
        technique_art_passive : Optional[Competence] = None,
        technique_haki_passive : Optional[Competence] = None,
        add_optional_bonus = True,
        add_specialization_bonus = True
    ) : 
        """
        params : 
        techniques_art = the art martial techniques
        techniques_haki = the haki techniques 
        techniques_art_passive = the art martial passive techniques, if is not conditional, will not prompt the user
        techniques_haki_passive = the haki passive techniques, if is not conditional, will not prompt the user
        add_optional_bonus = Manual prompt bonus 
        add_specialization_bonus = Do we fetch a specialized bonus from the sheet
        """
        roll_type = "Dégâts"
        roll_type_acronyme = "DEG"
        
        # Two damage output
        dmg_output = "@{" + self.ref_name + self.dmg + "}" # base damage
        dmg_output += "+@{"+self.ref_name+self.bonus_eq+"}*110" # Charge * 110
        dmg_output_electro = ""

        if self.comment : 
            dmg_output += "[Base "+roll_type_acronyme+"]"
         
        # Prompte the user for a damage bonus
        if add_optional_bonus :
            dmg_output += "+?{Dégâts bonus|0}"
            if self.comment : 
                dmg_output += "[Bonus "+roll_type_acronyme+"]"

        # Fetch the global damage bonus from the attribute on the sheet
        if add_specialization_bonus : 
            dmg_output += "+@{"+self.ref_name+self.bonus_deg+"}"
            if self.comment : 
                dmg_output += "[Bonus global "+roll_type_acronyme+"]"

        # Add the passif of art martial 
        if technique_art_passive is not None :
            # as a prompt if it's conditional
            if technique_art_passive.conditional :
                dmg_output_electro += "+?{ART TECH PASSIVE "+roll_type_acronyme+" : "+technique_art_passive.label+"?}"
            # directly if not
            else :
                dmg_output_electro += "+"+technique_art_passive.bonus

            if self.comment :
                dmg_output_electro += "[Passif "+technique_art_passive.label+"]"

        # Add the passif of Haki
        if technique_haki_passive is not None :
            # as a prompt if it's conditional
            if techniques_haki_passive.conditional :
                dmg_output_electro += "+?{HAKI TECH PASSIVE "+roll_type_acronyme+" : "+technique_haki_passive.label+"?}"
            # directly if not
            else :
                dmg_output_electro += "+"+technique_haki_passive.bonus

            if self.comment :
                dmg_output_electro += "[Passif "+technique_haki_passive.label+"]"

        # remove the first plus sign from the second damage type
        if len(dmg_output_electro) > 0 and dmg_output_electro[0] == '+' : 
            dmg_output_electro = dmg_output_electro[1:]
 

        # Function to create a table to display the roll
        def createDamageDisplay(t_art : Optional[Competence], t_haki : Optional[Competence]) :
            if t_art is None and t_haki is None : 
                return self.damageTable(
                    title              = "Dégâts", 
                    dmg_output         = dmg_output,
                    dmg_electro_output = dmg_output_electro
                )
            elif t_art is None : 
                return self.damageTable(
                    title              = "Dégâts : " +\
                        style_with_link('(' + t_haki.cost + 'H) ' + t_haki.label, style_red, t_haki.desc), 
                    dmg_output         = dmg_output,
                    dmg_electro_output = dmg_output_electro +\
                        "+" + t_haki.bonus + "[" + t_haki.label + "]"
                ) 
            elif t_haki is None : 
                return self.damageTable(
                    title              = "Dégâts : " +\
                        style_with_link('(' + t_art.cost + 'F) ' + t_art.label, style_blue, t_art.desc),
                    dmg_output         = dmg_output,
                    dmg_electro_output = dmg_output_electro +\
                        "+" + t_art.bonus + "[" + t_art.label + "]"
                )  
            else : 
                # Both art martial and haki technique
                return self.damageTable(
                    title              = "Dégâts : " +\
                        style_with_link('(' + t_art.cost + 'F) ' + t_art.label, style_blue, t_art.desc) +\
                        ", " + style_with_link('(' + t_haki.cost + 'H) ' + t_haki.label, style_red, t_haki.desc),
                    dmg_output         = dmg_output,
                    dmg_electro_output = dmg_output_electro +\
                        "+" + t_art.bonus  + "[" + t_art.label + "]" +\
                        "+" + t_haki.bonus + "[" + t_haki.label + "]"
                )    

        # prompt passif Art
        passif = ""
        if technique_art_passive is not None and technique_art_passive.conditional :
            passif += "?{ART TECH PASSIVE "+roll_type_acronyme+" : "+technique_art_passive.label+"?|" + \
                "Oui," + technique_art_passive.bonus + \
                "|Non,0}+"

        # prompt passif Haki
        if technique_haki_passive is not None and technique_haki_passive.conditional :
            passif += "?{HAKI TECH PASSIVE "+roll_type_acronyme+" : "+technique_haki_passive.label+"?|" + \
                "Oui," + technique_haki_passive.bonus + \
                "|Non,0}+"

        # Combinaison des macro en un dropdown
        return "?{Jet d'attaque}" + passif + self.createTechDropdown(createDamageDisplay, techniques_art, techniques_haki)
 

perso = Perso(name="Ethan D. Flow",comment=True)
perso.linkSpeToComp("Intellect", ["Mysticisme"])

##### INIT
print(perso.rollInit( 
    ask_for_bonus = True, 
    bonus_passif  = getTechBonus(bonus_type=BonusTypes.INIT, level=3, cond=1, is_passive=True, is_contained=True), 
    equipement_bonus_multiplier = 110
))

# # ## ATTAQUE
# print(perso.rollTech(
#     roll_type = "Attaque", roll_type_acronyme = "ATT", comp = "Combat", stat = "DEX",
#     techniques_art  = [ 
#         None,
#         Competence( "Tactique de meute", 
#             getTechBonus(bonus_type=BonusTypes.ATT, level=1, cond=1.5), 
#             cost = 5,
#             conditional = True,
#             desc="Si une créature allié capable de se battre est au CaC de la cible, Ethan obtient un bonus à l'attaque."
#         ),
#         Competence( "Tactique de meute", 
#             getTechBonus(bonus_type=BonusTypes.ATT, level=4, cond=1.5), 
#             cost = 20,
#             conditional = True,
#             desc="Si une créature allié capable de se battre est au CaC de la cible, Ethan obtient un bonus à l'attaque."
#         ),
#         Competence( "Croc de l'ombre", 
#             getTechBonus(bonus_type=BonusTypes.ATT, level=1, cond=2), 
#             cost = 5,
#             conditional = True,
#             desc="S'il est caché d'une cible, il peut sortir de sa cachette pour attaquer la cible dans son dos, et beneficier d'un bonus d'attaque contre elle."
#         ),
#         Competence( "Croc de l'ombre", 
#             getTechBonus(bonus_type=BonusTypes.ATT, level=4, cond=2), 
#             cost = 20,
#             conditional = True,
#             desc="S'il est caché d'une cible, il peut sortir de sa cachette pour attaquer la cible dans son dos, et beneficier d'un bonus d'attaque contre elle."
#         ) 
#     ],
#     technique_art_passive = Competence( "Tactique de meute", 
#             getTechBonus(bonus_type=BonusTypes.ATT, level=3, cond=1.5, is_passive=True),  
#             conditional = True,
#             desc="Si une créature allié capable de se battre est au CaC de la cible, Ethan obtient un bonus à l'attaque."
#         ),
#     equipement_bonus_multiplier = 44
#     # buttons = ["[s](~Ethan D. Flow|DAMAGE-SPLIT-2)"]
# ))

 
## PARADE
# print(perso.rollTech(
#     roll_type = "Parade", roll_type_acronyme = "PRD", comp = "Combat", stat = "DEX", 
#     equipement_bonus_multiplier = 44  
# ))

 
 
## ESQUIVE
# print(perso.rollTech(
#     roll_type = "Esquive", roll_type_acronyme = "ESQ", comp = "Combat", stat = "AGI", 
#     equipement_bonus_multiplier = 0,
#     techniques_art  = [ 
#         None,
#         Competence("Evasion fulgurante",
#             getTechBonus(bonus_type=BonusTypes.DEF, level=1, cond=1),
#             cost = 5,
#             conditional = True,
#             desc= "Ethan electrise ses jambes pour etre capable d'esquiver plus rapidement. Il gagne ainsi un bonus à son jet d'esquive."
#         ),
#         Competence("Evasion fulgurante",
#             getTechBonus(bonus_type=BonusTypes.DEF, level=4, cond=1),
#             cost = 20,
#             conditional = True,
#             desc= "Ethan electrise ses jambes pour etre capable d'esquiver plus rapidement. Il gagne ainsi un bonus à son jet d'esquive."
#         ),
#         Competence("Evasion polarisante",
#             getTechBonus(bonus_type=BonusTypes.DEF, level=4, cond=2),
#             cost = 20,
#             conditional = True,
#             desc= "En reaction à une attaque, Ethan peut decharger son electro pour se magnetiser afin de générer une puissante force de repulsion qui lui confère un bonus à son l'esquive. Après avoir décharger son electro de la sorte, Ethan ne peut plus utiliser son electro jusqu'à la fin de son prochain tour."
#         ) 
#     ]
# ))

## DISCRETION
# print(perso.rollTech(
#     roll_type = "Discretion", roll_type_acronyme = "COMP", comp = "Clandestin", stat = "AGI",
#     techniques_art  = [ 
#         None,
#         Competence("Furtivité du loup",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=1, cond=1),
#             cost = 5,
#             conditional = False,
#             desc= "Se sert de ses instinct de loup pour savoir comment se cacher efficacement de ses proies. Il gagne ainsi un bonus à son jet de discrétion pour se cacher."
#         ),
#         Competence("Furtivité du loup",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=4, cond=1),
#             cost = 20,
#             conditional = False,
#             desc= "Se sert de ses instinct de loup pour savoir comment se cacher efficacement de ses proies. Il gagne ainsi un bonus à son jet de discrétion pour se cacher."
#         ),
#         Competence("Furtivité du loup ténébreux",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=1, cond=1.5),
#             cost = 5,
#             conditional = True,
#             desc= "Se sert de ses instinct de loup pour savoir comment se cacher efficacement de ses proies. Il gagne ainsi un bonus à son jet de discrétion pour se cacher lorsque l'endroit ou il se cache est plongé dans le noir."
#         ),
#         Competence("Furtivité du loup ténébreux",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=4, cond=1.5),
#             cost = 20,
#             conditional = True,
#             desc= "Se sert de ses instinct de loup pour savoir comment se cacher efficacement de ses proies. Il gagne ainsi un bonus à son jet de discrétion pour se cacher lorsque l'endroit ou il se cache est plongé dans le noir."
#         )
#     ],
#     add_specialization_bonus = False, # No bonus in the sheet for that
#     technique_art_passive = Competence("Furtivité du loup",
#         getTechBonus(bonus_type=BonusTypes.COMP, level=3, cond=1, is_passive=True),
#         cost = 5,
#         conditional = False,
#         desc= "Se sert de ses instinct de loup pour savoir comment se cacher efficacement de ses proies. Il gagne ainsi un bonus à son jet de discrétion pour se cacher."
#     )  
# ))


## Perception
# print(perso.rollTech(
#     roll_type = "Perception", roll_type_acronyme = "COMP", comp = "Perception", stat = "SEN",
#     techniques_art  = [ 
#         None,
#         Competence("Perception alpha",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=1, cond=1.25),
#             cost = 5,
#             conditional = True,
#             desc= "Ethan amplifie son ouîe en canalysant l'electro dans son systeme nerveux. Par conséquent il obtient un bonus pour les jets de compétences qui peuvent se resoudre au travers avec l'ouîe."
#         ),
#         Competence("Perception alpha",
#             getTechBonus(bonus_type=BonusTypes.COMP, level=4, cond=1.25),
#             cost = 20,
#             conditional = True,
#             desc= "Ethan amplifie son ouîe en canalysant l'electro dans son systeme nerveux. Par conséquent il obtient un bonus pour les jets de compétences qui peuvent se resoudre au travers avec l'ouîe."
#         ),
#     ],
#     add_specialization_bonus = False, # No bonus in the sheet for that
#     technique_art_passive = Competence("Perception alpha",
#         getTechBonus(bonus_type=BonusTypes.COMP, level=3, cond=1.25, is_passive=True),
#         conditional = True,
#         desc = "Ethan amplifie son ouîe en canalysant l'electro dans son systeme nerveux. Par conséquent il obtient un bonus pour les jets de compétences qui peuvent se resoudre au travers avec l'ouîe."
#     )  
# ))

 
# perso.split_dmg_electro = False
dmg = perso.damageMacro(
    techniques_art = [
        None,
        Competence("Foudroiement sournoi", 
            getTechBonus(bonus_type=BonusTypes.DEG, level=1, cond=1.75),
            cost = 5,
            conditional = True,
            desc="S'il est caché face a un ennemi ou qu'il réussit une tactique de feinte face a lui, Ethan peut lors de son attaque mieux viser avec son electro pour foudroyer le cœur de la cible. Il gagne par conséquent un bonus à ses dégats lors de l'attaque."
        ),
        Competence("Foudroiement sournoi", 
            getTechBonus(bonus_type=BonusTypes.DEG, level=4, cond=1.75),
            cost = 20,
            conditional = True,
            desc="S'il est caché face a un ennemi ou qu'il réussit une tactique de feinte face a lui, Ethan peut lors de son attaque mieux viser avec son electro pour foudroyer le cœur de la cible. Il gagne par conséquent un bonus à ses dégats lors de l'attaque."
        ), 
        Competence("Instinct carnacier", 
            getTechBonus(bonus_type=BonusTypes.DEG, level=1, cond=1.5),
            cost = 5,
            desc = "Ethan reveil ses instincts animals pour savoir comment achever efficacement les proies blessés. Si sa cible est un créature vivante et que celle-ci est ensanglanté, il peut se servir de son sang pour mieux conduire son electro, et gagne ainsi un bonus de dégâts contre elle."
        ),
        Competence("Instinct carnacier", 
            getTechBonus(bonus_type=BonusTypes.DEG, level=4, cond=1.5),
            cost = 20,
            desc = "Ethan reveil ses instincts animals pour savoir comment achever efficacement les proies blessés. Si sa cible est un créature vivante et que celle-ci est ensanglanté, il peut se servir de son sang pour mieux conduire son electro, et gagne ainsi un bonus de dégâts contre elle."
        ),  
    ],
    technique_art_passive = Competence("Foudroiement sournoi", 
            getTechBonus(bonus_type=BonusTypes.DEG, level=3, cond=1.75, is_passive=True),
            conditional = True,
            desc="S'il est caché face a un ennemi ou qu'il réussit une tactique de feinte face a lui, Ethan peut lors de son attaque mieux viser avec son electro pour foudroyer le cœur de la cible. Il gagne par conséquent un bonus à ses dégats lors de l'attaque."
        ),  
    techniques_haki = [ 
        Competence("Revetement rouge", 
            "[[@{"+perso.ref_name+"H_ARM}*20*3]]",
            cost=12,
            desc = "Cette variante offensive du haki de l'armement est plus puissant."
        ),
        Competence("Revetement", 
            "[[@{"+perso.ref_name+"H_ARM}*20*0.75]]",
            cost=5
        ), 
        None,
        Competence("Flux * 10 ", 
            "[[@{"+perso.ref_name+"H_ARM}*20*3 * 10]]",
            cost=60
        ), 
    ] 
)
dmg = formatNested(dmg, char_to_format=["}", "|", ","])  
# print(dmg)

# print(perso.queryRollTable("Physique"  , stat_keys=["FOR", "CON", "AGI", "DEX", "PRE", "SEN", "MEN", "DET"])) 
# print(perso.queryRollTable("Volonte"   , stat_keys=["DET", "MEN", "SEN", "FOR", "PRE", "CON", "DEX", "AGI"])) 
# print(perso.queryRollTable("Social"    , stat_keys=["PRE", "MEN", "SEN", "FOR", "DET", "CON", "DEX", "AGI"])) 
# print(perso.queryRollTable("Intellect" , stat_keys=["MEN", "PRE", "SEN", "DET", "CON", "FOR", "DEX", "AGI"])) 
# print(perso.queryRollTable("Perception", stat_keys=["SEN", "PRE", "MEN", "CON", "DET", "FOR", "DEX", "AGI"])) 
# print(perso.queryRollTable("Creation"  , stat_keys=["MEN", "PRE", "DET", "DEX", "FOR", "SEN", "CON", "AGI"])) 
# print(perso.queryRollTable("Clandestin", stat_keys=["AGI", "DEX", "PRE", "SEN", "CON", "FOR", "MEN", "DET"]))
# print(perso.queryRollTable("Combat"    , stat_keys=["DEX", "AGI", "SEN", "FOR", "MEN", "PRE", "CON", "DET"]))  


# 352 ATT / PRD / ESQ
# 880 vitesse 880 init
# 128 TOUT EXEPT INIT

# Bonus manitas, bouffe