dnl # -----------------------------------------------------------------------------
dnl # This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
dnl # For the latest info, see http://www.ostis.net
dnl #
dnl # Copyright (c) 2010 OSTIS
dnl # 
dnl # OSTIS is free software: you can redistribute it and/or modify
dnl # it under the terms of the GNU Lesser General Public License as published by
dnl # the Free Software Foundation, either version 3 of the License, or
dnl # (at your option) any later version.
dnl #
dnl # OSTIS is distributed in the hope that it will be useful,
dnl # but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl # GNU Lesser General Public License for more details.
dnl # 
dnl # You should have received a copy of the GNU Lesser General Public License
dnl # along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
dnl # -----------------------------------------------------------------------------
dnl ***************************************
dnl *      Author: ALK                    *
dnl * Modified by: IVP & Dmitry Lazurkin  *
dnl ***************************************
dnl
changequote([,])dnl
define([m4define],[builtin([define],[$1],[$2])])dnl
define([m4ifelse],[builtin([ifelse],[$1],[$2],[$3],[$4])])dnl
undefine([ifelse])dnl
dnl
m4define([M4SCPINBRACES],[[[$*]]])dnl
m4define([M4SCPADD_DEF],[m4define([$1],M4SCPINBRACES($1)[[$2]])])dnl
m4define([M4SCPADD_OPTIONAL],[m4ifelse([$1],,[$3],[$2])])dnl
m4define([M4SCPINBRACES_LIST],[[[$*]]])dnl
m4define([M4SCPINDOUBLEBRACES],[[[[$1]]]])dnl
m4define([M4SCPOUTBRACES],$*)dnl
dnl
dnl
m4define([program],[m4ifelse([$1],,[[program]],[dnl
m4define([M4SCPCONSTS],[$1[]_consts])dnl
m4define([M4SCPFILENAME],[builtin([patsubst],__file__,\\,\\\\)])dnl
m4define([M4SCPVARS],[$1[]_vars])dnl
m4define([M4SCPNUMBER],[1])dnl
m4define([M4SCPOPERATORSET],[])dnl
m4define([M4SCPPROGRAMNAME],[$1])dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])dnl
programSCP, init -> [$1] = {
        const_: M4SCPCONSTS[]M4SCPADD_OPTIONAL([$2],[[ = $2]],[ = {}]),
          var_: M4SCPVARS[]M4SCPADD_OPTIONAL([$3],[[ = $3]],[ = {}])
};])])dnl
dnl
m4define([end],[m4ifelse([M4SCPPROGRAMNAME],M4SCPPROGRAMNAME,[[end]],[dnl
m4ifelse(M4SCPOPERATORSET[],,,[M4SCPPROGRAMNAME -> init_: M4SCPOPERATORSET[];])dnl
m4undefine([M4SCPPROGRAMNAME])])])dnl
dnl
m4define([procedure],[m4ifelse([$1],,[[procedure]],[dnl
m4define([M4SCPCONSTS],[$1[]_consts])dnl
m4define([M4SCPVARS],[$1[]_vars])dnl
m4define([M4SCPPRMS],[$1[]_prms])dnl
m4define([M4SCPNUMBER],[1])dnl
m4define([M4SCPFILENAME],[builtin([patsubst],__file__,\\,\\\\)])dnl
m4define([M4SCPOPERATORSET],[])dnl
m4define([M4SCPPROGRAMNAME],[$1])dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])dnl
programSCP -> [$1] = {
        const_: M4SCPCONSTS[]M4SCPADD_OPTIONAL([$2],[[ = $2]],[ = {}]),
          var_: M4SCPVARS[]M4SCPADD_OPTIONAL([$3],[[ = $3]],[ = {}]),
          prm_: M4SCPPRMS[]M4SCPADD_OPTIONAL([$4],[[ = $4]],[ = {}])
};])])dnl
dnl
m4define([M4SCPINC],[m4define([$1],m4incr($1))])dnl
dnl
m4define([M4SCPADD_ELEMENT],[m4define([$1],M4SCPINBRACES_LIST(m4ifelse($1,,,[$1,])[]$2))])dnl
dnl
m4define([catch],[m4ifelse([$1],,[[catch]],[M4SCPADD_DEF([M4SCPERRORTRAP],[,
        error_: $1])dnl[]])])dnl
m4define([label],[m4ifelse([$1],,[[label]],[M4SCPADD_DEF([M4SCPPENDINGLABELS],[$1 = ])dnl[]])])dnl
m4define([M4SCPGOTOXXX],[,
        $1: M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER[]])dnl
m4define([M4SCPTHENELSE],[[,
        $1: $2]])dnl
