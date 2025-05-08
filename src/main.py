#!/usr/bin/env python3
"""
Muninn Bot - Main entry point
"""

import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

if __name__ == "__main__":
    from muninn.bot import main
    main() 