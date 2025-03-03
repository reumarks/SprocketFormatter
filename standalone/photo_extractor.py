import os
import sys
import json
from PIL import Image
from PIL.ExifTags import TAGS

def get_date_taken(image_path):
    """Extracts the 'DateTimeOriginal' from an image's EXIF data."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # Loop through EXIF tags looking for DateTimeOriginal
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        return value
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None

def process_folder(folder_path):
    """Walks through the folder and processes image files."""
    photos = []
    # Define the image extensions you want to process
    valid_extensions = {'.jpg', '.jpeg', '.png', '.heic'}
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                file_path = os.path.join(root, file)
                date_taken = get_date_taken(file_path)
                if(date_taken != None):
                  photos.append({
                     "filename": file,
                     "date": date_taken
                  })
    return photos

def main():
    if len(sys.argv) != 2:
        print("Usage: python photo_extractor.py /path/to/folder")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    if not os.path.isdir(folder_path):
        print("The provided path is not a valid folder.")
        sys.exit(1)
    
    photos = process_folder(folder_path)
    output = {"photos": photos}
    
    # Write JSON output to a file
    output_filename = folder_path + "\_Sprocked_Photo_Data.json"
    with open(output_filename, "w") as json_file:
        json.dump(output, json_file, indent=4)
    
    print(f"JSON file '{output_filename}' generated successfully.")

if __name__ == "__main__":
    main()