m4define([M4SCPTHENELSEGOTO],[M4SCPTHENELSE([$1],[$2])m4ifelse([$1],[then_],[M4SCPGOTOXXX(else_)],[M4SCPGOTOXXX(then_)])])dnl
m4define([M4SCPGOTO_ELTH],[m4ifelse([$2],,[M4SCPGOTOXXX([goto_])],[M4SCPTHENELSEGOTO([$1],[$2])])])dnl
m4define([M4SCPGOTOTHENELSE],[m4ifelse([$1],,[M4SCPGOTO_ELTH([else_],[$2])],dnl
[m4ifelse([$2],,[M4SCPGOTO_ELTH([then_],[$1])],dnl
[m4ifelse([$2],[$1],[M4SCPTHENELSE([goto_],[$1])],[M4SCPTHENELSE([then_],[$1])[]M4SCPTHENELSE([else_],[$2])])])])])dnl
dnl
m4define([M4SCPFOREACH], [m4pushdef([M4SCP_ARG])m4pushdef([$1], [[$1]])M4SCP_FOREACH($1,1,[$2],[$3])m4popdef([$1])m4popdef([M4SCP_ARG])])dnl
m4define([M4SCP_FOREACH],dnl
[m4define([M4SCP_ARG], ]M4SCPINDOUBLEBRACES([$]$2)[)[]m4ifelse(M4SCPINBRACES(M4SCP_ARG($3)),M4SCPINBRACES(M4SCP_ARG()), ,dnl
[m4define([$1],[M4SCPINBRACES(M4SCP_ARG($3))])M4SCPOUTBRACES(m4ifelse([$2],[1],[$1],[$4]))[]M4SCP_FOREACH([$1],m4incr($2),[$3],[$4])])])dnl
m4define([M4SCPSPLIT_OPERANDS],[M4SCPFOREACH(M4SCPOPERAND,$1,[[,] 
        M4SCPOPERAND])])dnl
