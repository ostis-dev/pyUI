
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2010 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""


'''
Created on 29.01.2010

@author: Denis Koronchick
'''
# FIXME:        encoding problems

import sys, os
import xml.dom.minidom as xml
import locale as lc


import codecs
lc.setlocale(lc.LC_ALL, ('English_United States', '1251'))
encoding = lc.getlocale()[1]
if not encoding:
    encoding = "utf-8"
reload(sys)
sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")

stype_inc_list = []

stypes_conv = {"predmet": "stype_ext_obj_abstract",
               "relation": "stype_bin_orient_norole_rel",
               "attribute": "stype_bin_orient_role_rel",
               "nopredmet": "stype_struct",
               "group": "stype_concept_norel",
               "asymmetry": "stype_sheaf"}

format_conv = {"x-ms-bmp": "bmp"}



# not used for now
aconst_conv = {"const": ">",
               "var": ">>",
               "meta": ">>>"}
# not used for now
apos_conv = {"pos": "-",
             "neg": "/",
             "fuz": "~"}

# counter for object id's
object_counter = 0

# writed elements
writed_ids = []

# source path
src_path = None

##################
class Element:

    includes = []
    gwf_files = []

    output_lines = []

    idtf2loc_id = {}
    loc2glob_id = {}
    globid2el = {}


    @staticmethod
    def appendComment(text):
        Element.output_lines.append("// %s" % text)

    @staticmethod
    def appendLine(text):
        if text is not None:
            Element.output_lines.append(text.lstrip())

    @staticmethod
    def reset():
        Element.loc2glob_id = {}

    def __init__(self):
        self._id = None
        self._idtf = None
        self._parent = None
        self.glob_id = None
        self.writed = False

    def have_idtf(self):
        return len(self._idtf) > 0

    def get_glob_id_str(self):
        return "$%s" % (self.glob_id)

    def write_to_scs(self):
        # creating identificator
        if self.have_idtf() and Element.idtf2loc_id.has_key(self._idtf):
            _id = Element.idtf2loc_id[self._idtf]
            self.writed = True
        else:
            _id = get_id()
            Element.idtf2loc_id[self._idtf] = _id
            Element.globid2el[_id] = self

        Element.loc2glob_id[self._id] = _id

        self.glob_id = _id

        return None

class Node(Element):

    def __init__(self):
        Element.__init__(self)
        self._type = None
        self._content_type = None
        self._mime_type = None
        self._content = None

    def have_cont(self):
        return self._content_type == "1" or self._content_type == "2" or self._content_type == "3" or self._content_type == "4"

    def compare(self, _other):
        return False

    def get_glob_id_str(self):

        if self._type.find("var") != -1:
            return "$_%s" % (self.glob_id)
        elif self._type.find("meta") != -1:
            return "$__%s" % (self.glob_id)

        return "$%s" % (self.glob_id)

    def write_to_scs(self):

        res = ""

        Element.write_to_scs(self)
        if self.writed: return None

        # getting const
        _const = ""
        if self._type.find('const') != -1:
            _const = ""
        elif self._type.find('var') != -1:
            _const = ". ."
        elif self._type.find('meta') != -1:
            _const = ".. .."


        # writing nodes to output
        if self.have_idtf():
                res = res + ('%s = "%s" = {%s};\n' % (self.get_glob_id_str(), self._idtf, _const))
        else:
            res = res + ('%s = {%s};\n' % (self.get_glob_id_str(), _const))

        # writing nodes content
        if self.have_cont():

            fmt = "unknown"
            _b64 = ""
            if self._content_type == "4":
                # getting format
                fmt = self._mime_type
                idx = self._mime_type.rfind("/")
                if idx != -1:
                    fmt = self._mime_type[idx+1:].upper()
                if format_conv.has_key(fmt):    fmt = format_conv[fmt]
                fmt_a = "="
                _b64 = "b64"
                cnt = self._content
                self._content = cnt.replace(" ", "").replace("\n", "").replace("\r", "")
            else:
                if self._content_type == "2":
                    fmt = "int"
                    fmt_a = "=n="
                elif self._content_type == "3":
                    fmt = "real"
                    fmt_a = "=n="
                elif self._content_type == "1":
                    fmt = "string"
                    fmt_a = "=c="

                    # removing newlines symbols and spaces
                    cnt = self._content
                    cnt = cnt.lstrip().rstrip()
                    while cnt.endswith("\n"):
                        cnt = cnt[:-1]

                    cnt = cnt.replace("\"", "\\\"")

                    #cnt = cnt.replace("\r\n", "")
                    #cnt = cnt.replace("\n\r", "")


                    self._content = cnt




            if self._content_type == "2" or self._content_type == "3":
                self._content = self._content.replace("\n", "")
                res = res + ('%s %s "%s";\n' % (self.get_glob_id_str(), fmt_a, self._content))
            else:
                # writing content
                res = res + ('%s %s %s/"%s"/;\n' % (self.get_glob_id_str(), fmt_a, _b64, self._content))
            # creating format
            res = res + ("ui_format_%s -> %s;\n" % (fmt.lower(), self.get_glob_id_str()))

        # struct type
        stype = None
        for st, vl in stypes_conv.items():
            if self._type.find(st) != -1:
                stype = vl

        if stype is not None:
            if self.have_idtf():
                if not self._idtf in stype_inc_list:
                    stype_inc_list.append(self._idtf)
                    res = res + ("%s -> %s;\n" % (stype, self.get_glob_id_str()))
            else:
                res = res + ("%s -> %s;\n" % (stype, self.get_glob_id_str()))

        return res

