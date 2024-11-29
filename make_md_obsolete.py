from xml.etree import cElementTree as ElementTree
from sys import argv as initialization_arguments
import os
import bbcode


def table_of_members(members:ElementTree.Element) -> str:
    table = "|Type|Name|Default Value|\n| - | - | - |\n"
    for m in members:
        try:
            a = m.attrib
            if not 'default' in a:
                a['default'] = " "
            table += '|'+a['type']+'|'+a['name']+'|'+a['default']+"|\n"
        except Exception as error:
            print("Error while interpretting members: ",error)
            table += "| |Invalid member| |\n"
    return table

def decode_method(m:ElementTree.Element) -> tuple[str,str]:
    return_type = ""
    name = m.attrib["name"] + "("
    params = {}

    for e in m:
        try:
            match e.tag:
                case "return":
                    return_type = e.attrib["type"]
                case "param":
                    params[e.attrib["index"]] = e.attrib
        except:
            continue

    keys = list(params.keys())
    keys.sort()
    n = len(keys)
    for i in range(n):
        try:
            if i != 0:
                name += ", "
            name += params[keys[i]]["type"] + " " + params[keys[i]]["name"]
            try:
                name += "=" + params[keys[i]]["default"]
            except:
                pass
        except:
            continue
    name += ")"

    return return_type,name

def table_of_methods(methods:ElementTree.Element) -> str:
    table = "|Return Type|Method|\n| - | - |\n"
    for m in methods:
        try:
            type,method = decode_method(m)
            table += '|'+type+'|'+method+'|'+"\n"
        except Exception as error:
            print("Error while interpretting members: ",error)
            table += "| |Invalid member| |\n"
    return table

def xml_to_mark_down(root:ElementTree.Element,parser:bbcode.Parser) -> str:
    D = {}
    members = []
    methods = []
    constants = []

    i = 0
    while True:
        try:
            e = root[i]
            match e.tag:
                case "brief_description":
                    D["brief_description"] = e.text
                case "description":
                    D["description"] = e.text
                case "tutorials":
                    D["tutorials"] = e.text
                case "members":
                    members = e
                case "methods":
                    methods = e
        except:
            break
        i += 1

    D["brief_description"] = parser.format(D["brief_description"])
    D["description"] = parser.format(D["description"])

    to_return = "# " + root.attrib["name"] + "\n\n**Inherits:** " + root.attrib["inherits"] + "\n" + D["brief_description"] + "\n"
    to_return += "## Description \n" + D["description"] + "\n"
    to_return += "## Tutorials \n" + D["tutorials"] + "\n"
    to_return += "## Properties \n" + table_of_members(members) + "\n"
    to_return += "## Methods \n" + table_of_methods(methods) + "\n"

    return to_return

# A custom programing language render function.
def render_language(tag_name, value, options, parent, context):
    return '**%s:** \n```%s\n%s \n```' % (tag_name, tag_name, value)

# A custom code render function.
def render_code(tag_name, value, options, parent, context):
    code_parser = bbcode.Parser(newline=" \n", escape_html=False, replace_links=False, replace_cosmetic=True)
    code_parser.REPLACE_COSMETIC = (("    ", ""), ("\t", ""))
    for language in ["csharp","gdscript","python","cpp","text"]:
        code_parser.add_formatter(language, render_language, render_embedded=False, escape_html=False,replace_cosmetic=False)
    return code_parser.format(value)


def create_bbcode_parser() -> bbcode.Parser:
    # Installing simple formatters.
    parser = bbcode.Parser(newline=" \n",escape_html=False,replace_links=False,replace_cosmetic=True)
    parser.REPLACE_COSMETIC = (("    ",""),("\t",""))
    parser.add_simple_formatter('b', '**%(value)s**')
    parser.add_simple_formatter('i', '*%(value)s*')
    parser.add_simple_formatter('u', '<u>%(value)s<u>')
    parser.add_simple_formatter('s', '~~%(value)s~~')
    parser.add_simple_formatter('code', '`%(value)s`',render_embedded=False,escape_html=False,replace_cosmetic=False)
    parser.add_formatter('codeblocks', render_code,render_embedded=False,escape_html=False,replace_cosmetic=False)

    return parser


if __name__ == '__main__':
    # First argument is input directory. Second argument is output directory.
    if len(initialization_arguments) >= 3:
        xml_directory = initialization_arguments[1]
        md_directory = initialization_arguments[2]
    else:
        print('\033[41m' + '\033[30m' + "Please specify directory to .xml docs in first argument and output directory in second." + '\033[0m')
        quit(1)

    try:
        # Gets names of .xml files
        xml_files = os.listdir(xml_directory)
    except:
        print('\033[31m' + "Directory:" + xml_directory + " does not exist or is not a directory." + '\033[0m')
        quit(1)

    parser = create_bbcode_parser()

    for file in xml_files:
        if file[-4:] != ".xml":
            continue
        tree = ElementTree.parse(xml_directory + file)
        root = tree.getroot()
        md_text = xml_to_mark_down(root,parser)

        with open(md_directory + file[:-4] + '.md', 'w') as md_file:
            md_file.write(md_text[:-1])
