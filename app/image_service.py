
from app.enums.pic_order import PicOrder
from app.enums.merge_type import MergeType
import os, shutil
from flask import Flask, flash, request, redirect
from PIL import Image
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import numpy

UPLOAD_FOLDER_FULL_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static' + '/img_folder/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
HIST_EXTENSION = '_hist.png'
MERGED_IMAGE_NAME = 'merged_image.png'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_FULL_PATH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###
# This function uploads the image from the user into the image folder
def upload_file(file, picNumber):
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        filename = picNumber + '.' + extension
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(full_filename)
        return filename

###
# This function creates RGB histogram
def plot_histogram(image, title, mask=None):
	# split the image into its respective channels, then initialize
	# the tuple of channel names along with our figure for plotting
	chans = cv2.split(image)
	colors = ("b", "g", "r")
	plt.figure()
	plt.title(title)
	plt.xlabel("Bins")
	plt.ylabel("# of Pixels")

	# loop over the image channels
	for (chan, color) in zip(chans, colors):
		# create a histogram for the current channel and plot it
		hist = cv2.calcHist([chan], [0], mask, [256], [0, 256])
		plt.plot(hist, color=color)
		plt.xlim([0, 256])


###
# This function returns image name of the saved matplotlib RGB histogram
def get_rgb_hist(filename, picNumber):
    pil_image = Image.open(UPLOAD_FOLDER_FULL_PATH+filename).convert('RGB') 
    open_cv_image = numpy.array(pil_image) 
    # Convert RGB to BGR 
    im = open_cv_image[:, :, ::-1].copy() 
    plot_histogram(im, "Histogram for Original Image")

    hist_full_filename = os.path.join(app.config['UPLOAD_FOLDER'], picNumber + HIST_EXTENSION)
    plt.savefig(hist_full_filename, bbox_inches='tight', dpi=100)
    return picNumber + HIST_EXTENSION

###
# This function concatenates images vertically or horizontally according to the second arg `merge_type`
def merge_images(imagenames, merge_type):
    full_filepath = os.path.join(app.config['UPLOAD_FOLDER'], MERGED_IMAGE_NAME)
    if merge_type == MergeType.Vertical:
        image = get_image_concatenated_vertically(Image.open(UPLOAD_FOLDER_FULL_PATH + imagenames[0]), Image.open(UPLOAD_FOLDER_FULL_PATH + imagenames[1]))
        image.save(full_filepath)
    else:
        image = get_image_concatenated_horizontally(Image.open(UPLOAD_FOLDER_FULL_PATH + imagenames[0]), Image.open(UPLOAD_FOLDER_FULL_PATH + imagenames[1]))
        image.save(full_filepath)
    return get_rgb_hist(MERGED_IMAGE_NAME, PicOrder.Third)

###
# This function concatenates two given images into one vertically. Images have to be Pillow images, not filenames
def get_image_concatenated_vertically(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

###
# This function concatenates two given images into one horizontally. Images have to be Pillow images, not filenames
def get_image_concatenated_horizontally(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

###
# This function clean ups the image folder between requests
def clear_image_folder():
    file_path = app.config['UPLOAD_FOLDER']
    if os.path.isdir(file_path):
      shutil.rmtree(file_path)
    os.mkdir(file_path)