class Bus(Element):

    def __init__(self):
        Element.__init__(self)
        self._owner = None


    def write_to_scs(self):
        """Writes bus to scs
        """
        if self._owner != "0":
            if self.have_idtf() and Element.idtf2loc_id.has_key(self._idtf):
                _id = Element.idtf2loc_id[self._idtf]
            else:
                _id = Element.loc2glob_id[self._owner]
                Element.idtf2loc_id[self._idtf] = _id
                Element.loc2glob_id[self._id] = _id
#                Element.globid2el[_id] = self

            Element.loc2glob_id[self._id] = _id
            self.glob_id = _id
        else:
            Element.write_to_scs(self)

        if self.writed: return None

        # writing to scs
        res = "$%s = {};\n" % (self.glob_id)
        if self.have_idtf():    res = res + '%s = "%s";' % (self.get_glob_id_str(), self._idtf)

        return res

class Contour(Element):

    def __init__(self):
        Element.__init__(self)
        self.has_1_ = False
        self.has_2_ = False

    def write_to_scs(self):
        """Writes contour to scs
        """
        Element.write_to_scs(self)

        if self.writed: return None

        # writing contour
        res = "$%s = {};\n" % (self.glob_id)
        if self.have_idtf():    res = res + '%s = "%s";' % (self.get_glob_id_str(), self._idtf)

        return res

class Arc(Element):

    def __init__(self):
        Element.__init__(self)
        self._beg = None
        self._end = None
        self._type = None

    def gen_id(self):

        if self.glob_id is not None:    return

        _id = get_id()
        Element.idtf2loc_id[self._idtf] = _id
        Element.globid2el[_id] = self
        Element.loc2glob_id[self._id] = _id
        self.glob_id = _id

    def get_glob_id_str(self):

        if self._type.find("var") != -1:
            return "$_%s" % (self.glob_id)
        elif self._type.find("meta") != -1:
            return "$__%s" % (self.glob_id)

        return "$%s" % (self.glob_id)

    def write_to_scs(self):

        # getting types and process pairs
        if self._type.startswith("pair"):
            return None
        else:
            # const
            _const = ">"
            _pre_id = ""
            if self._type.find("const") != -1:
                _const = ">"
            elif self._type.find("var") != -1:
                _const = ">>"
                _pre_id = "_"
            elif self._type.find("meta") != -1:
                _const = ">>>"
                _pre_id = "__"

            # pos
            _pos = "-"
            if self._type.find("pos") != -1:
                _pos = "-"
            elif self._type.find("neg") != -1:
                _pos = "/"
            elif self._type.find("fuz") != -1:
                _pos = "~"


            res = "$%s%s = (%s %s%s %s);" % (_pre_id,
                                               self.glob_id,
                                               self.globid2el[self.loc2glob_id[self._beg]].get_glob_id_str(),
                                               _pos, _const,
                                               self.globid2el[self.loc2glob_id[self._end]].get_glob_id_str())


            return res

