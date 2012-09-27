# -*- coding: utf-8 -*-

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
Created on 21.09.2010

@author: Zhitko V.A.
'''

import suit.core.keynodes as sc_keys
import sc_core.pm as sc

class Operation:
    
    # конструктор класса
    def __init__(self):
        pass

    # функция проверки условия выполнения операции
    # должны быть переопределена
    @classmethod
    def checking(self, question):
        print "[Operation] Warning default checking!!!"
        return True
    
    # функция вызываемая при выполнении операции
    # должны быть переопределена
    # возвращает 
    # [продолжить ли поиск вопроса, [множество узлов ответа]]
    def running(self, question):
        return []
    
    # возвращает sc_addr узла спецификации операции
    @classmethod
    def getOperationNode(self):
        return None
        
        
        
        
        
        
        
        
        
        