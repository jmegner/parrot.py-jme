from lib.detection_strategies import *
import threading
import numpy as np
import pyautogui
from pyautogui import press, hotkey, click, scroll, typewrite, moveRel, moveTo, position, keyUp, keyDown, mouseUp, mouseDown
from time import sleep
from subprocess import call
from lib.system_toggles import toggle_eyetracker, turn_on_sound, mute_sound, toggle_speechrec
from lib.pattern_detector import PatternDetector
from lib.heroes_grammar import *
import os
import pythoncom

class StarcraftMode:
			
	def __init__(self, modeSwitcher):
	
		self.mode = "regular"
		self.modeSwitcher = modeSwitcher
		self.detector = PatternDetector({
			'select': {
				'strategy': 'rapid',
				'sound': 'sound_s',
				'percentage': 70,
				'intensity': 800,
				'throttle': 0.01
			},
			'rightclick': {
				'strategy': 'rapid',
				'sound': 'cluck',
				'percentage': 50,
				'intensity': 1000,
				'throttle': 0.1
			},
			'attack': {
				'strategy': 'rapid',
				'sound': 'whistle',
				'percentage': 70,
				'intensity': 1000,
				'throttle': 0.1
			},
			'control': {
				'strategy': 'rapid',
				'sound': 'sound_oh',
				'percentage': 43,
				'intensity': 5000,
				'throttle': 0.1
			},
			'shift': {
				'strategy': 'rapid',
				'sound': '????',
				'percentage': 43,
				'intensity': 5000,
				'throttle': 0.1
			},
			'camera': {
				'strategy': 'rapid',
				'sound': 'sound_uuh',
				'percentage': 50,
				'intensity': 1000,
				'throttle': 0.1
			},
			'q': {
				'strategy': 'rapid',
				'sound': 'sound_ooh',
				'percentage': 60,
				'intensity': 2000,
				'throttle': 0.1
			},
			'w': {
				'strategy': 'rapid',
				'sound': 'sound_f',
				'percentage': 70,
				'intensity': 1500,
				'throttle': 0.1
			},
			'grid_ability': {
				'strategy': 'rapid',
				'sound': 'sound_ah',
				'percentage': 60,
				'intensity': 3000,
				'throttle': 0.05
			},
			'r': {
				'strategy': 'rapid',
				'sound': 'sound_sh',
				'percentage': 35,
				'intensity': 4000,
				'throttle': 0.1
			},
			'numbers': {
				'strategy': 'rapid',
				'sound': 'sound_ie',
				'percentage': 70,
				'intensity': 1000,
				'throttle': 0.1
			},
			'skip_cutscenes': {
				'strategy': 'rapid',
				'sound': 'hotel_bell',
				'percentage': 60,
				'intensity': 500,
				'throttle': 0.3
			}
		})

		self.pressed_keys = []
		self.should_follow = False
		self.should_drag = False
		self.last_control_group = -1
		self.ability_selected = False
		self.ctrlKey = False
		self.shiftKey = False
		
		self.hold_key = ""

	def start( self ):
		mute_sound()
		toggle_eyetracker()
		
	def cast_ability( self, ability ):
		self.press_ability( ability )
		self.ability_selected = True
	
	def hold_shift( self, shift ):
		if( self.shiftKey != shift ):
			if( shift == True ):
				keyDown('shift')
				print( 'Holding SHIFT' )
			else:
				keyUp('shift')
				print( 'Releasing SHIFT' )
				
		self.shiftKey = shift	
	
	def hold_control( self, ctrlKey ):
		if( self.ctrlKey != ctrlKey ):
			if( ctrlKey == True ):
				keyDown('ctrl')
				print( 'Holding CTRL' )
			else:
				keyUp('ctrl')
				print( 'Releasing CTRL' )
				
		self.ctrlKey = ctrlKey
	
	def release_hold_keys( self ):
		self.ability_selected = False	
		self.hold_control( False )
		self.hold_shift( False )
	
	def handle_input( self, dataDicts ):
		self.detector.tick( dataDicts )
		
		## Mouse actions
		# Selecting units
		selecting = self.detector.detect( "select" )
		self.drag_mouse( selecting )
		if( selecting ):
			self.release_hold_keys()
		elif( self.detector.detect( "rightclick" ) ):
		
			# Cast selected ability or Ctrl+click
			if( self.detect_command_area() or self.ability_selected == True or self.ctrlKey == True  ):
				click(button='left')
			else:
				click(button='right')
				
			self.release_hold_keys()
			
		# CTRL KEY holding
		elif( self.detector.detect( "control" ) ):
			self.hold_control( True )

		## Attack move / Patrol move
		quadrant3x3 = self.detector.detect_mouse_quadrant( 3, 3 )		
		if( self.detector.detect( "attack" ) ):
			if( quadrant3x3 <= 3 ):
				self.cast_ability( 'p' )
			else:
				self.cast_ability( 'a' )
		## Press Q
		elif( self.detector.detect( "q" ) ):
			self.cast_ability( 'q' )
		## Press W
		elif( self.detector.detect( "w") ):
			self.cast_ability( 'w' )
		## Press R ( Burrow )
		elif( self.detector.detect( "r") ):
			self.press_ability( 'r' )
		elif( self.detector.detect( "skip_cutscenes" ) ):
			self.press_ability( 'esc' )
			
		## Move the camera
		if( self.detector.detect( "camera" ) ):
			self.camera_movement( quadrant3x3 )
			
		## Press Grid ability
		elif( self.detector.detect("grid_ability") ):
			quadrant4x3 = self.detector.detect_mouse_quadrant( 4, 3 )
			self.use_ability( quadrant4x3 )
			self.release_hold_keys()
			
		## Press control group
		elif( self.detector.detect( "numbers" ) ):
			self.use_control_group( quadrant3x3 )
			self.release_hold_keys()
			
		return self.detector.tickActions
		
	def use_control_group( self, quadrant ):
		if( quadrant == 1 ):
			self.press_ability('1')
		elif( quadrant == 2 ):
			self.press_ability('2')
		elif( quadrant == 3 ):
			self.press_ability('3')
		elif( quadrant == 4 ):
			self.press_ability('4')
		elif( quadrant == 5 ):
			self.press_ability('5')
		elif( quadrant == 6 ):
			self.press_ability('6')			
		elif( quadrant == 7 ):
			self.press_ability('7')
		elif( quadrant == 8 ):
			self.press_ability('8')			
		elif( quadrant == 9 ):
			self.press_ability('9')
			
		self.last_control_group = quadrant
		
	def use_ability( self, quadrant ):
		if( quadrant == 1 ):
			self.press_ability('q')
		elif( quadrant == 2 ):
			self.press_ability('w')
		elif( quadrant == 3 ):
			self.press_ability('e')
		elif( quadrant == 4 ):
			self.press_ability('r')
		elif( quadrant == 5 ):
			self.press_ability('a')
		elif( quadrant == 6 ):
			self.press_ability('s')			
		elif( quadrant == 7 ):
			self.press_ability('d')
		elif( quadrant == 8 ):
			self.press_ability('f')			
		elif( quadrant == 9 ):
			self.press_ability('z')
		elif( quadrant == 10 ):
			self.press_ability('x')
		elif( quadrant == 11 ):
			self.press_ability('c')
		elif( quadrant == 12 ):
			self.press_ability('v')
		
	def press_ability( self, key ):
		print( "pressing " + key )
		press( key )
		self.hold_control( False )
		
	def camera_movement( self, quadrant ):
		## Move camera to kerrigan when looking above the UI
		if( quadrant < 4 ):
			self.press_ability( "f1" )
		
		elif( quadrant > 3 and quadrant < 7 ):
			self.press_ability( "backspace" )
		
		## Move camera to danger when when looking at the minimap or unit selection
		elif( quadrant == 7 or quadrant == 8 ):
			self.press_ability( "space" )
			
		## Follow the unit when looking near the command card
		elif( quadrant == 9 ):
			self.press_ability( "." )
				
	# Detect when the cursor is inside the command area
	def detect_command_area( self ):
		return self.detector.detect_inside_minimap( 1521, 815, 396, 266 )
				
	# Drag mouse for selection purposes
	def drag_mouse( self, should_drag ):
		if( self.should_drag != should_drag ):
			if( should_drag == True ):
				mouseDown()
			else:
				mouseUp()
				
		self.should_drag = should_drag

	def exit( self ):
		self.mode = "regular"
		turn_on_sound()
		toggle_eyetracker()
		