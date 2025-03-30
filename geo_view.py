import tkinter as tk
from tkinter import ttk
from osgeo import gdal
import numpy as np
from PIL import Image, ImageTk

class GeoTIFFViewer:
    def __init__(self, root, file_path, max_size=(600, 400)):
        self.root = root
        self.root.title("Geo Tiff Viewer")
        self.root.configure(bg="#2a3439")
        self.window_width = 800
        self.window_height = 600
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        # Load GeoTIFF
        self.dataset = gdal.Open(file_path)
        self.geo_transform = self.dataset.GetGeoTransform()
        
        # Convert to image
        self.image = self.read_geotiff_as_image()
        self.tk_image = ImageTk.PhotoImage(self.image)
        
        # Top Frame for Coordinates
        self.coord_frame = tk.Frame(root, bg="#2a3439")
        self.coord_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.lat_label = tk.Label(self.coord_frame, text="Latitude:", fg="white", bg="#2a3439")
        self.lat_label.pack(side=tk.LEFT, padx=15)
        self.lat_entry = tk.Entry(self.coord_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.lat_entry.pack(side=tk.LEFT)
        
        self.lon_label = tk.Label(self.coord_frame, text="Longitude:", fg="white", bg="#2a3439")
        self.lon_label.pack(side=tk.LEFT, padx=15)
        self.lon_entry = tk.Entry(self.coord_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.lon_entry.pack(side=tk.LEFT)
        
        self.x_label = tk.Label(self.coord_frame, text="X:", fg="white", bg="#2a3439")
        self.x_label.pack(side=tk.LEFT, padx=15)
        self.x_entry = tk.Entry(self.coord_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.x_entry.pack(side=tk.LEFT)
        
        self.y_label = tk.Label(self.coord_frame, text="Y:", fg="white", bg="#2a3439")
        self.y_label.pack(side=tk.LEFT, padx=15)
        self.y_entry = tk.Entry(self.coord_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.y_entry.pack(side=tk.LEFT)

        # Canvas setup and loading image 
        self.load_and_display_image(file_path, max_size)

        # Event bindings
        self.canvas.bind("<Motion>", self.track_mouse)


       # **New Frame Below Image for Input Fields and Button**
        self.mark_frame = tk.Frame(self.root, bg="#2a3439")
        self.mark_frame.pack(pady=10, after=self.canvas)  # Place under the image

        # Latitude Input
        self.enter_latitude_label = tk.Label(self.mark_frame, text="Latitude:", fg="white", bg="#2a3439")
        self.enter_latitude_label.pack(side=tk.LEFT, padx=5)
        self.enter_latitude_entry = tk.Entry(self.mark_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.enter_latitude_entry.pack(side=tk.LEFT)

        # Longitude Input
        self.enter_longitude_label = tk.Label(self.mark_frame, text="Longitude:", fg="white", bg="#2a3439")
        self.enter_longitude_label.pack(side=tk.LEFT, padx=5)
        self.enter_longitude_entry = tk.Entry(self.mark_frame, width=20, bg="#2a3439", fg="white", border=1)
        self.enter_longitude_entry.pack(side=tk.LEFT)

        # Mark Button
        self.mark_button = tk.Button(self.mark_frame, command=self.mark_location, text="Mark", bg="#4CAF50", fg="white")
        self.mark_button.pack(side=tk.LEFT, padx=10)



    def load_and_display_image(self, image_path, max_size):
        original_image = Image.open(image_path)

        # Resize the image while maintaining aspect ratio
        original_image.thumbnail(max_size)

        self.tk_image = ImageTk.PhotoImage(original_image)

        # Get new image dimensions
        img_width, img_height = self.tk_image.width(), self.tk_image.height()

        # Create a canvas with image dimensions
        self.canvas = tk.Canvas(self.root, width=img_width, height=img_height, bg="#2b2b2b", border=1)
        self.canvas.pack(pady=20)

        # Calculate centered position
        x_center = img_width / 2
        y_center = img_height / 2

        # Create and place image
        self.image_id = self.canvas.create_image(x_center+3, y_center+3, anchor=tk.CENTER, image=self.tk_image)
    
    def read_geotiff_as_image(self):
        r = self.dataset.GetRasterBand(1).ReadAsArray()
        g = self.dataset.GetRasterBand(2).ReadAsArray()
        b = self.dataset.GetRasterBand(3).ReadAsArray()

        # Stack into an (H, W, 3) array
        rgb_array = np.dstack((r, g, b))

        # Convert to image
        image = Image.fromarray(rgb_array.astype(np.uint8))
        return image

    def track_mouse(self, event):
        x, y = event.x, event.y
        lat, lon = self.pixel_to_latlon(x, y)

        # Update entries with correct indices
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))
        self.lat_entry.delete(0, tk.END)
        self.lat_entry.insert(0, f"{lat:.6f}")
        self.lon_entry.delete(0, tk.END)
        self.lon_entry.insert(0, f"{lon:.6f}")

    def pixel_to_latlon(self, x, y):
        lon = self.geo_transform[0] + x * self.geo_transform[1]
        lat = self.geo_transform[3] + y * self.geo_transform[5]
        return lat, lon

    def latlon_to_pixel(self, lat, lon):
        """ Convert latitude/longitude to pixel coordinates. """
        inv_transform = gdal.InvGeoTransform(self.geo_transform)
        x, y = gdal.ApplyGeoTransform(inv_transform, lon, lat)
        return int(x), int(y)

    def mark_location(self):
        """ Mark user-defined latitude/longitude on the image. """
        lat_text = self.enter_latitude_entry.get().strip()
        lon_text = self.enter_longitude_entry.get().strip()

        # Validate input: Ensure fields are not empty and contain valid numbers
        if not lat_text or not lon_text:
            print("Error: Latitude and Longitude fields cannot be empty.")
            return

        try:
            lat = float(lat_text)
            lon = float(lon_text)
        except ValueError:
            print("Error: Invalid latitude or longitude. Please enter numeric values.")
            return

        # Convert lat/lon to pixel coordinates
        x, y = self.latlon_to_pixel(lat, lon)

        # Adjust for image positioning on canvas
        image_x, image_y = self.canvas.coords(self.image_id)
        img_width = self.tk_image.width()
        img_height = self.tk_image.height()
        img_top_left_x = image_x - (img_width / 2)
        img_top_left_y = image_y - (img_height / 2)

        x_on_canvas = img_top_left_x + x
        y_on_canvas = img_top_left_y + y

        # Draw marker on canvas
        # Cross size
        cross_size = 10  

        # Draw cross: Two intersecting lines
        self.canvas.create_line(x_on_canvas - cross_size, y_on_canvas - cross_size, 
                                x_on_canvas + cross_size, y_on_canvas + cross_size, 
                                fill="red", width=2)
        self.canvas.create_line(x_on_canvas - cross_size, y_on_canvas + cross_size, 
                                x_on_canvas + cross_size, y_on_canvas - cross_size, 
                                fill="red", width=2)




# Run the application
if __name__ == "__main__":
    file_path = "testGeoTiff.tif"  # Update with actual path
    root = tk.Tk()
    app = GeoTIFFViewer(root, file_path)
    root.mainloop()
