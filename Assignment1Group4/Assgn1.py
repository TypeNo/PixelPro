import cv2
import numpy as np
import tkinter as tk
from tkinter import Listbox, Button, Scrollbar

# Create a list to store ROI coordinates
rois = []

# Create a dictionary to store the brightness levels for each ROI
roi_brightness_levels = {}

# Define a global variable to control brightness update
updating_brightness = False

# Function to select multiple ROIs
def select_roi():
    global rois

    roi = cv2.selectROI("Select ROI", image)
    
    # Check if a valid ROI was selected (not canceled)
    if roi != (0, 0, 0, 0):
        rois.append(roi)
        roi_brightness_levels[len(rois) - 1] = 0  # Set initial brightness level to 0 for the new ROI
        update_roi_list()

    cv2.destroyWindow("Select ROI")

# Function to update the ROI list
def update_roi_list():
    roi_listbox.delete(0, tk.END)
    for i, roi in enumerate(rois):
        brightness = roi_brightness_levels.get(i, 0)
        roi_listbox.insert(tk.END, f"ROI {i+1}: {roi} (Brightness: {brightness})")
    update_processed_image()

# Function to delete the selected ROIs
def delete_selected_rois():
    selected_indices = roi_listbox.curselection()
    if selected_indices:
        selected_indices = [int(i) for i in selected_indices]
        selected_indices.sort(reverse=True)  # Reverse to avoid changing indices
        for index in selected_indices:
            del rois[index]
            # Delete the brightness level for the deleted ROI
            if index in roi_brightness_levels:
                del roi_brightness_levels[index]
        update_roi_list()

# Function to draw dashed lines around selected ROIs
def draw_frames_around_selected_rois(image_copy, selected_indices, dash_length=5):
    for i in selected_indices:
        x, y, w, h = rois[i]
        color = (0, 255, 0)  # Green color

        # Draw the top horizontal line
        for x0 in range(x, x + w, dash_length * 2):
            x1 = min(x0 + dash_length, x + w)
            cv2.line(image_copy, (x0, y), (x1, y), color, 1)

        # Draw the bottom horizontal line
        for x0 in range(x, x + w, dash_length * 2):
            x1 = min(x0 + dash_length, x + w)
            cv2.line(image_copy, (x0, y + h - 1), (x1, y + h - 1), color, 1)

        # Draw the left vertical line
        for y0 in range(y, y + h, dash_length * 2):
            y1 = min(y0 + dash_length, y + h)
            cv2.line(image_copy, (x, y0), (x, y1), color, 1)

        # Draw the right vertical line
        for y0 in range(y, y + h, dash_length * 2):
            y1 = min(y0 + dash_length, y + h)
            cv2.line(image_copy, (x + w - 1, y0), (x + w - 1, y1), color, 1)

# Function to update the processed image based on selected ROIs and their brightness levels
def update_processed_image():
    image_copy = np.copy(original_image)

    for i, roi in enumerate(rois):
        x, y, w, h = roi
        
        # Get the brightness level for this ROI
        brightness_level = roi_brightness_levels.get(i, 0)  

        selected_region = image_copy[y:y + h, x:x + w]

        # Apply brightness adjustment
        adjusted_region = cv2.multiply(selected_region, (1, 1, 1, 1), scale=1 + brightness_level / 100.0)
        
        image_copy[y:y + h, x:x + w] = adjusted_region

    selected_indices = roi_listbox.curselection()
    if selected_indices:
        selected_indices = [int(i) for i in selected_indices]
        draw_frames_around_selected_rois(image_copy, selected_indices)

    cv2.imshow("Processed Image", image_copy)

# Function to draw dashed frames around the selected ROI when an item is clicked
def draw_frame_on_list_click(event):
    image_copy = np.copy(original_image)
    
    for i, roi in enumerate(rois):
        x, y, w, h = roi
        brightness_level = roi_brightness_levels.get(i, 0)
        selected_region = image_copy[y:y + h, x:x + w]

        # Apply brightness adjustment
        adjusted_region = cv2.addWeighted(selected_region, 1 + brightness_level / 100.0, selected_region, 0, 0)

        image_copy[y:y + h, x:x + w] = adjusted_region

    selected_indices = roi_listbox.curselection()
    if selected_indices:
        selected_indices = [int(i) for i in selected_indices]

        # Draw dashed frames for selected ROIs
        draw_frames_around_selected_rois(image_copy, selected_indices)

    cv2.imshow("Processed Image", image_copy)

# Function to update the brightness level for the selected ROI when the brightness slider is adjusted
def update_brightness_level(event):
        global updating_brightness
        if updating_brightness:
            selected_indices = roi_listbox.curselection()
            if selected_indices:
                brightness = brightness_slider.get()
                for i in selected_indices:
                    roi_brightness_levels[i] = brightness
                update_processed_image()


# Function to set the brightness level of the selected ROI to 0, effectively blackening it
def blacken_selected_roi():
    selected_indices = roi_listbox.curselection()
    if selected_indices:
        for i in selected_indices:
            roi_brightness_levels[i] = -100
        update_processed_image()

# Create a Tkinter window for GUI
window = tk.Tk()
window.title("ROI Selection")

# Load an image
image = cv2.imread('Images/lenna.tif')
original_image = np.copy(image)
cv2.imshow("Original Image", image)

# Create buttons for ROI selection, deletion, and processing
select_roi_button = tk.Button(window, text="Select ROI", command=select_roi)
select_roi_button.pack()

# Create a slider for brightness adjustment
brightness_slider = tk.Scale(window, label="Brightness", from_=-100, to=100, orient="horizontal")
brightness_slider.pack()

# Function to set updating_brightness to True when the slider is clicked
def slider_click(event):
    global updating_brightness
    updating_brightness = True

# Function to set updating_brightness to False when the slider is released
def slider_release(event):
    global updating_brightness
    updating_brightness = False

# Bind the slider to respond to mouse clicks and releases
brightness_slider.bind("<ButtonPress-1>", slider_click)
brightness_slider.bind("<ButtonRelease-1>", slider_release)

# Bind the update_brightness_level function to the slider's event
brightness_slider.bind("<Motion>", update_brightness_level)

# Create a listbox to display selected ROIs with multiple selection
roi_listbox = Listbox(window, selectmode=tk.MULTIPLE)
roi_listbox.pack()

# Create a scrollbar for the listbox
scrollbar = Scrollbar(window, command=roi_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
roi_listbox.config(yscrollcommand=scrollbar.set)

# Create a button to blacken the selected ROI
blacken_roi_button = tk.Button(window, text="Blacken Selected ROI", command=blacken_selected_roi)
blacken_roi_button.pack()

# Create a button for deleting selected ROIs
delete_roi_button = tk.Button(window, text="Delete Selected ROI(s)", command=delete_selected_rois)
delete_roi_button.pack()


# Bind the draw_frame_on_list_click function to the listbox's <<ListboxSelect>> event
roi_listbox.bind("<<ListboxSelect>>", draw_frame_on_list_click)

# Create a window to display the processed image
cv2.namedWindow("Processed Image")

# Update the processed image initially
update_processed_image()

# Start the GUI loop
window.mainloop()

cv2.destroyAllWindows()

