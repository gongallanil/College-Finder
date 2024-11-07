from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        return None
    except pd.errors.ParserError:
        return None

def find_top_colleges(state, data):
    filtered_data = data[data['State'].str.strip().str.lower() == state.lower()]
    top_colleges = filtered_data.sort_values(by='Rating', ascending=False).head(10)
    return top_colleges

def generate_plot(data, x_param, y_param, title, xlabel, ylabel, graph_type):
    plt.figure(figsize=(10, 6))

    # Convert x_param to numeric if it's not
    data[x_param] = pd.to_numeric(data[x_param], errors='coerce')

    if graph_type == 'line':
        sns.lineplot(x=x_param, y=y_param, data=data, marker='o')
    else:
        raise ValueError(f"Unsupported graph type: {graph_type}")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    file_path = 'colleges.csv'
    data = load_data(file_path)

    top_colleges = None
    parameter_img = None
    if request.method == 'POST':
        state = request.form.get('state')
        parameter = request.form.get('parameter')
        graph_type = request.form.get('graph_type')

        if data is not None:
            top_colleges = find_top_colleges(state, data)

            if not top_colleges.empty:
                # Generate plot for the selected parameter
                parameter_img = generate_plot(top_colleges, parameter, 'College Name',
                                              f'{parameter} of Top Colleges in {state}', parameter, 'College Name', graph_type)

    return render_template('index.html', top_colleges=top_colleges, parameter_img=parameter_img)

if __name__ == '__main__':
    app.run(debug=True)
