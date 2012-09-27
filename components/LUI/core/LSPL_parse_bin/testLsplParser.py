# -*- coding: cp1251 -*-
import LsplParser
import os

rml_dir = os.path.dirname(os.path.abspath(__file__))
LsplParser.setRMLpath(rml_dir)

parser = LsplParser.LsplParser()
parser.loadMorphology()
namespace = parser.createNewNamespace()

parser.addPatternToNamespace(namespace, "TARGET = {N}N")
parser.addPatternToNamespace(namespace, "TARGET = [A]N")
parser.addPatternToNamespace(namespace, "WhatIsIs = \"что\" \"такое\" * TARGET")
parser.addPatternToNamespace(namespace, "WhatIsIs = A<полный> [A<семантичаская>] * \"окрестность\" * TARGET")
parser.addPatternToNamespace(namespace, "SrchIll = V<выглядеть> * TARGET")

text = "как выглядит тупоугольный треугольник"
print text
result = parser.parseTextInNamespace(namespace, text)
for question in result.getQuestionVariants(): print "Question = %s" % question
for target in result.getObjectsVariants(): print "Object = %s" % target
