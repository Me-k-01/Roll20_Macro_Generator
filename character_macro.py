from roll20_format_lib import formatNested, createTable, createDropdown  
    
class StatBlock :
    """Generate macro to be used in a character sheet, that will automatically fetch the attributes inside the character sheet.

    # Optional arguments : 
    
    comment : bool = Default to True; Decide if you want to have the comments automatically generated inside the macros
    
    name : String = Default to None; If you want to be able to use the mace outside the caracter sheet (in the global macro area for example), 
    you'll have to name it. I don't recommend setting this values to something else than None, as it could break some macros if special character are used in the character name (",", "|", "}"...).
    """
    def __init__(self, name = None, comment=True):
        # Link a specific character to the macro
        if name is not None :
            self.ref_name = name + "|"
        else :
            self.ref_name = ""
        self.comment=comment
        # Special attributes
        self.endu = "Endurance"
        self.dmg = "Damage"
        # Recommended naming schemes of the values on the character sheet :
        # Pascal case
        self.comp_keys = [
            "Physique", "Volonte", "Social", "Intellect", "Perception", "Creation", "Clandestin", "Combat"
        ]
        # I recommend using three letter, full caps to not mistake the stat with something else
        self.stat_keys = [
            "FOR", "CON", "AGI", "DEX", "MEN", "SEN", "DET", "PRE"
        ]
        # Special stat keys, as many letter as needed, full caps
        self.special_stats_keys = [
            "FRUIT", "HAKI_OBS", "HAKI_ARM", "HAKI_ROI"
        ] 
        # Speciality
        self.spe = {
            "Physique":[],
            "Volonte":[],
            "Social":[],
            "Intellect":[],
            "Perception":[],
            "Creation":[],
            "Clandestin":[],
            "Combat":[]
        }
        self.d100 = "d100cf<5cs>96"

    def damageMacro(self, ask_for_bonus=True) :
        """Generate a macro that will calculate the damage threshold. 
        Will query the value of the attack roll and uses the base damage attribute in the character sheet.
        
        # Optional arguments
        ask_for_bonus : bool = Default to True; Does the macro query a damage bonus?
        """

        # return createTable(title="Dégâts pour : " + "?{Jet d'attaque |0} à l'attaque", 
        #     hidden_roll="[[floor([[[[[[[[[[[[[[[[[[?{Jet d'attaque |0}]]-1]]-49]]-1]]-99]]-1]]*0+@{" + self.ref_name + self.dmg + "}]]*2]]/8)]]",
        #     row_labels=[
        #         "$[[2]] ≤ Déf ≤ $[[1]] 🡆",
        #         "$[[4]] ≤ Déf ≤ $[[3]] 🡆",
        #         "Déf ≤ $[[5]] 🡆"
        #     ], row_contents=[
        #         "$[[8]]",
        #         "$[[6]]",
        #         "$[[7]]" 
        #     ]
        # )
        att_precalculation = "[[[[[[[[?{Jet d'attaque |0}]]-1]]-50]]-100]]" 
        fetch_damage = "@{" + self.ref_name + self.dmg + "}"
        dmg_bonus = ""
        if ask_for_bonus :
            dmg_bonus = "+?{Dégâts bonus |0}[Deg bonus]"
        total_precalculation = "[[floor([[[[[["+att_precalculation+"[ATT]*0+"+fetch_damage+"]][Deg base]"+dmg_bonus+"]]*2]]/8)]]"
  
        return createTable(title="Dégâts pour " + "?{Jet d'attaque |0} à l'attaque",  
            hidden_roll = total_precalculation,
            # One row to make it look better. 
            row_labels=[
                "Déf ≤ $[[1]]%NEWLINE%Déf ≤ $[[2]]%NEWLINE%Déf ≤ $[[3]]"
            ], row_contents=[
                "🡆 $[[7]] Dég%NEWLINE%🡆 $[[5]] Dég%NEWLINE%🡆 $[[6]] Dég"
            ]
        ) 

    def getFatigue(self, is_contained=True): 
        """Retrieve the exchaustion penalty.
        
        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """
        # MIN(ENDU, 0)
        macro = "{@{"+self.endu+"}, 0}kl1"
        if is_contained : 
            macro = "[["+macro+"]]"
        if self.comment :
            macro += "[Fatigue]"
        return macro

    def rollInit(self, ask_for_bonus=True): 
        """Macro to calculate the initiative, and to add the currently selected token to the turn order.
        The AGI stat modifier is used in this macro.

        # Optional arguments
        ask_for_bonus : bool = Default to True; Does the macro query a initiative bonus?
        """

        if self.ref_name == "" :
            title = "Initiative"
        else :
            title = "Initiative de " + self.ref_name[:-1]

        init_bonus = ""
        if ask_for_bonus :
            init_bonus = "+?{Initiative bonus |0}[Initiative bonus]"

        return createTable(title=title,
            row_labels=[ "Roll :" ],
            row_contents = [ "[[([[" + self.d100 + "]][d100] + [[(2*" + self.getModStat("AGI", is_contained=False) + ")]][AGI]"+init_bonus+")&{tracker}]]" ]
        ) 

    def getModStat(self, stat_key, is_contained=True): 
        """Calculate the stat modifier from an attributes in the character sheet. 

        # Argument
        comp_key : String = The special competence name.

        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """

        # SI(B25<6;PRODUIT(B25;10);PRODUIT((B25-5)*20+50))
        macro = "{{6-1,-1}>@{" + self.ref_name + stat_key + "}}*((@{" + self.ref_name + stat_key + \
            "}*10)-((@{" + self.ref_name + stat_key + "}-5)*20+50))+((@{" + self.ref_name + stat_key + \
            "}-5)*20+50)"

        if is_contained : 
            macro = "[["+macro+"]]"
        if self.comment :
            macro += "[" + stat_key + "]" 
        return macro

    def getAbilityLimit(self, stat_key, is_contained=True):
        """Calculate the maximum of the roll+modifier that can be made for that ability.
        
        # Argument
        stat_key : String = The stat.

        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """
        # SI(STAT>2;STAT*50;150) <=> MAX(STAT*50, 150)
        macro = "{@{" + self.ref_name + stat_key + "}*50,150}kh1"  
        if is_contained : 
            macro = "[["+macro+"]]"
        if self.comment :
            macro += "[" + stat_key + "_MAX" + "]" 

        return macro

    def getSpecialMod(self, stat_key, is_contained=True):
        """Retrieve a special competence as an attributes inside a character sheet.
        
        # Argument
        comp_key : String = The special competence name.

        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """

        macro = "(20*@{" + self.ref_name + stat_key + "})"

        if is_contained : 
            macro = "[["+macro+"]]"
        if self.comment :
            macro += "[" + stat_key + "]" 

        return macro

    def getComp(self, comp_key, is_contained=True):
        """Retrieve the competence as an attributes inside a character sheet.
        
        # Argument
        comp_key : String = The competence name.

        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """
        macro = "@{"+self.ref_name + comp_key + "}"

        if is_contained : 
            macro = "[["+macro+"]]" 
        if self.comment :
            macro += "[" + comp_key + "]" 

        return macro


    def roll(self, stat_key, comp_key, spe_key=None, is_contained=True, add_optional_bonus=True) :
        """Rolls a stat and limit the maximum possible for the roll.
        
        # Arguments :
        comp_key : String = A competence to roll with.
        stat_key : String = A statistic to roll with.

        # Optional arguments :
        spe_key : String = Default to None; A potential speciality to roll with.
        add_optional_bonus : bool = Default to True; Do the macro prompt the user a bonus to use that will go past the ability limit?
        spe_key : String = Default to None; If a speciality is provided, will make the roll with that speciality.
        """  
        # Modifyer that breaks the limit
        add_to_limit = "+" + self.getFatigue()
        if add_optional_bonus :
            add_to_limit += "+?{Bonus|0}"
            if self.comment :
                add_to_limit += "[Bonus]"

        add_spe = "" 
        if spe_key is not None : 
            assert spe_key in self.spe[comp_key]
            add_spe = "+"+"@{"+spe_key+"}"
            if self.comment :
                add_spe += "["+spe_key+"]"


        macro = "{" + \
            self.d100 + "+" + \
            self.getModStat(stat_key) + "+" + \
            self.getComp(comp_key) + \
            add_spe + \
            "," + "0d0+" + self.getAbilityLimit(stat_key) + \
        "}kl1" + add_to_limit

        if is_contained : 
            macro = "[["+macro+"]]"
        return macro
 
    def linkSpeToComp(self, comp_key, spe_key):
        """Links a speciality to a competence.
        Can accepts a list of competence and a list of speciality too.
        If both are a list, then every comp will receive the same array of competence.

        # Arguments :
        comp_key : String | list[String] = The competence(s) to link the speciality to.
        spe_key : String | list[String] = The speciality that will be linked.
        """
        if isinstance(comp_key, list) :  
            for comp in comp_key :
                if isinstance(spe_key, list) : 
                    for spe in spe_key : 
                        assert spe not in self.spe[comp]
                        self.spe[comp].append(spe)
                else :
                    assert spe_key not in self.spe[comp]
                    self.spe[comp].append(spe_key)
        else :
            if isinstance(spe_key, list) : 
                for spe in spe_key : 
                    assert spe not in self.spe[comp_key]
                    self.spe[comp_key].append(spe)
            else :
                assert spe_key not in self.spe[comp_key]
                self.spe[comp_key].append(spe_key)

    def rollTable(self, comp_key, stat_key, spe_key=None, add_optional_bonus=True) : 
        """Creates a macro that will make the ability roll inside a table.
        
        The roll = MIN(d100 + STAT_MOD + COMP + ?SPE, STAT_MAX) + ?BONUS

        # Arguments :
        comp_key : String = A competence to roll with
        stat_key : String = A statistic to roll with

        # Optional arguments :
        add_optional_bonus : bool = Default to True, Do the macro prompt the user a bonus to use that will go past the ability limit?
        spe_key : String = Default to None; if a speciality is provided, will make the roll with that speciality.
        """
        if spe_key is None :   
            return createTable(
                title         = "Roll de " + stat_key + "-" + comp_key,
                row_labels   = [ "d100 :" ],
                row_contents = [ self.roll(stat_key, comp_key, is_contained=True, add_optional_bonus=add_optional_bonus) ]
            ) 
        else :
            return createTable(
                title         = "Roll de " + stat_key + "-" + comp_key + " : " + spe_key,
                row_labels   = [ "d100 :" ],
                row_contents = [ self.roll(
                    stat_key=stat_key, 
                    comp_key=comp_key, 
                    spe_key=spe_key, 
                    is_contained=True, 
                    add_optional_bonus=add_optional_bonus
                ) ]
            )  


    def queryRollTable(self, comp_key, stat_keys=None, add_optional_bonus=True):
        """Generate a generic macro linked to a competence that asks the user the statistic and speciality to use for that roll.
        
        For this method to use the specialities of the character, you have to specify them first with linkSpeToComp(competence_key, speciality_key)
        
        # Arguments :
        comp_key : String = A competence from which to generate the query.

        # Optional arguments :
        stat_keys : list[String] = Default to None; Restrict the stat to query to a list of stat_key. Can also be used to set an order in the stat query
        add_optional_bonus : bool = Default to True; Does the macro ask at the end a bonus to use that will go past the ability limit?
        """ 

        assert comp_key in self.comp_keys 

        if stat_keys is None : # By default, makes a query that ask for every stats
            stat_keys = self.stat_keys
   
        # First level of nesting : Stat query
        macro = createDropdown(
            title="Stat pour " + comp_key.lower() + " ", 
            labels=[
                stat_key + " (@{"+stat_key+"})" 
                for stat_key in stat_keys 
            ], 
            outputs = [ 
                self.rollTable(comp_key, stat_key)
                if len(self.spe[comp_key]) == 0 else
                # Second level of nesting : Speciality query 
                createDropdown(
                    title="Spé pour " + comp_key.lower() + " ", 
                    labels=["-"] + [
                        spe + " (@{"+spe+"})"
                        for spe in self.spe[comp_key] 
                    ], 
                    outputs = [self.rollTable(comp_key=comp_key, stat_key=stat_key)] + [ 
                        self.rollTable(comp_key=comp_key, stat_key=stat_key, spe_key=spe_key)
                        for spe_key in self.spe[comp_key]
                    ], deeply_nested=True
                )
                for stat_key in stat_keys  
            ]
        )

        return macro
 
