
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
    cmd_mouse_move_to_empty_place = session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_move_to_empty_place")
    cmd_mouse_button_press  =   session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_button_press")
    cmd_mouse_button_release=   session.find_keynode_full_uri(u"/ui/core/ui_cmd_mouse_button_release")

    cmd_keyboard_button_press   = session.find_keynode_full_uri(u"/ui/core/ui_cmd_keyboard_button_press")
    cmd_keyboard_button_release = session.find_keynode_full_uri(u"/ui/core/ui_cmd_keyboard_button_release")

    mouse_button_left       =   session.find_keynode_full_uri(u"/ui/core/mouse_button_left")
    mouse_button_right      =   session.find_keynode_full_uri(u"/ui/core/mouse_button_right")
    mouse_button_middle     =   session.find_keynode_full_uri(u"/ui/core/mouse_button_middle")

    class keyboard:

        import ogre.io.OIS as ois

        button_kc_1       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_1")
        button_kc_2       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_2")
        button_kc_3       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_3")
        button_kc_4       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_4")
        button_kc_5       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_5")
        button_kc_6       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_6")
        button_kc_7       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_7")
        button_kc_8       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_8")
        button_kc_9       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_9")
        button_kc_0       =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_0")

        button_kc_f1      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f1")
        button_kc_f2      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f2")
        button_kc_f3      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f3")
        button_kc_f4      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f4")
        button_kc_f5      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f5")
        button_kc_f6      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f6")
        button_kc_f7      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f7")
        button_kc_f8      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f8")
        button_kc_f9      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f9")
        button_kc_f10     =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f10")
        button_kc_f11     =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f11")
        button_kc_f12     =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f12")

        button_kc_q      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_q")
        button_kc_w      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_w")
        button_kc_e      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_e")
        button_kc_r      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_r")
        button_kc_t      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_t")
        button_kc_y      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_y")
        button_kc_u      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_u")
        button_kc_i      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_i")
        button_kc_o      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_o")
        button_kc_p      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_p")
        button_kc_a      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_a")
        button_kc_s      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_s")
        button_kc_d      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_d")
        button_kc_f      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_f")
        button_kc_g      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_g")
        button_kc_h      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_h")
        button_kc_j      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_j")
        button_kc_k      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_k")
        button_kc_l      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_l")
        button_kc_z      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_z")
        button_kc_x      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_x")
        button_kc_c      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_c")
        button_kc_v      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_v")
        button_kc_b      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_b")
        button_kc_n      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_n")
        button_kc_m      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_m")

        button_kc_up        =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_up")
        button_kc_down      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_down")
        button_kc_right     =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_right")
        button_kc_left      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_left")

        button_kc_escape    =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_escape")
        button_kc_delete    =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_delete")
        button_kc_return    =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_return")
        button_kc_space     =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_space")
        button_kc_pgup      =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_pgup")
        button_kc_pgdown    =   session.find_keynode_full_uri(u"/ui/core/keyboard_button_pgdown")

        dictionary = {
            button_kc_1     :ois.KC_1,              button_kc_q:ois.KC_Q,               button_kc_up        :ois.KC_UP,
            button_kc_2     :ois.KC_2,              button_kc_w:ois.KC_W,               button_kc_down      :ois.KC_DOWN,
            button_kc_3     :ois.KC_3,              button_kc_e:ois.KC_E,               button_kc_right     :ois.KC_RIGHT,
            button_kc_4     :ois.KC_4,              button_kc_r:ois.KC_R,               button_kc_left      :ois.KC_LEFT,
            button_kc_5     :ois.KC_5,              button_kc_t:ois.KC_T,
            button_kc_6     :ois.KC_6,              button_kc_y:ois.KC_Y,               button_kc_escape    :ois.KC_ESCAPE,
            button_kc_7     :ois.KC_7,              button_kc_i:ois.KC_I,               button_kc_delete    :ois.KC_DELETE,
            button_kc_8     :ois.KC_8,              button_kc_o:ois.KC_O,               button_kc_return    :ois.KC_RETURN,
            button_kc_9     :ois.KC_9,              button_kc_p:ois.KC_P,               button_kc_space     :ois.KC_SPACE,
            button_kc_0     :ois.KC_0,              button_kc_a:ois.KC_A,               button_kc_pgup      :ois.KC_PGUP,
            button_kc_f1    :ois.KC_F1,             button_kc_s:ois.KC_S,               button_kc_pgdown    :ois.KC_PGDOWN,
            button_kc_f2    :ois.KC_F2,             button_kc_d:ois.KC_D,
            button_kc_f3    :ois.KC_F3,             button_kc_f:ois.KC_D,
            button_kc_f4    :ois.KC_F4,             button_kc_g:ois.KC_G,
            button_kc_f5    :ois.KC_F5,             button_kc_h:ois.KC_H,
            button_kc_f6    :ois.KC_F6,             button_kc_j:ois.KC_J,
            button_kc_f7    :ois.KC_F7,             button_kc_k:ois.KC_K,
            button_kc_f8    :ois.KC_F8,             button_kc_l:ois.KC_L,
            button_kc_f9    :ois.KC_F9,             button_kc_z:ois.KC_Z,
            button_kc_f10   :ois.KC_F10,            button_kc_x:ois.KC_X,
            button_kc_f11   :ois.KC_F11,            button_kc_c:ois.KC_C,
            button_kc_f12   :ois.KC_F12,            button_kc_v:ois.KC_V,
                                                    button_kc_b:ois.KC_B,
                                                    button_kc_n:ois.KC_N,
                                                    button_kc_m:ois.KC_M,
                                                    button_kc_u:ois.KC_U,
        }


    
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
    rrel_active_user             =   session.find_keynode_full_uri(u"/ui/core/активный пользователь_")
    user_name               =   session.find_keynode_full_uri(u"/ui/core/имя пользователя")
    user_password           =   session.find_keynode_full_uri(u"/ui/core/пароль")
    
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
    