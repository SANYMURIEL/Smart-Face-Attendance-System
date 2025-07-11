# main_app_styles.py
import tkinter as tk # Only if needed for font definitions, not strictly for colors

# --- Style Constants (Theme: Green & White) ---
COLOR_BG = "#F7FFF9"            # Main application background (off-white)
COLOR_CARD_BG = "#FFFFFF"       # Background for main content card (white)
COLOR_WHITE = "#FFFFFF"         # General white color
COLOR_GREEN = "#28A745"         # Primary green color for accents, buttons, title bar
COLOR_GREEN_HOVER = "#218838"   # Darker green for hover effects
COLOR_TEXT_DARK = "#333333"     # Dark text color for labels and entry content
COLOR_TEXT_LIGHT = "#666666"    # Lighter text color for subtitles/descriptions
COLOR_PLACEHOLDER = "#A0A0A0"   # Placeholder text color in entry fields
COLOR_BORDER = "#E0E0E0"        # Border color for entry fields and card
COLOR_BORDER_FOCUS = COLOR_GREEN # Border color when entry field is focused
COLOR_EXIT = COLOR_GREEN        # Close button color (green to match title bar)
COLOR_EXIT_HOVER = "#1E692D"    # Darker green for close button hover
COLOR_ERROR = "#DC3545"         # Red color for error messages

# Define COLOR_TEXT for general use where a specific shade isn't specified
COLOR_TEXT = COLOR_TEXT_DARK # Alias for dark text, common in headers

# Font definitions
FONT_TITLE = ("Segoe UI", 22, "bold") # Main title font
FONT_SUB = ("Segoe UI", 9)            # Subtitle and small text font (used in enroll.py)
FONT_LABEL = ("Segoe UI", 11)        # Label text font (used in enroll.py)
FONT_ENTRY = ("Segoe UI", 11)        # Entry field text font (used in enroll.py)
FONT_BTN = ("Segoe UI", 11, "bold")   # Generic button text font (used in enroll.py)
FONT_BUTTON = FONT_BTN                # Alias FONT_BUTTON to FONT_BTN for main.py (if used)

# For the main application specifically (sidebar, etc.)
COLOR_SIDEBAR = "#333333"    # Dark gray sidebar
COLOR_SIDEBAR_TEXT = "#FFFFFF" # White text in sidebar
COLOR_ACCENT = COLOR_GREEN   # Re-use COLOR_GREEN as accent
FONT_SUBTITLE = ("Segoe UI", 14) # Subtitle font for main page (accueil)
FONT_SIDEBAR = ("Segoe UI", 12) # Sidebar button font