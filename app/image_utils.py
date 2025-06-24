"""
Improved Image utilities for the Priston Tale Potion Bot
----------------------------------------------
This module provides enhanced utilities for image processing and bar detection.
"""

import os
import time
import logging
import cv2
import numpy as np
from PIL import Image, ImageGrab

logger = logging.getLogger('PristonBot')

def capture_window_screenshot(window_rect):
    """
    Capture a screenshot of a window
    
    Args:
        window_rect: Window rectangle (left, top, right, bottom)
        
    Returns:
        PIL.Image or None if failed
    """
    if not window_rect:
        logger.warning("Cannot capture screenshot: Invalid window rectangle")
        return None
    
    try:
        x, y, right, bottom = window_rect
        width, height = right - x, bottom - y
        
        logger.debug(f"Capturing screenshot of area ({width}x{height}) at ({x}, {y})")
        screenshot = ImageGrab.grab(bbox=(x, y, right, bottom))
        
        return screenshot
    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}", exc_info=True)
        return None

def save_debug_image(image, prefix, extension="png"):
    """
    Save an image for debugging purposes
    
    Args:
        image: PIL.Image or numpy array
        prefix: Prefix for the filename
        extension: Image file extension
        
    Returns:
        Path to saved image or None if failed
    """
    debug_dir = "debug_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        filepath = os.path.join(debug_dir, filename)
        
        # Check if image is numpy array or PIL Image
        if isinstance(image, np.ndarray):
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_to_save = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_to_save = image
            cv2.imwrite(filepath, image_to_save)
        else:
            # Assume PIL Image
            image.save(filepath)
            
        logger.debug(f"Saved debug image to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving debug image: {e}", exc_info=True)
        return None

def extract_bar_region(screenshot, bar):
    """
    Extract a bar region from a screenshot
    
    Args:
        screenshot: Screenshot as numpy array
        bar: BarSelector object
        
    Returns:
        Bar region as numpy array or None if failed
    """
    try:
        # Get the screen coordinates relative to the screenshot
        if not hasattr(bar, 'screen_x1') or not hasattr(bar, 'screen_y1'):
            logger.warning(f"Bar {bar.title} does not have screen coordinates set")
            return None
            
        # Calculate relative position
        window_x, window_y = 0, 0
        
        # If we have window coordinates, use them to calculate relative position
        if hasattr(bar, 'game_window_x') and hasattr(bar, 'game_window_y'):
            window_x = bar.game_window_x
            window_y = bar.game_window_y
            
        # Calculate relative coordinates
        x1 = bar.screen_x1 - window_x
        y1 = bar.screen_y1 - window_y
        x2 = bar.screen_x2 - window_x
        y2 = bar.screen_y2 - window_y
        
        logger.debug(f"Extracting {bar.title} bar from relative coordinates: ({x1},{y1})-({x2},{y2})")
        
        # Ensure coordinates are within screenshot bounds
        height, width = screenshot.shape[0], screenshot.shape[1]
        
        if x1 >= width or y1 >= height or x2 <= 0 or y2 <= 0:
            logger.warning(f"Bar coordinates ({x1},{y1})-({x2},{y2}) are outside screenshot bounds ({width}x{height})")
            # Save the screenshot for debugging
            save_debug_image(screenshot, f"{bar.title.lower()}_screenshot_out_of_bounds")
            return None
            
        # Clip coordinates to screenshot bounds
        x1 = max(0, min(x1, width-1))
        y1 = max(0, min(y1, height-1))
        x2 = max(0, min(x2, width-1))
        y2 = max(0, min(y2, height-1))
        
        # Extract the region
        region = screenshot[y1:y2, x1:x2]
        
        # Log the size of the extracted region
        if hasattr(region, 'shape'):
            height, width = region.shape[0], region.shape[1]
            logger.debug(f"Extracted {bar.title} bar region: {width}x{height} pixels")
            
            # Save the extracted region for debugging
            save_debug_image(region, f"{bar.title.lower()}_bar_region")
        else:
            logger.warning(f"Extracted {bar.title} bar region has invalid shape")
            
        return region
    except Exception as e:
        logger.error(f"Error extracting bar region: {e}", exc_info=True)
        return None

