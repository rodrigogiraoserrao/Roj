import sys

grammar_name = sys.argv[1]

op_wrapper = """<span style="color:#0033cc">'{}'</span>"""
lhs_coloring = """<span style="color:#009900">{}</span>"""

with open(grammar_name, "r") as f:
    contents = f.read()
    
contents = contents.replace("\n\n", "\n_\n")
contents = contents.split("\n")
    
styling = """
<style>
    p, br {
        line-height: 30%;
    }
</style>
"""

def get_blue(line):
    if "'" in line:
        # intense index handling
        # cuts a string of the form abc'de'fgh into
        # head = abc, rest = de'fgh, mid = de, tail = fgh
        head = line[:line.index("'")]
        rest = line[len(head)+1:]
        mid = rest[:rest.index("'")]
        tail = rest[len(mid)+1:]
        
        tail = get_blue(tail)
        return head + op_wrapper.format(mid) + tail
    else:
        return line
    
with open("grammar.html", "w") as f:
    f.write("<html>\n<head>\n{}\n</head>\n<body>\n".format(styling))
    f.write("<h1>" + contents[0] + "</h1>\n")
    
    for line in contents[1:]:
        # mark the blue stuff
        line = get_blue(line)
        if ":" in line:
            idx = line.index(":")
            line = lhs_coloring.format(line[:idx]) + line[idx:]
        if line != "_":
            f.write("<p>{}</p>\n".format(line.strip()))
        else:
            f.write("<br />\n")
            
    f.write("</body>\n</html>")