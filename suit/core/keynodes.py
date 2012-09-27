
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
Created on 20.11.2009

@author: Denis Koronchik
'''
import kernel

session = kernel.Kernel.session()

session.open_segment(u"/etc/com_keynodes")
session.open_segment(u"/etc/questions")

# getting system keynodes
n_1     =   session.find_keynode_full_uri(u"/proc/keynode/1_")
n_2     =   session.find_keynode_full_uri(u"/proc/keynode/2_")
n_3     =   session.find_keynode_full_uri(u"/proc/keynode/3_")
n_4     =   session.find_keynode_full_uri(u"/proc/keynode/4_")
n_5     =   session.find_keynode_full_uri(u"/proc/keynode/5_")
n_6     =   session.find_keynode_full_uri(u"/proc/keynode/6_")
n_7     =   session.find_keynode_full_uri(u"/proc/keynode/7_")
n_8     =   session.find_keynode_full_uri(u"/proc/keynode/8_")
n_9     =   session.find_keynode_full_uri(u"/proc/keynode/9_")
n_10    =   session.find_keynode_full_uri(u"/proc/keynode/10_")

attr = {
        0:session.find_keynode_full_uri(u"/proc/keynode/1_"),
        1:session.find_keynode_full_uri(u"/proc/keynode/2_"),
        2:session.find_keynode_full_uri(u"/proc/keynode/3_"),
        3:session.find_keynode_full_uri(u"/proc/keynode/4_"),
        4:session.find_keynode_full_uri(u"/proc/keynode/5_"),
        5:session.find_keynode_full_uri(u"/proc/keynode/6_"),
        6:session.find_keynode_full_uri(u"/proc/keynode/7_"),
        7:session.find_keynode_full_uri(u"/proc/keynode/8_"),
        8:session.find_keynode_full_uri(u"/proc/keynode/9_"),
        9:session.find_keynode_full_uri(u"/proc/keynode/10_")
        }


# semantic keynodes
class info:
    sc_unknown      =   session.find_keynode_full_uri(u"/info/sc_unknown")
    sc_const        =   session.find_keynode_full_uri(u"/info/sc_const")
    sc_var          =   session.find_keynode_full_uri(u"/info/sc_var")
    sc_meta         =   session.find_keynode_full_uri(u"/info/sc_meta")
    
    # structure type
    stype_element   =   session.find_keynode_full_uri(u"/info/stype_element")
    stype_sheaf     =   session.find_keynode_full_uri(u"/info/stype_sheaf")
    stype_pair_noorient =   session.find_keynode_full_uri(u"/info/stype_pair_noorient")
    stype_pair_orient   =   session.find_keynode_full_uri(u"/info/stype_pair_orient")
    
    
    stype_nopair_sheaf  =   session.find_keynode_full_uri(u"/info/stype_nopair_sheaf")
    stype_struct    =   session.find_keynode_full_uri(u"/info/stype_struct")
    stype_concept   =   session.find_keynode_full_uri(u"/info/stype_concept")
    stype_relation  =   session.find_keynode_full_uri(u"/info/stype_relation")
    stype_bin_noorient_rel  =   session.find_keynode_full_uri(u"/info/stype_bin_noorient_rel")
    stype_bin_orient_rel    =   session.find_keynode_full_uri(u"/info/stype_bin_orient_rel")
    stype_bin_orient_role_rel   =   session.find_keynode_full_uri(u"/info/stype_bin_orient_role_rel")
    stype_bin_orient_norole_rel =   session.find_keynode_full_uri(u"/info/stype_bin_orient_norole_rel")
    stype_nobin_noorient_rel    =   session.find_keynode_full_uri(u"/info/stype_nobin_noorient_rel")
    stype_nobin_orient_rel  =   session.find_keynode_full_uri(u"/info/stype_nobin_orient_rel")
    stype_concept_norel =   session.find_keynode_full_uri(u"/info/stype_concept_norel")
    stype_struct_class  =   session.find_keynode_full_uri(u"/info/stype_struct_class")
    stype_ext_obj_class =   session.find_keynode_full_uri(u"/info/stype_ext_obj_class")
    stype_ext_info_type1_class  =   session.find_keynode_full_uri(u"/info/stype_ext_info_type1_class")
    stype_ext_obj       =   session.find_keynode_full_uri(u"/info/stype_ext_obj")
    stype_ext_obj_abstract  =   session.find_keynode_full_uri(u"/info/stype_ext_obj_abstract")
    stype_ext_obj_real  =   session.find_keynode_full_uri(u"/info/stype_ext_obj_real")
    stype_ext_info_constr   =   session.find_keynode_full_uri(u"/info/stype_ext_info_constr")
    stype_ext_noinfo_obj_real   =   session.find_keynode_full_uri(u"/info/stype_ext_noinfo_obj_real")
    
    stype_pair_time     =   session.find_keynode_full_uri(u"/info/stype_pair_time")
    
# keynodes for user interface
class ui:
    viewer                  =   session.find_keynode_full_uri(u"/ui/core/просмотрщик")
    editor                  =   session.find_keynode_full_uri(u"/ui/core/редактор")
    translator              =   session.find_keynode_full_uri(u"/ui/core/транслятор")
    main_window             =   session.find_keynode_full_uri(u"/ui/core/главное окно")
    sc_window               =   session.find_keynode_full_uri(u"/ui/core/sc-окно")
    set_output_windows      =   session.find_keynode_full_uri(u"/ui/core/ui_output_window_set")
    translate_langs         =   session.find_keynode_full_uri(u"/ui/core/ui_all_translations")
    translate_lang_current  =   session.find_keynode_full_uri(u"/ui/core/ui_used_translation")
    
    nrel_set_of_supported_formats   =   session.find_keynode_full_uri(u"/ui/core/множество поддерживаемых форматов*")
    nrel_set_of_supported_input_formats  =    session.find_keynode_full_uri(u"/ui/core/множество поддерживаемых входных форматов*")
    nrel_set_of_supported_output_formats =    session.find_keynode_full_uri(u"/ui/core/множество поддерживаемых выходных форматов*")
    nrel_child_window       =   session.find_keynode_full_uri(u"/ui/core/дочернее окно*")
    nrel_set_of_output_windows      =   session.find_keynode_full_uri(u"/ui/core/множество окон для вывода ответа*")
    
    arg_cur_window          =   session.find_keynode_full_uri(u"/ui/core/ui_arg_cur_window")
    arg_set                 =   session.find_keynode_full_uri(u"/ui/core/ui_arg_set")
    arg_set_only            =   session.find_keynode_full_uri(u"/ui/core/ui_arg_set_only")
    arg_all_el              =   session.find_keynode_full_uri(u"/ui/core/ui_arg_all_el")
    arg_1                   =   session.find_keynode_full_uri(u"/ui/core/ui_arg_1")
    arg_2                   =   session.find_keynode_full_uri(u"/ui/core/ui_arg_2")
    arg_3                   =   session.find_keynode_full_uri(u"/ui/core/ui_arg_3")
    arg_4                   =   session.find_keynode_full_uri(u"/ui/core/ui_arg_4")
    
    base_user_cmd           =   session.find_keynode_full_uri(u"/ui/core/элементарная пользовательская команда")
    init_base_user_cmd      =   session.find_keynode_full_uri(u"/ui/core/инициированная элементарная пользовательская команда")
    active_base_user_cmd    =   session.find_keynode_full_uri(u"/ui/core/активная элементарная пользовательская команда")
    finish_base_user_cmd    =   session.find_keynode_full_uri(u"/ui/core/завершенная элементарная пользовательская команда")
    
    user_cmd           =   session.find_keynode_full_uri(u"/ui/core/ui_user_command")
    init_user_cmd      =   session.find_keynode_full_uri(u"/ui/core/ui_initiated_user_command")
    active_user_cmd    =   session.find_keynode_full_uri(u"/ui/core/ui_active_user_command")
    finish_user_cmd    =   session.find_keynode_full_uri(u"/ui/core/ui_finished_user_command")
        
    nrel_template_user_cmd  =   session.find_keynode_full_uri(u"/ui/core/обобщенная формулировка команды*")
    
    cmd_mouse_move_obj      =   session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_move_obj")
    cmd_mouse_button_press  =   session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_button_press")
    cmd_mouse_button_release=   session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_button_release")
    
    mouse_button_left       =   session.find_keynode_full_uri(u"/ui/core/mouse_button_left")
    mouse_button_right      =   session.find_keynode_full_uri(u"/ui/core/mouse_button_right")
    mouse_button_middle     =   session.find_keynode_full_uri(u"/ui/core/mouse_button_middle")
    
    # format
    format                  =   session.find_keynode_full_uri(u"/ui/core/формат")
    format_sc               =   session.find_keynode_full_uri(u"/ui/core/SC")
    format_scgx             =   session.find_keynode_full_uri(u"/ui/core/SCGx")
    format_geomx            =   session.find_keynode_full_uri(u"/ui/core/GEOMx")
    
    format_jpg              =   session.find_keynode_full_uri(u"/ui/core/JPG")
    format_jpeg             =   session.find_keynode_full_uri(u"/ui/core/JPEG")
    format_bmp              =   session.find_keynode_full_uri(u"/ui/core/BMP")
    format_png              =   session.find_keynode_full_uri(u"/ui/core/PNG")
    
    format_string           =   session.find_keynode_full_uri(u"/ui/core/STRING")
    format_term             =   session.find_keynode_full_uri(u"/ui/core/TERM")
    
    format_int              =   session.find_keynode_full_uri(u"/ui/core/INT")
    format_real             =   session.find_keynode_full_uri(u"/ui/core/REAL")
    
    format_wmv              =   session.find_keynode_full_uri(u"/ui/core/WMV")
    format_avi              =   session.find_keynode_full_uri(u"/ui/core/AVI")
    format_mp4              =   session.find_keynode_full_uri(u"/ui/core/MP4")
    format_flv              =   session.find_keynode_full_uri(u"/ui/core/FLV")
    format_mpg              =   session.find_keynode_full_uri(u"/ui/core/MPG")
    format_html             =   session.find_keynode_full_uri(u"/ui/core/HTML")
    format_swf              =   session.find_keynode_full_uri(u"/ui/core/SWF")
    
    format_midmif           =   session.find_keynode_full_uri(u"/ui/core/MIDMIF")
    
    format_objx             =   session.find_keynode_full_uri(u"/ui/core/OBJx")
    
    format_graph            =   session.find_keynode_full_uri(u"/ui/core/GRAPH")
    
    format_space            =   session.find_keynode_full_uri(u"/ui/core/SPACEx")
    
    # command keynodes
    atom_command            =   session.find_keynode_full_uri(u"/ui/core/атомарная команда")
    noatom_command          =   session.find_keynode_full_uri(u"/ui/core/неатомарная команда")
    question_command        =   session.find_keynode_full_uri(u"/ui/core/команда вопрос")
    user                    =   session.find_keynode_full_uri(u"/ui/core/пользователь")
    
    
class common:
    nrel_decomposition      =   session.find_keynode_full_uri(u"/etc/com_keynodes/декомпозиция*");
    nrel_identification     =   session.find_keynode_full_uri(u"/etc/com_keynodes/идентификация*");
    nrel_authors            =   session.find_keynode_full_uri(u"/etc/com_keynodes/авторы*")
    nrel_base_order         =   session.find_keynode_full_uri(u"/etc/com_keynodes/базовая последовательность*")
    nrel_value              =   session.find_keynode_full_uri(u"/etc/com_keynodes/значение*")
    nrel_explanation        =   session.find_keynode_full_uri(u"/etc/com_keynodes/пояснение*")

    rrel_russian_text       =   session.find_keynode_full_uri(u"/etc/com_keynodes/русский текст_");
    rrel_english_text       =   session.find_keynode_full_uri(u"/etc/com_keynodes/английский текст_");
    rrel_dec_number         =   session.find_keynode_full_uri(u"/etc/com_keynodes/десятичное число_")
    
    #group_russian_language  =   session.find_keynode_full_uri(u"/etc/com_keynodes/Русский язык")
    group_image             =   session.find_keynode_full_uri(u"/etc/com_keynodes/изображение")
        
    
class questions:
    question                =   session.find_keynode_full_uri(u"/etc/questions/вопрос")
    initiated               =   session.find_keynode_full_uri(u"/etc/questions/инициированный вопрос")
    atom                    =   session.find_keynode_full_uri(u"/etc/questions/атомарный вопрос")
    noatom                  =   session.find_keynode_full_uri(u"/etc/questions/неатомарный вопрос")
    active                  =   session.find_keynode_full_uri(u"/etc/questions/активный вопрос")
    finished                =   session.find_keynode_full_uri(u"/etc/questions/отработанный вопрос")
    succesful               =   session.find_keynode_full_uri(u"/etc/questions/успешный вопрос")
    _class                  =   session.find_keynode_full_uri(u"/etc/questions/класс вопроса")
    
    nrel_action_area        =   session.find_keynode_full_uri(u"/etc/questions/область действия вопроса*")
    nrel_key_fragment       =   session.find_keynode_full_uri(u"/etc/questions/ключевой фрагмент вопроса*")
    nrel_answer             =   session.find_keynode_full_uri(u"/etc/questions/ответ*")
    nrel_general_formulation=   session.find_keynode_full_uri(u"/etc/questions/обобщенная формулировка вопроса*")
    