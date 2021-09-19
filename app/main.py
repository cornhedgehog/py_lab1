from app.image_service import upload_file, get_rgb_hist, merge_images, clear_image_folder, MERGED_IMAGE_NAME
from app.enums.pic_order import PicOrder
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['post', 'get'])
def index():
    if request.method == 'GET':
        clear_image_folder()
    if request.method == 'POST':
        paths = []
        hists = []
        for uploaded_file in request.files.getlist('pic1'):
            if uploaded_file.filename:
                path = upload_file(uploaded_file, PicOrder.First)
                paths.append(path)
                hist = get_rgb_hist(path, PicOrder.First)
                hists.append(hist)
        for uploaded_file in request.files.getlist('pic2'):
            if uploaded_file.filename:
                path2 = upload_file(uploaded_file, PicOrder.Second)
                paths.append(path2)
                hist2 = get_rgb_hist(path2, PicOrder.Second)
                hists.append(hist2)
        if len(paths) == 2:
            hist3 = merge_images(paths, request.form.get('pic-alignment'))
            print(paths[0])
            image_results = dict(pic1=paths[0], hist1=hists[0], pic2=paths[1], hist2=hists[1], pic3=MERGED_IMAGE_NAME, hist3=hist3)
            return render_template('image_result.html', image_results=image_results)

    return render_template('index.html')