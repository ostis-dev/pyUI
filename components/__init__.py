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
__all__ = ['scg',
			'common',
			'geometry',
			'text',
			'audio',
			'chemistry',
			'flash',
			'graph',
			'image',
			'map',
			'space',
			'video',
			'panels',
			'questions',
			'LUI',
			'math',
			'LUI_voice_output',
            'logic'
            ]
			
modules = [
			'common.menu',
			'panels.mainpanel',
            'panels.userpanel',
#			'panels.windowpanel',
			'panels.taskpanel',
			'scg.base.scg_init',
			'text.text_init',
#			'audio.audio_init',
#			'chemistry.chem_init',
			#'flash.flash_init',
			'graph.graph_init',
			'image.image_init',
#			'map.map_init',
			#'space.space_init',
			'video.video_init',
			'geometry.base.geom_init',
#			'LUI.lui_init',
#			'LUI_voice_output.vo_init',
            'questions.questions_init',
			'math.math_init'
            'logic.logic_init'
]