import base64
import os, shutil
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory, current_app
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import glob
import convert
import time
import dash_bootstrap_components as dbc
import dash_core_components as dcc


#https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html
#https://www.safran-group.com/urd2021/reports/index.html

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__, static_url_path='')
app = dash.Dash(server=server)

current_path = os.getcwd()

vert = '#009081'
XBRL_DIRECTORY = os.path.join(current_path, 'Entrees_XBRL')
CSV_DIRECTORY = os.path.join(current_path, 'Sorties_CSV')

UPLOAD_DIRECTORY = " "

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

#Vider CSV_DIRECTORY et XBRL_DIRECTORY
def clean_folder(folder) : 
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

clean_folder(XBRL_DIRECTORY)
clean_folder(CSV_DIRECTORY)

@server.route('/download/<path:filename>')
def download(filename):
    """Serve a file from the upload directory."""
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads, filename, as_attachment=True)


app.layout = dbc.Container(
    [
        html.Div(style={'backgroundColor': '#009081',
                        'height' : '20px' },),
        dbc.Row(
            [
                dbc.Col(html.Img(src=app.get_asset_url('logo.png'),
                                 style={'height':'17%', 'width':'17%'}),
                    width=2),
                dbc.Col(html.H2("Convertisseur de fichiers XBRL en tableaux EXCEL"),
                    width=4)]
            ),
        html.H4("Zone de dépôt XBRL :"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Glisser puis déposer ou cliquer pour choisir un fichier à charger."]
            ),
            style={
                "width": "50%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
                
            },
            multiple=True,
            
        ),
        html.H4("Fichiers à télécharger :"),
        dcc.Loading(children=[html.Ul(id="file-list")]),
        html.Div(id="time-indic"),
        
    ], 
    fluid=True
)




def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(XBRL_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files(URL):
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(URL):
        path = os.path.join(URL, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    #location = "/{}".format(urlquote(filename))
    location = CSV_DIRECTORY + "/" + filename
    print("location : " + filename)
    print('')
    print(location)
    #download("/{}")
   
    return html.A(filename, href=location)




@app.callback(
    [Output("file-list", "children"), Output("time-indic", "children")],
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    
    start = time.process_time()   

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)
            print('Fichier sauvegardé')
            
    
    xbrl_files = uploaded_files(XBRL_DIRECTORY)
    for i in xbrl_files :
        convert.convertir_V2(CSV_DIRECTORY, i, XBRL_DIRECTORY)
        print(str(i))
        print('Fichier converti')
    
    csv_files = uploaded_files(CSV_DIRECTORY) 
    
    
    if len(csv_files) == 0:
        csv_list = [html.Li("Aucun rapport n'a encore été chargé")]
    else :
        print("checker : ")
        print('')
        print(type(csv_files[0]))
        csv_list = [html.Li(file_download_link(filename)) for filename in csv_files]
    
    execution_time_sentence = "Le traitement a duré : " + str(time.process_time() - start) + " secondes."
    
    return csv_list, execution_time_sentence



if __name__ == "__main__":
    app.run_server(debug=True, port=8080)