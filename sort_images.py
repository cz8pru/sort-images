#!/bin/python3
import os
import os.path
import shutil
import exifread
import logging
import argparse

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "[%(levelname)8s]:%(filename)10s:%(lineno)4s:%(funcName)20s():     %(message)s"


    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
	




def mkdir_custom(path, dry_run=False):
	if dry_run:
		logger.debug(f'Make directory: {path}')
		return
	else:
		os.makedirs(path, exist_ok=True)


def move_custom(src, dst, dry_run=False):
	if dry_run:
		logger.debug(f'Move file from {src} to {dst}')
		return
	else:
		shutil.move(src, dst)

def get_images(input_images_path, images_limit=10000):
	max_processed_images = 0

	# Recursively walk through all subdirectories and store the path + name of the jpg images
	images = []
	for root, dirs, files in os.walk(input_images_path):
		
		if "@eaDir" in root:
			logger.warning(f"Skipping file {f} in {root} because it is an @eaDir file.")
			continue

		for f in files:
			# I'm only interested in pictures
			if f.endswith(".jpg"):
				tmp = os.path.join(root, f)
				images.append(tmp)
				logger.debug(tmp)
				max_processed_images += 1

				if max_processed_images > images_limit:
					logger.warning(f"Maximum number of images to process reached: {max_processed_images}.")
					return images
	return images


def main(input_images_path, output_images_path="./tmp", dry_run=False):
	'''
	Sorts images by date taken, using EXIF tags.
	Images are moved to a folder with the format YYYY.MM.DD.
	Images without EXIF tags are moved to a folder named 0000.

	:param input_images_path: Path where images to be organized are located.
	'''

	fail_count = 0
	success_count = 0
	processed_images = 0

	# Path for sorted files to be stored
	# If it doesn't exist, creates a new one
	if not os.path.exists(output_images_path):
		os.mkdir(output_images_path)


	images = get_images(input_images_path)

	# Extracts the date an image was taken and moves it to a folder with the format YYYY.MM.DD
	# If the image doesn't have EXIF tags, sends it to a folder named 0000
	for img in images:
		processed_images += 1
		with open(img, "rb") as file:
			tags = exifread.process_file(file, details=False, stop_tag="DateTimeOriginal")
			date_path = "0000"
			try:
				date_list = str(tags["EXIF DateTimeOriginal"])[:10].split(":")
				date_path = os.path.join(date_list[0], date_list[1], date_list[2])
				logger.debug(f"Image {img} has EXIF tags. Date: {date_path}")
				success_count += 1
			except:
				logger.warning(f"Image {img} does not have EXIF tags.")
				fail_count += 1
				
		dest_image = os.path.basename(img)

		destination = os.path.join(output_images_path, date_path, dest_image)
		
		mkdir_custom(os.path.join(output_images_path, date_path), dry_run)
		move_custom(img, destination, dry_run)

		logger.info(f"Processed {processed_images}/{len(images)} images. ({img} -> {destination})")


	print("="*120 + "\n\n")
	logger.info(f"Sorted         {success_count:>10} files.")
	logger.info(f"Failed to sort {fail_count:>10} files.")
	print("="*120)
	logger.info(f"Total          {processed_images:>10} files in total.")



logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser(
	prog='sort_images',
	description='A simple python script to sort pictures by date taken.',
	epilog='Originaly from https://github.com/vitords/sort-images/'
	)
parser.add_argument('input_images_path')
parser.add_argument('output_images_path', nargs='?', default="./tmp", help='Path where sorted images will be stored. Default is "./tmp".')
parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
parser.add_argument('--dry-run', action='store_true', help='If set, no files will be moved, only logged.')


args = parser.parse_args()
logger.info(f"input_images_path: {args.input_images_path}")
logger.info(f"output_images_path: {args.output_images_path}")
logger.info(f"verbose: {args.verbose}")
logger.info(f"dry_run: {args.dry_run}")

if (args.verbose):
	logger.setLevel(logging.DEBUG)




main(args.input_images_path, args.output_images_path, args.dry_run)