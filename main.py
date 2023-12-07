from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import os
import pandas as pd
import extcolors
from colormap import rgb2hex

# specify folder where the image is saved
upload_folder = "./static/photos"

app = Flask(__name__)

def color_to_df(input):
    """Takes input of ([((R, G, B), occurrence) then converts RGB input to hex codes and finally to Panda dataframe.
    The df has the following columns "Color", "Color code", "Percent" """
    pixel_count = input[-1]
    colors_pre_list = str(input).replace('([(', '').split(', (')[0:-1]
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_percent = [(int(i.split('), ')[1].replace(')', '')) / pixel_count) * 100 for i in colors_pre_list]

    # convert RGB to HEX code
    df_color_up = [rgb2hex(int(i.split(", ")[0].replace("(", "")),
                           int(i.split(", ")[1]),
                           int(i.split(", ")[2].replace(")", ""))) for i in df_rgb]

    df = pd.DataFrame(zip(df_color_up, df_color_up, df_percent), columns=['Color', 'Color code', 'Percent'])
    df = df.round(2)
    df['Percent'] = df['Percent'].astype(str) + ' %'
    return df

@app.route("/")
def main():
    filename = ""
    return render_template("index.html", image_to_show=filename)

@app.route("/uploader", methods = ["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files["file"]
        tolerance = int(request.form.get("tolerance"))

        # secure filename to make filename safe
        filename = secure_filename(f.filename)
        # combine the upload folder and filename to get the full path
        full_path = os.path.join(upload_folder, filename)
        # save the file to the specified folder
        f.save(full_path)

        colors_x = extcolors.extract_from_path(full_path, tolerance=tolerance, limit=10)
        df_color = color_to_df(colors_x)
        dict_color = df_color.to_dict()

        return render_template("index.html",
                               image_to_show=filename,
                               tables=dict_color,
                               titles=df_color.columns.values,
                               dataframe = df_color)

if __name__ == "__main__":
    app.run(debug=True, port=5010)