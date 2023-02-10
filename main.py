#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-

import logging
from python.mainloop import Appli

#=============================================================================

if __name__ == '__main__':

	logging.info("LApp: before run()")
	Appli(bmenu=False,bframe=False,title='wwtool').run()
	logging.info("LApp: after run()")

#=============================================================================
