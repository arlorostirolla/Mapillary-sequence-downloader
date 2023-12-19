import mapillary.interface as mly
import json
import requests
import os, shutil


my_token = "insert access token here"
mly.set_access_token(my_token)
quality_cutoff = 0.5
def get_bbox(path):
    if not os.path.exists(path):
        data = json.loads(
            mly.images_in_bbox(
                bbox={
                    "east": 138.798896,
                    "south": -33.447633,
                    "west": 137.085028,
                    "north": -32.217598,
                },
                max_captured_at="*",
                min_captured_at="2013-01-01",
                image_type="all",
                compass_angle=(0, 360),
            )
        )

        # Save the JSON data to a file (optional)
        with open(path, mode="w") as f:
            json.dump(data, f, indent=4)

        # Create a directory to store the downloaded images
        if not os.path.exists("downloaded_images"):
            os.makedirs("downloaded_images")
    return data

dictionary = {}
def download_dataset(data):
    #data = json.load(data)
    i=0
    # Download and save each image
    for image in data.get("features", []):
        print(i)
        i+=1
        image_key = image["properties"]["id"]
        if not os.path.exists(f"./downloaded_images/{image_key}.jpg"):
            image_data = mly.image_from_key(key= image_key, 
                    fields=['altitude','atomic_scale','camera_parameters', 'camera_type', 
                    'captured_at', 'compass_angle', 'computed_altitude', 'computed_compass_angle',
                    'computed_geometry', 'computed_rotation', 'exif_orientation', 'geometry',
                    'height', 'thumb_1024_url', 'thumb_2048_url', 'merge_cc', 'mesh', 'quality_score',
                    'sequence', 'sfm_cluster', 'width'])

            image_data=eval(image_data)
        
            image_url = image_data['features']['properties']['thumb_2048_url']  # You can adjust the size by changing 'thumb-2048' to another size.
            quality_score = image_data['features']['properties']['quality_score']

            if quality_score >= quality_cutoff:
       
                image_url = image_data['features']['properties']['thumb_2048_url']
                response = requests.get(image_url.replace("\\", ''), stream=True)
                response.raise_for_status()
                with open(f"./downloaded_images/{image_key}.jpg", "wb") as img_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        img_file.write(chunk)

                image_data['file'] = f"./downloaded_images/{image_key}.jpg"
                dictionary[image_key] = image_data

            else:
                print(f"Skipped image {image_key} due to low quality score ({quality_score})")
            
            with open('output.json', mode='w') as out:
                json.dump(dictionary, out, indent=4)
        else:
            print('already downloaded')
    
    return dictionary

'''"510461217588360": {
        "type"
        "features"
            "type"
            "geometry"
            "properties"
                "altitude"
                "atomic_scale"
                "camera_parameters"
                "camera_type"
                "captured_at"
                "compass_angle"
                "computed_altitude"
                "computed_compass_angle"
                "computed_geometry"
                    "type"
                    "coordinates"
                "computed_rotation": 
                "exif_orientation": 
                "height": 
                "thumb_1024_url": 
                "thumb_2048_url": 
                "merge_cc": 
                "mesh": 
                    "id": 
                    "url":      
                "quality_score": 
                "sequence": 
                "sfm_cluster": 
                    "id": 
                    "url": 
                "width":
                "id": 
        "file": 
'''
def organize_sequences(data):
    sequences = dict()
    for entry in data.values():
        sequence_id = entry['features']['properties']['sequence']
        if not sequence_id in sequences.keys():
            sequences[sequence_id] = [entry]
        else:
            sequences[sequence_id].append(entry)

    ordered_sequences = {}
    for sequence_id, info in sequences.items():
        ordered_info = sorted(info, key=lambda x: x['features']['properties']['captured_at'])
        ordered_sequences[sequence_id] = ordered_info

    base_dir = './sequences/'
    
    for sequence_id, ordered_info in ordered_sequences.items():
        sequence_dir = os.path.join(base_dir, sequence_id)
        os.makedirs(sequence_dir, exist_ok=True)

        for item in ordered_info:
            try:
                file_name = item['file']
                shutil.move(file_name, os.path.join(sequence_dir, file_name[-20:]))
            except:
                print('exception')

    with open('ordered_sequences.json', mode="w") as f:
        json.dump(ordered_sequences, f, indent=4)

    return ordered_sequences



if __name__ == '__main__':
    first_time = False
    json_filename = "images_in_bbox_1.json"
    dataset_filename = "output.json"

    if first_time:
        data = get_bbox(json_filename)
    else:    
        with open(json_filename, mode='r') as c:
            data = json.load(c)
    first_time = False
    if first_time:
        dataset_data = download_dataset(data)
    else:
        with open(dataset_filename, mode='r') as c:
            dataset_data = json.load(c)
            

    ordered_sequences = organize_sequences(dataset_data)