class Pair(Arc):

    def __init__(self):
        Arc.__init__(self)

        self.gen_ids = []

    def write_to_scs(self):

        if self.writed: return None

        # getting const
        _node_const = None
        _pair_const = None
        _attr_const = None
        _pair_pre = None
        _node_const_o = None
        _node_const_c = None
        if self._type.find("const") != -1:
            _node_const = "{}"
            _pair_const = "->"
            _attr_const = ":"
            _node_const_o = "{"
            _node_const_c = "}"
            _pair_pre = ""
        elif self._type.find("var") != -1:
            _node_const = "{. .}"
            _node_const_o = "{."
            _node_const_c = ".}"
            _pair_const = "->>"
            _attr_const = "::"
            _pair_pre = "_"
        elif self._type.find("meta") != -1:
            _node_const = "{.. ..}"
            _node_const_o = "{.."
            _node_const_c = "..}"
            _pair_const = "->>>"
            _attr_const = ":::"
            _pair_pre = "__"
        else:
            print "unsupported pair type %s" % self._type
            return None

        # getting orient flag
        _orient = False
        if self._type.find("orient") != -1:
            _orient = True

        # writing sheaf node
        res = "%s = %s;\n" % (self.get_glob_id_str(), _node_const)

        if self.have_idtf():
            res = res + '%s = "%s";\n' % (self.get_glob_id_str(), self._idtf)

        self.gen_ids = [self.get_glob_id_str()]#, a1, a2]

        if _orient:
            #res = res + "1_ %s $%s%s;\n" % (_pair_const, _pair_pre, a1)
            #res = res + "2_ %s $%s%s;" % (_pair_const, _pair_pre, a2)
            arc1_id = "$%s%s" % (_pair_pre, get_id())
            arc1_attr_id = "$%s%s" % (_pair_pre, get_id())
            arc2_id = "$%s%s" % (_pair_pre, get_id())
            arc2_attr_id = "$%s%s" % (_pair_pre, get_id())
            res = res + "%s = ( %s %s %s );\n" % (arc1_id,
                                                     self.get_glob_id_str(), _pair_const,
                                                     self.globid2el[self.loc2glob_id[self._beg]].get_glob_id_str())
            res = res + "%s = ( %s %s %s );\n" % ( arc2_id,
                                                     self.get_glob_id_str(), _pair_const,
                                                     self.globid2el[self.loc2glob_id[self._end]].get_glob_id_str())
            res = res + "%s = ( 1_ %s %s );\n" % (arc1_attr_id, _pair_const, arc1_id)
            res = res + "%s = ( 2_ %s %s );\n" % (arc2_attr_id, _pair_const, arc2_id)
            self.gen_ids.append(arc1_id)
            self.gen_ids.append(arc1_attr_id)
            self.gen_ids.append(arc2_id)
            self.gen_ids.append(arc2_attr_id)
            self.gen_ids.append("1_")
            self.gen_ids.append("2_")
        else:
            arc1_id = "$%s%s" % (_pair_pre, get_id())
            arc2_id = "$%s%s" % (_pair_pre, get_id())
            res = res + "%s = ( %s %s %s );\n" % (arc1_id,
                                                     self.get_glob_id_str(), _pair_const,
                                                     self.globid2el[self.loc2glob_id[self._beg]].get_glob_id_str())
            res = res + "%s = ( %s %s %s );\n" % ( arc2_id,
                                                     self.get_glob_id_str(), _pair_const,
                                                     self.globid2el[self.loc2glob_id[self._end]].get_glob_id_str())
            self.gen_ids.append(arc1_id)
            self.gen_ids.append(arc2_id)


        res = res + "%s -> %s;\n" % (stypes_conv["asymmetry"], self.get_glob_id_str())

        return res


##################

def get_includes(lines):

    # getting includes
    for line in lines:
        ln = line.lstrip()
        if ln.startswith("#include"):
            Element.includes.append(ln)

def get_gwf_files(lines):

    # getting list of gwf files with absolute path
    for line in lines:
        ln = line.lstrip().rstrip()
        if ln.endswith(".gwf"):
            Element.gwf_files.append(os.path.join(src_path, ln))

def get_id():

    global object_counter
    object_counter += 1
    return str(object_counter)

def reset():

    Element.includes = []
    Element.gwf_files = []

    Element.output_lines = []

    Element.idtf2loc_id = {}

def write_list(_list):
    for item in _list:
        Element.appendLine(item.write_to_scs())

def process_gwf_data(nodes, arcs, pairs, buss, contours):

    objs = []
    objs.extend(nodes)
    objs.extend(arcs)
    objs.extend(pairs)
    objs.extend(buss)
    objs.extend(contours)

    Element.appendComment("----------------------------------------------")

    # creating local idtfs map
    loc_id_text = {}
    for obj in objs:
        if len(obj._idtf) > 0:
            loc_id_text[obj._id] = obj._idtf

    # map local -> global
    global writed_ids

    # writing nodes to output file
    Element.appendComment("node")
    write_list(nodes)
    # writing contours to output file
    Element.appendComment("contour")
    write_list(contours)
    # writing buses to output file
    Element.appendComment("bus")
    write_list(buss)
    for arc in arcs:    arc.gen_id()
    for pair in pairs:    pair.gen_id()

    # writing pairs to output file
    Element.appendComment("pair")
    write_list(arcs)
    # writing binary pairs to output file
    Element.appendComment("bin pair")
    write_list(pairs)


    Element.appendComment("contour child elements")
    def inc_contour(_contour_id, _el_id):
        Element.output_lines.append("%s -> %s;" % (_contour_id, _el_id))

    # creating contours
    for obj in objs:
        _contour = None
        for _cont in contours:
            if _cont._id == obj._parent:
                _contour = _cont
                break

        if _contour is None:    continue

        # appending contour child objects
        if isinstance(obj, Pair):
            for _id in obj.gen_ids:
                if _id == "1_":
                    if _contour.has_1_:
                        continue
                    _contour.has_1_ = True
                elif _id == "2_":
                    if _contour.has_2_:
                        continue
                    _contour.has_2_ = True
                inc_contour(_contour.get_glob_id_str(), _id)
        else:
            inc_contour(_contour.get_glob_id_str(), obj.get_glob_id_str())

