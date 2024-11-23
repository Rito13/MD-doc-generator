from xml.etree import cElementTree as ElementTree
from sys import argv as initialization_arguments
import os
import bbcode


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def dict_to_mark_down(D:dict,parser:bbcode.Parser) -> str:
    D["brief_description"] = parser.format(D["brief_description"])
    D["description"] = parser.format(D["description"])

    to_return = "# " + D["name"] + "\n\n**Inherits:** " + D["inherits"] + "\n" + D["brief_description"] + "\n"
    to_return += "## Description \n" + D["description"] + "\n"
    to_return += "## Tutorials \n" + D["tutorials"] + "\n"

    return to_return

# A custom programing language render function.
def render_language(tag_name, value, options, parent, context):
    return '**%s:**  \n```%s\n%s  \n```' % (tag_name, tag_name, value)

# A custom code render function.
def render_code(tag_name, value, options, parent, context):
    code_parser = bbcode.Parser(newline="  \n", escape_html=False, replace_links=False, replace_cosmetic=True)
    code_parser.REPLACE_COSMETIC = (("    ", ""), ("\t", ""))
    for language in ["csharp","gdscript","python","cpp","text"]:
        code_parser.add_formatter(language, render_language, render_embedded=False, escape_html=False,replace_cosmetic=False)
    return code_parser.format(value)


def create_bbcode_parser() -> bbcode.Parser:
    # Installing simple formatters.
    parser = bbcode.Parser(newline="  \n",escape_html=False,replace_links=False,replace_cosmetic=True)
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
        xmldict = XmlDictConfig(root)
        md_text = dict_to_mark_down(xmldict,parser)

        with open(md_directory + file[:-4] + '.md', 'w') as md_file:
            md_file.write(md_text[:-1])
