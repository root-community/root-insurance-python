#
# Import this file at the top of every test to have 'root' in context
# e.g. 
# >>> import context	# import of 'root' won't work without this
# >>> from root.insurance import InsuranceClient
#
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from root import insurance