def get_bar_percentage(bar, screenshot_np):
    """
    Calculate the percentage of a bar that is filled
    
    Args:
        bar: BarSelector object
        screenshot_np: Screenshot as numpy array
        
    Returns:
        Percentage of bar filled (0-100) or 100 if failed
    """
    try:
        # Extract bar region from screenshot
        bar_region = extract_bar_region(screenshot_np, bar)
        if bar_region is None or bar_region.size == 0:
            logger.warning(f"Could not extract {bar.title} bar region or region is empty")
            return 100
            
        # Generate preview image for the UI
        try:
            # Convert to PIL for the UI
            rgb_region = cv2.cvtColor(bar_region, cv2.COLOR_BGR2RGB)
            bar.preview_image = Image.fromarray(rgb_region)
            logger.debug(f"Updated preview image for {bar.title} bar")
        except Exception as e:
            logger.error(f"Error updating preview image: {e}")
        
        # Convert to multiple color spaces for robust detection
        hsv = cv2.cvtColor(bar_region, cv2.COLOR_RGB2HSV)
        
        # Create masks based on bar color with optimized ranges for Priston Tale
        if bar.title == "Health":  # Red
            # Optimized range for Priston Tale's red health bar
            lower1 = np.array([0, 70, 70])
            upper1 = np.array([10, 255, 255])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            
            lower2 = np.array([160, 70, 70])
            upper2 = np.array([180, 255, 255])
            mask2 = cv2.inRange(hsv, lower2, upper2)
            
            mask = mask1 | mask2
            logger.debug("Using optimized red color detection for Health bar")
            
        elif bar.title == "Mana":  # Blue
            # Optimized range for Priston Tale's blue mana bar
            lower = np.array([90, 70, 70])
            upper = np.array([130, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            logger.debug("Using optimized blue color detection for Mana bar")
            
        else:  # Green (Stamina)
            # Optimized range for Priston Tale's green stamina bar
            lower = np.array([40, 70, 70])
            upper = np.array([80, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            logger.debug("Using optimized green color detection for Stamina bar")
        
        # Save the mask for debugging
        save_debug_image(mask, f"{bar.title.lower()}_mask")
        
        # Apply morphological operations to improve mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Save the improved mask
        save_debug_image(mask, f"{bar.title.lower()}_mask_improved")
        
        # Count colored pixels
        colored_pixels = cv2.countNonZero(mask)
        total_pixels = bar_region.shape[0] * bar_region.shape[1]
        
        # Calculate percentage
        if total_pixels > 0:
            percentage = (colored_pixels / total_pixels) * 100
        else:
            percentage = 0
            
        logger.debug(f"{bar.title} bar: {colored_pixels}/{total_pixels} pixels = {percentage:.1f}%")
        return percentage
        
    except Exception as e:
        logger.error(f"Error calculating {bar.title} bar percentage: {e}", exc_info=True)
        return 100  # Default to full to avoid unnecessary potion usage

def draw_debug_overlay(screenshot, bars, percentages):
    """
    Draw a debug overlay on the screenshot showing detected bars
    
    Args:
        screenshot: Screenshot as PIL.Image
        bars: List of BarSelector objects
        percentages: List of detected percentages
        
    Returns:
        Screenshot with debug overlay as PIL.Image
    """
    try:
        # Convert PIL Image to OpenCV format
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Colors for each bar (BGR format for OpenCV)
        colors = {
            "Health": (0, 0, 255),    # Red (BGR)
            "Mana": (255, 0, 0),      # Blue (BGR)
            "Stamina": (0, 255, 0)    # Green (BGR)
        }
        
        # Draw rectangles and percentage text for each bar
        for i, bar in enumerate(bars):
            if hasattr(bar, 'screen_x1') and all([bar.screen_x1, bar.screen_y1, bar.screen_x2, bar.screen_y2]):
                # Calculate relative coordinates for drawing
                window_x, window_y = 0, 0
                if hasattr(bar, 'game_window_x') and hasattr(bar, 'game_window_y'):
                    window_x = bar.game_window_x
                    window_y = bar.game_window_y
                
                # Convert screen coordinates to relative coordinates
                x1 = bar.screen_x1 - window_x
                y1 = bar.screen_y1 - window_y
                x2 = bar.screen_x2 - window_x
                y2 = bar.screen_y2 - window_y
                
                # Draw rectangle around bar
                cv2.rectangle(img, (x1, y1), (x2, y2), 
                            colors.get(bar.title, (255, 255, 255)), 2)
                
                # Draw percentage text
                if i < len(percentages):
                    text = f"{bar.title}: {percentages[i]:.1f}%"
                    cv2.putText(img, text, (x1, y1 - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors.get(bar.title, (255, 255, 255)), 2)
        
        # Convert back to PIL Image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = Image.fromarray(img_rgb)
        
        # Save the debug image
        save_debug_image(result, "debug_overlay")
        
        return result
    except Exception as e:
        logger.error(f"Error drawing debug overlay: {e}", exc_info=True)
        return screenshot