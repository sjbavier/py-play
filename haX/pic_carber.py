import re, zlib, cv2
from pathlib import Path

from scapy.all import *

home = str(Path.home())

pictures_directory = f'{home}/Pictures/pic_carver/pictures'
faces_directory = f'{home}/Pictures/pic_carver/faces'

pcap_file = 'bhp.pcap'

def http_assembler(pcap_file):

    carved_images = 0
    faces_detected = 0
    
    a = rdpcap(pcap_file)

    sessions = a.sessions()

    for session in sessions:
        
        http_payload = ''

        for packet in sessions[session]:

            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:

                    # reassemble the stream
                    http_payload += str(packet[TCP].payload)

            except:
                pass
        
        headers = get_http_headers(http_payload)

        if headers is None:
            continue

        image,image_type = extract_image(headers, http_payload)

        if image is not None and image_type is not None:
            # store the image
            file_name = f'{pcap_file}-pic_carver_{carved_images}.{image_type}'

            fd = open(f'{pictures_directory}/{file_name}','wb')

            fd.write(image)
            fd.close()

            carved_images += 1

            # now attempt face detection
            try:
                result = face_detect(f'{pictures_directory}/{file_name}', file_name)

                if result is True:
                    face_detected += 1
            
            except:
                pass
        
    return carved_images, faces_detected

carved_images, faces_detected = http_assembler(pcap_file)

print(f'Extracted: {carved_images} images')
print(f'Detected: {faces_detected} faces')