if __name__ == "__main__":
    perso = StatBlock(comment=True)  

    ######## Getting the essential
    # Getting the init
    print(perso.rollInit())
    # Getting the damage from a roll (will query the attack roll)
    # print(perso.damageMacro())

    # Single line roll example with MEN-Intellect :
    # print(perso.roll("MEN", "Intellect")) 
    

    ######## Making the competences macro
    # Competences and abilities that can be used:
    # Comp = Physique, Volonte, Social, Intellect, Perception, Creation, Clandestin, Combat
    # STAT = FOR, CON, AGI, DEX, MEN, SEN, DET, PRE

    # Example of adding speciality to the macro of Combat
    # perso.linkSpeToComp("Combat", ["Attaque", "Parade", "Esquive"]) 

    # This will output a query for a combat roll, limited to 3 statistic only 
    # (This macro will automatically use the specialities specified just before)
    # print(perso.queryRollTable("Combat"  , stat_keys = ["DEX", "AGI", "SEN"])) 
 

    # The following macro have their stat_keys ordered to be tailored for each competence macro.
    # print(perso.queryRollTable("Physique"  , stat_keys=["FOR", "CON", "AGI", "DEX", "PRE", "SEN", "MEN", "DET"])) 
    # print(perso.queryRollTable("Volonte"   , stat_keys=["DET", "MEN", "SEN", "FOR", "PRE", "CON", "DEX", "AGI"])) 
    # print(perso.queryRollTable("Social"    , stat_keys=["PRE", "MEN", "SEN", "FOR", "DET", "CON", "DEX", "AGI"])) 
    # print(perso.queryRollTable("Intellect" , stat_keys=["MEN", "PRE", "SEN", "DET", "CON", "FOR", "DEX", "AGI"])) 
    # print(perso.queryRollTable("Perception", stat_keys=["SEN", "PRE", "MEN", "CON", "DET", "FOR", "DEX", "AGI"])) 
    # print(perso.queryRollTable("Creation"  , stat_keys=["MEN", "PRE", "DET", "DEX", "FOR", "SEN", "CON", "AGI"])) 
    # print(perso.queryRollTable("Clandestin", stat_keys=["AGI", "DEX", "PRE", "SEN", "CON", "FOR", "MEN", "DET"]))
    # print(perso.queryRollTable("Combat"    , stat_keys=["DEX", "AGI", "SEN", "FOR", "MEN", "PRE", "CON", "DET"])) 
 


 
 