def parse_gwf(file_name):
    """Parse one gwf file and appending data from it to structures
    """
    doc = xml.parse(file_name)
    gwf_node = doc.childNodes[0]

    Element.reset()

    nodes = []
    buss = []
    pairs = []
    arcs = []
    contours = []

    # parsing nodes
    node_tags = gwf_node.getElementsByTagName("node")
    for tag in node_tags:
        # getting attributes
        node = Node()
        node._type = tag.attributes["type"].value
        node._idtf = tag.attributes["idtf"].value
        node._id = tag.attributes["id"].value
        node._parent = tag.attributes["parent"].value

        # getting content
        c_tag = tag.getElementsByTagName("content")[0]
        node._content_type = c_tag.attributes["type"].value
        node._mime_type = c_tag.attributes["mime_type"].value
        if node._content_type != "0":
            node._content = c_tag.firstChild.wholeText

        nodes.append(node)

    bus_tags = gwf_node.getElementsByTagName("bus")
    for tag in bus_tags:
        # getting attributes
        bus = Bus()
        bus._idtf = tag.attributes["idtf"].value
        bus._owner = tag.attributes["owner"].value
        bus._id = tag.attributes["id"].value
        bus._parent = tag.attributes["parent"].value

        buss.append(bus)

    contour_tags = gwf_node.getElementsByTagName("contour")
    for tag in contour_tags:
        # getting attributes
        contour = Contour()
        contour._idtf = tag.attributes["idtf"].value
        contour._id = tag.attributes["id"].value
        contour._parent = tag.attributes["parent"].value

        contours.append(contour)

    arc_tags = gwf_node.getElementsByTagName("arc")
    for tag in arc_tags:
        # getting attributes
        arc = Arc()
        arc._idtf = tag.attributes["idtf"].value
        arc._id = tag.attributes["id"].value
        arc._beg = tag.attributes["id_b"].value
        arc._end = tag.attributes["id_e"].value
        arc._parent = tag.attributes["parent"].value
        arc._type = tag.attributes["type"].value

        arcs.append(arc)

    pair_tags = gwf_node.getElementsByTagName("pair")
    for tag in pair_tags:
        # getting attributes
        pair = Pair()
        pair._idtf = tag.attributes["idtf"].value
        pair._id = tag.attributes["id"].value
        pair._beg = tag.attributes["id_b"].value
        pair._end = tag.attributes["id_e"].value
        pair._parent = tag.attributes["parent"].value
        pair._type = tag.attributes["type"].value

        pairs.append(pair)

    Element.appendComment("file: %s" % file_name)
    process_gwf_data(nodes, arcs, pairs, buss, contours)


def parse_gwf_files():
    """Parsing gwf files and merge them
    """
    for gwf_file in Element.gwf_files:
        print "parsing %s" % (gwf_file.decode("cp1251"))
        parse_gwf(gwf_file)


def parse_scg(file_name):
    """parse scg file
    """
    reset()

    scg_file = open(file_name, "r")
    lines = scg_file.readlines()
    scg_file.close()
    # getting source path
    global src_path
    src_path = os.path.dirname(file_name)

    # includes
    get_includes(lines)
    # getting list of gwf files
    get_gwf_files(lines)
    # parse gwf files
    parse_gwf_files()

    print "preparing for building"


def write_scs(scs_file):

    scs_file.write('#include "_keynodes.scsy"')
    for inc in Element.includes:
        scs_file.write("%s\n" % inc)
    for line in Element.output_lines:
        scs_file.write("%s\n" % line.encode('cp1251'))


if __name__ == '__main__':

    # parsing files
    parse_scg(sys.argv[1])

    scs_file = file(sys.argv[2], "w")
    write_scs(scs_file)
    scs_file.close()