m4define([operator],[m4ifelse([$1],,[[operator]],[M4SCPADD_ELEMENT([M4SCPOPERATORSET],[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER])[]dnl
[$1] -> M4SCPPENDINGLABELS[]M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER = M4SCPINC([M4SCPNUMBER]){
	operator_file_: /"M4SCPFILENAME"/, operator_line_: n/__line__/,
        M4SCPSPLIT_OPERANDS([$2])[]M4SCPERRORTRAP[]dnl
M4SCPGOTOTHENELSE([$3],[$4])
};dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])])])dnl
m4define([return],[m4ifelse([M4SCPPROGRAMNAME],M4SCPPROGRAMNAME,[[return]],[M4SCPADD_ELEMENT([M4SCPOPERATORSET],[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER])[]dnl
[return] -> M4SCPPENDINGLABELS[]M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER = M4SCPINC([M4SCPNUMBER]){
	operator_file_: /"M4SCPFILENAME"/, operator_line_: n/__line__/
};dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])])])dnl
m4define([nop],[m4ifelse([$1],,[[nop]],[M4SCPADD_ELEMENT([M4SCPOPERATORSET],[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER])[]dnl
[nop] -> M4SCPPENDINGLABELS[]M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER = M4SCPINC([M4SCPNUMBER]){
	operator_file_: /"M4SCPFILENAME"/, operator_line_: n/__line__/,
        goto_:[]m4ifelse([$1],,[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER[]],[$1])
};dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])])])dnl
m4define([print_opened_segments],[m4ifelse([$1],[[print_opened_segments]],[[print_opened_segments]],[M4SCPADD_ELEMENT([M4SCPOPERATORSET],[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER])[]dnl
[print_opened_segments] -> M4SCPPENDINGLABELS[]M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER = M4SCPINC([M4SCPNUMBER]){
	operator_file_: /"M4SCPFILENAME"/, operator_line_: n/__line__/
        goto_:[]m4ifelse([$1],,[M4SCPPROGRAMNAME[]_op[]M4SCPNUMBER[]],[$1])
};dnl
m4define([M4SCPPENDINGLABELS],[])dnl
m4define([M4SCPERRORTRAP],[])])])dnl
dnl
m4define(m4scp_define_operator,[m4define([$1],M4SCP[]OUTBRACES([m4ifelse](M4SCPINBRACES(M4SCPINDOUBLEBRACES([$][1]))[,[[[]]],M4SCPINDOUBLEBRACES([$1]),M4SCPOUTBRACES(M4SCPINDOUBLEBRACES([operator([$1],]]M4SCPINBRACES(M4SCPINDOUBLEBRACES([$][1]))[[,]$][2[,]$][3[)]])[))]))])dnl
m4define([define_operator],[m4scp_define_operator($*)])dnl
dnl # standard scp operator set -----------------------
define_operator(call)dnl
define_operator(callReturn)dnl
define_operator(contAssign)dnl
define_operator(contErase)dnl
define_operator(eraseEl)dnl
define_operator(eraseElStr3)dnl
define_operator(eraseElStr5)dnl
define_operator(eraseSetStr3)dnl
dnl define_operator(eraseSetStr5)
define_operator(genEl)dnl
define_operator(genElStr3)dnl
define_operator(genElStr5)dnl
define_operator(idtfAssign)dnl
define_operator(idtfErase)dnl
define_operator(idtfMove)dnl
define_operator(ifCoin)dnl
define_operator(ifEq)dnl
define_operator(ifFormCont)dnl
define_operator(ifFormIdtf)dnl
define_operator(ifGr)dnl
define_operator(ifGrEq)dnl
define_operator(ifType)dnl
define_operator(ifVarAssign)dnl
define_operator(ifNumber)dnl
define_operator(ifString)dnl
dnl define_operator(return) //already defined
define_operator(searchElStr3)dnl
define_operator(searchElStr5)dnl
define_operator(searchSetStr3)dnl
define_operator(searchSetStr5)dnl
define_operator(selectYStr3)dnl
define_operator(selectYStr5)dnl
define_operator(selectNStr3)dnl
define_operator(selectNStr5)dnl
define_operator(waitReturn)dnl
define_operator(varAssign)dnl
define_operator(varErase)dnl
dnl # content scp operator set ------------------------
define_operator(add)dnl
define_operator(ceil)dnl
define_operator(div)dnl
define_operator(floor)dnl
define_operator(mult)dnl
define_operator(pow)dnl
define_operator(sub)dnl
define_operator(toStr)dnl
define_operator(gsub)dnl
dnl # monitoring scp operator set  --------------------
define_operator(print)dnl
define_operator(printEl)dnl
define_operator(printNl)dnl
dnl # system special operator set extensions
define_operator(sys_set_default_segment)dnl
define_operator(sys_get_default_segment)dnl
define_operator(sys_get_autosegment)dnl
define_operator(sys_get_location)dnl
define_operator(sys_send_message)dnl
define_operator(sys_create_segment)dnl
define_operator(sys_open_segment_uri)dnl
define_operator(sys_open_segment)dnl
define_operator(sys_open_dir_uri)dnl
define_operator(sys_open_dir)dnl
define_operator(sys_spin_segment)dnl
define_operator(sys_close_segment)dnl
define_operator(sys_unlink)dnl
define_operator(sys_wait)dnl
define_operator(sys_set_event_handler)dnl
define_operator(sys_open_for_shell)dnl
define_operator(ui_output)dnl
define_operator(ui_sheet_create)dnl
define_operator(ui_messagebox)dnl
define_operator(ui_removeFromSheet)dnl
define_operator(sys_get_shell)dnl
define_operator(sys_send_message)dnl
define_operator(content_write_to_file)dnl
define_operator(content_append_to_file)dnl
define_operator(sys_transform_to_xml)dnl
define_operator(sys_merge_element)dnl
define_operator(sys_copy_element)dnl
define_operator(sys_search)dnl
define_operator(sys_gen)dnl
define_operator(createMutex)dnl
define_operator(releaseMutex)dnl
define_operator(waitMutex)dnl
define_operator(eraseMutex)dnl
define_operator(createStream)dnl
define_operator(writeStream)dnl
define_operator(halt)dnl
define_operator(scpBreakpoint)dnl
define_operator(sys_create_unique_segment)dnl
dnl[]
undefine([define_operator])dnl
undefine([define])dnl
m4define([m4incr],[builtin(incr,[$*])])dnl
undefine([incr])dnl
m4define([m4include],[builtin([include],[$*])])dnl
undefine([include])dnl
m4define([m4pushdef],[builtin([pushdef],[$*])])dnl
undefine([pushdef])dnl
m4define([m4popdef],[builtin([popdef],[$*])])dnl
undefine([popdef])dnl
undefine([changequote])dnl
undefine([traceon])dnl
undefine([traceoff])dnl
undefine([undivert])dnl
undefine([translit])dnl
undefine([sysval])dnl
undefine([syscmd])dnl
undefine([substr])dnl
undefine([sinclude])dnl
undefine([shift])dnl
undefine([regexp])dnl
undefine([patsubst])dnl
undefine([maketemp])dnl
undefine([len])dnl
undefine([indir])dnl
undefine([index])dnl
undefine([ifdef])dnl
undefine([format])dnl
undefine([eval])dnl
undefine([esyscmd])dnl
undefine([errprint])dnl
undefine([dumpdef])dnl
undefine([divnum])dnl
undefine([divert])dnl
undefine([defn])dnl
undefine([decr])dnl
undefine([debugfile])dnl
undefine([debugmode])dnl
undefine([changecom])dnl
m4define([m4undefine],[builtin([undefine],[$*])])dnl
m4undefine([undefine])dnl
dnl[]
