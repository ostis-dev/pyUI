
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
Created on 10.12.2009

@author: Denis Koronchick

Module contains help window. Before using this module you need to call initialize function, 
after you finished to use it don't remember to call shutdown function.
'''

import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui


# help window
_help_window = None
_help_window_static_text = None

# help window text
_modes = {'v': 'view mode', 'e': 'edit mode'}
_help_window_text = ''

# help window size
_help_window_width = 250
_help_window_height = 100

def initialize():
    _createHelpWindow()
    _recreate_help_window_text()

def shutdown():
    _destroyHelpWindow()


def show_help_window():
    """Shows help window for scg-editor
    """
    _help_window.setVisible(True)

def hide_help_window():
    """Hides help window for scg-editor
    """
    _help_window.setVisible(False)

def is_help_window_showed():
    """Check if scg help window is showed
    """
    return _help_window.isVisible()

def toggle_help_window():
    """Toggle help window visibility
    """
    if is_help_window_showed():
        hide_help_window()
    else:
        show_help_window()

def _recreate_help_window_text():
    """Recreating text.
    
    @attention: you need to care about thread synchronization of this function 
    """
    global _help_window_text
    _help_window_text = ''
    
    for mode in _modes.iteritems():
        key, value = mode
        _help_window_text += "#FFCC33%s #FFFFFF - #FFFFCC%s\n" % (key, value)
        if _help_window_static_text:
            _help_window_static_text.setCaption(_help_window_text)

def _createHelpWindow():
    """Creates help window
    """
    global _help_window
    global _help_window_static_text
    _help_window = render_engine.Gui.createWidgetT("Window", "Panel", 
                                                   mygui.IntCoord(5, render_engine.Window.height - 5 - _help_window_height, _help_window_width, _help_window_height), 
                                                   mygui.Align(), "Popup", "")
    _help_window_static_text = _help_window.createWidgetT("StaticText", "StaticText", 
                                            mygui.IntCoord(7, 7, _help_window_width - 14, _help_window_height - 14),
                                            mygui.Align())
#    _help_window_static_text.setCaption(_help_window_text)
    _help_window.setVisible(False)
    _help_window.setAlpha(0.8)
    

def _destroyHelpWindow():
    """Destroye help window
    """
    global _help_window
    render_engine.Gui.destroyWidget(_help_window)