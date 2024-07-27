from roll20_format_lib import formatNested, createTable, createDropdown  
from character_macro import StatBlock

class TransfoStatBlock(StatBlock) : 

    """The macro will be additionned to another character sheet (the result of every dice will be the addition of the two section).
    Will use the Endurance in the new transformation character sheet

    # Arguments

    name : String = The name of the character sheet that will be used as a base stat block for the transformation

    # Optional arguments
    
    comment : bool = Default to True; Decide if you want to have the comments automatically generated inside the macros 
    """
    def __init__(self, original_character_name, comment=True):
        super().__init__(comment=comment)
        # Link a specific character to the macro
        self.original_character_name = original_character_name
        self.original_character_ref = original_character_name + "|"  

    def damageMacro(self) :
        """Generate a macro that will calculate the damage threshold. 
        Will query the value of the attack roll and uses the base damage attribute in the character sheet."""
 
        return createTable(title="Dégâts pour : " + "?{Jet d'attaque |0} à l'attaque", 
            hidden_roll="[[floor([[[[[[[[[[[[[[[[[[?{Jet d'attaque |0}]]-1]]-49]]-1]]-99]]-1]]*0+@{" +\
                self.original_character_ref + self.dmg + "}+@{" + self.dmg + "}]]*2]]/8)]]",
            # One row to make it look better. 
            row_labels=[
                "$[[2]] ≤ Déf ≤ $[[1]]%NEWLINE%$[[4]] ≤ Déf ≤ $[[3]]%NEWLINE%Déf ≤ $[[5]]"
            ], row_contents=[
                "🡆 $[[8]] Dég%NEWLINE%🡆 $[[6]] Dég%NEWLINE%🡆 $[[7]] Dég"
            ]
        )  

    def getInit(self): 
        """Macro to calculate the initiative, and to add the currently selected token to the turn order.
        The AGI stat modifier is used in this macro.""" 

        return createTable(
            title        = "Initiative de " + self.original_character_name,
            row_labels   = [ "Roll :" ],
            row_contents = [ "[[" + self.d100 + " + (2*" + self.getModStat("AGI", is_contained=False) + ")[Init]&{tracker}]]" ]
        ) 

    def getModStat(self, stat_key, is_contained=True): 
        """Calculate the stat modifier from an attributes in the character sheet. 

        # Argument
        comp_key : String = The special competence name.

        # Optional argument
        is_contained : bool = Default to True; Is the macro self contained such as : [[#macro]]
        """
        # stat becomes TF_STAT + BASE_STAT
        attrib_ref = "(@{" + stat_key + "}+@{" + self.original_character_ref + stat_key + "})"
        attrib_ref_cond = "[[@{" + stat_key + "}+@{" + self.original_character_ref + stat_key + "}]]" # for conditional

        # SI (STAT<6) ALORS STAT*10 SINON (STAT-5)*20+50) 
        # with [[{{x,something-less-than-A}>A}*(T-F) + F]] we get
        # [[{{6-1,something-less-than-STAT}>STAT}*(STAT*10-(STAT-5)*20+50) + (STAT-5)*20+50]]

        macro = "{{6-1,-1}>" + attrib_ref_cond + "}*((" + attrib_ref +\
            "*10)-((" + attrib_ref + "-5)*20+50))+((" + attrib_ref + \
            "-5)*20+50)"

        if is_contained : 
            macro = "[[" + macro + "]]"
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
        attrib_ref = "(@{" + stat_key + "}+@{" + self.original_character_ref + stat_key + "})"
        # SI(STAT>2;STAT*50;150) <=> MAX(STAT*50, 150)
        macro = "{" + attrib_ref + "*50,150}kh1"  
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

        attrib_ref = "(@{" + stat_key + "}+@{" + self.original_character_ref + stat_key + "})"
        macro = "(20*" + attrib_ref + ")"

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
        macro = "(@{" + comp_key + "}+@{" + self.original_character_ref + comp_key + "})"

        if is_contained : 
            macro = "[["+macro+"]]" 
        if self.comment :
            macro += "[" + comp_key + "]" 

        return macro 
   
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
                stat_key + " (@{" + stat_key + "}+@{" + self.original_character_ref + stat_key + "})"
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
    perso_tf = TransfoStatBlock("Elneir") # The zoan can gain stat and competence boost

    ######## Getting the essential
    # Getting the init
    # print(perso_tf.getInit())
    # Getting the damage from a roll (will query the attack roll)
    # print(perso_tf.damageMacro())

    # Single line roll example with MEN-Intellect :
    # print(perso_tf.roll("MEN", "Intellect")) 
    

    ######## Making the competences macro
    # Competences and abilities that can be used:
    # Comp = Physique, Volonte, Social, Intellect, Perception, Creation, Clandestin, Combat
    # STAT = FOR, CON, AGI, DEX, MEN, SEN, DET, PRE

    # Example of adding speciality to the macro of Combat
    perso_tf.linkSpeToComp("Combat", ["Attaque", "Parade", "Esquive"]) 

    # This will output a query for a combat roll, limited to 3 statistic only 
    # (This macro will automatically use the specialities specified just before)
    print(perso_tf.queryRollTable("Combat"  , stat_keys = ["DEX", "AGI", "SEN"])) 
 
    # The following macro have their stat_keys ordered to be tailored for each competence macro.
    # print(perso_tf.queryRollTable("Physique"  , stat_keys=["FOR", "CON", "AGI", "DEX", "PRE", "SEN", "MEN", "DET"])) 
    # print(perso_tf.queryRollTable("Volonte"   , stat_keys=["DET", "MEN", "SEN", "FOR", "PRE", "CON", "DEX", "AGI"])) 
    # print(perso_tf.queryRollTable("Social"    , stat_keys=["PRE", "MEN", "SEN", "FOR", "DET", "CON", "DEX", "AGI"])) 
    # print(perso_tf.queryRollTable("Intellect" , stat_keys=["MEN", "PRE", "SEN", "DET", "CON", "FOR", "DEX", "AGI"])) 
    # print(perso_tf.queryRollTable("Perception", stat_keys=["SEN", "PRE", "MEN", "CON", "DET", "FOR", "DEX", "AGI"])) 
    # print(perso_tf.queryRollTable("Creation"  , stat_keys=["MEN", "PRE", "DET", "DEX", "FOR", "SEN", "CON", "AGI"])) 
    # print(perso_tf.queryRollTable("Clandestin", stat_keys=["AGI", "DEX", "PRE", "SEN", "CON", "FOR", "MEN", "DET"]))
    # print(perso_tf.queryRollTable("Combat"    , stat_keys=["DEX", "AGI", "SEN", "FOR", "MEN", "PRE", "CON", "DET"])) 
 


 
 