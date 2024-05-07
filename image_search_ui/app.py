import dash
from dash import html, dcc
import base64
from dash.dependencies import Input, Output, State
import requests
import io

import requests
from requests_toolbelt import MultipartEncoder
import os
base_url = os.getenv("HOST_URL", "http://127.0.0.1:8000/")

def make_request(img, event_id="asdf", limit=2, thres=0.3):
    url = f'{base_url}download/?event_id={event_id}&limit={limit}&threshold={thres}'
    m = MultipartEncoder(
    fields={
            'files': ('p3.jpeg', img, 'image/jpeg')
        }
    )

    headers = {
        'accept': 'application/json',
        'Content-Type': m.content_type
    }

    response = requests.post(url, headers=headers, data=m)
    return response.json()


# Dash App Setup
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        }
    ),
    html.Div(id='output-image-search', style={'display': 'flex', 'flex-wrap': 'wrap'}),  # Container for images
    html.Div(id='output-info') 
])


# Helper function to display an image
def display_image(image_path, caption):
    with open(image_path, "rb") as f: 
        encoded_image = base64.b64encode(f.read()).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{encoded_image}"
    return html.Div([
        html.H5(caption),
        html.Img(src=data_uri, style={'width': '23%', 'margin': '1%'})  # Style for image size
    ])

@app.callback(
    [Output('output-image-search', 'children'), Output('output-info', 'children')],
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'))
def search_similar_images(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        try:
            decoded = base64.b64decode(content_string)

            # Convert to bytes
            image_bytes = io.BytesIO(decoded)

            results = make_request(image_bytes)
            print(results)

            if results["status"]=="DONE":
                # images = [display_image(result['image_data'], result['caption']) for result in results['similar']]
                results = ["/Users/abhaychaturvedi/Documents/Work/id-verification/face_rect/src/test/test.jpeg"]#results["results"]
                images = [display_image(image, "Similar Image") for image in results]

                return images, "Similar Images Found!"
            else:
                return [], "Error processing image. Try again!"

        except Exception as e:
            return [], f"An error occurred: {e}"
    else:
        return [], "No image uploaded yet!"


if __name__ == '__main__':
    app.run_server(debug=True)
