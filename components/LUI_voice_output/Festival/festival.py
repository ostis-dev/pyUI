import os

''' This is the wrapper for the popular voice engine Festival
	Current build supports russian language by default
'''

def say(sayText):
	os.system('festival.exe --libdir "lib" -b "(begin (voice_msu_ru_nsh_clunits) (SayText \"'+sayText+'\" nil))"')