import re

######## Global variables
replacable_char = {
    "&" : "&amp;", #"&#38;",
    # "#" : "&#35;",

    "," : "&#44;",
    "|" : "&#124;",
    "{" : "&lbrace;",   # "&#123;",
    "}" : "&rbrace;",   # "&#125;", 
    "space" : "&nbsp;", # "&#160;",
    "=" : "&#61;",
    "_" : "&#95;",
    "(" : "&#40;",
    ")" : "&#41;",
    "[" : "&lbrack;",   # "&#91;",
    "]" : "&rbrack;",   # "&#93;",
    "<" : "&lt;",       # "&#60;",
    ">" : "&gt;",       # "&#62;",
    "`" : "&#96;",
    "*" : "&#42;",
    "!" : "&#33;",
    '"' : "&#34;",
    "-" : "&#45;",
    "@" : "&#64;"
}

######## Functions
def createTable(title, row_labels, row_contents) :
    """Generate a table from a dictionnary.
    
    # Arguments 
    title : String = The title of the table
    row_labels : list[String] = The left side of the table
    row_contents : list[String] = The right side of the table
    """
    assert len(row_labels) == len(row_contents)

    output_table = "&{template:default} {{name=" + title + "}}"
    for i in range(len(row_labels)) :
        output_table += "{{" + row_labels[i] + "=" + row_contents[i] + "}}"

    return output_table

def createSelectable(title, labels, outputs, do_format_nested=True, deeply_nested=False):
    """Create a selectable macro. If you have multiple selectable, you'll have to use different title for each one of them,
    because roll20 will automatically parse the values of the first query to the second, if they have the same name.
    
    # Arguments 
    title : String = The title of the query (usually a question)
    row_labels : list[String] = The labels listed inside the dropdown of the query
    outputs : list[String] = The query outputs

    # Optional arguments 
    do_format_nested : bool = Default to True; will automatically format the problematic character inside the query.
    """
    char_to_format = ["}", "|", ","] 
    if do_format_nested and deeply_nested :
        char_to_format.append("&")
    
    select_macro = "?{" + formatNested(title, char_to_format=char_to_format) + "|" 
    assert len(labels) == len(outputs)
 

    for i, label in enumerate(labels): 
        if do_format_nested :
            select_macro += formatNested(label, char_to_format=char_to_format) + "," 
            select_macro += formatNested(outputs[i], char_to_format=char_to_format)
        else : 
            select_macro += label + ","
            select_macro += outputs[i]

        if i != len(labels)-1:
            select_macro += "|"

    select_macro += "}"
    return select_macro


def customReplace(match, char_to_format):
    global replacable_char
    # Remplacer les caractères seulement si le match n'est pas une portion protégée
    word = match.group(0)
    if re.match(r'@{[^}]*}|%{[^}]*}|#[ ]* ', word):
        return word  # Ne pas remplacer dans ces cas
    else:
        for c in char_to_format:
            word = word.replace(c, replacable_char[c])
        return word

def formatNested(text, char_to_format=None):
    global replacable_char
    """Format a macro to be nested inside another macro"""


    if char_to_format is None :
        char_to_format = list(replacable_char.keys())
    else :
        char_to_format = char_to_format.copy()


    # Construire une regex qui capture tous les caractères spécifiés
    regex_replacable_char = ''.join(re.escape(k) for k in replacable_char.keys())
    pattern = re.compile(rf'@{{[^}}]*}}|%{{[^}}]*}}|#[ ]* |[{regex_replacable_char}]|[^@%#{"".join(re.escape(c) for c in regex_replacable_char)}]+')
    
    # Utiliser re.sub avec une fonction de remplacement personnalisée
    return pattern.sub(lambda m : customReplace(m, char_to_format), text) 

if __name__ == "__main__":
    input_text = "Here is &#a  &#96;e test @{not,replaced} and %{also,not,replaced} #bu#t # this# #e ||[][{}] and also @this should be replaced"
    # input_text = "Here is &#96a,a"
    result = formatNested(input_text)
    print(result)  # Doit afficher &#124;
 
    # Exemple d'utilisation 
    input_text = "Here is a te,st, @{not,replaced} and %{also,not,replaced} but this ||[][{}],@ should be replaced"
    result = formatNested(input_text, char_to_format=["]"])
    print(result) 