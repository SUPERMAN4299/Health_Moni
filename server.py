from flask import Flask
#import thread

app = Flask(__name__)

stored_user_enc = "61646d696e"
stored_pass_enc = "61646d696e"

add_user_enc = "61646d696e31"
add_user_enc = "61646d696e31"

@app.route('/s')
def get_string():
	return f" {stored_user_enc}{stored_pass_enc}"
    
@app.route("/query")
def query():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health_Moni Project Login Guide</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f4f8;
            color: #333;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #4CAF50;
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        main {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            margin-bottom: 15px;
        }
        h1 {
            color: #2c3e50;
        }
        h2 {
            color: #34495e;
        }
        h3 {
            color: #7f8c8d;
        }
        ol {
            padding-left: 20px;
        }
        a {
            color: #1abc9c;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
        .note {
            background-color: #eafaf1;
            padding: 10px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>

<header>
    <h1>Welcome to the Health_Moni Project</h1>
</header>

<main>
    <section>
        <h2>How to Login</h2>
        <div class="note">
            You will receive a card in your product box containing your Username and Password. Enter them exactly as shown in the app to access our service.
        </div>
        <h3>If you're unsure how to proceed, follow these steps carefully:</h3>
        <ol>
            <li>Open the box where you received this product.</li>
            <li>On your desktop, download the software from our website: <a href="http://127.0.0.1:5000/download" target="_blank">Download Here</a></li>
            <li>Install the software on your PC as usual. Make sure Python is installed: <a href="https://www.python.org" target="_blank">Download Python</a></li>
            <li>Before opening the app, turn on Bluetooth on your device.</li>
            <li>Open the software and enter the Username and Password provided in your card.</li>
            <li>Connect the device associated with our service.</li>
            <li>Allow the software to access the device.</li>
            <li>Once connected, you will be redirected to the monitoring dashboard with real-time graphs.</li>
        </ol>
    </section>
</main>

</body>
</html>
    """

if __name__ == '__main__':
    app.run(debug=True)
