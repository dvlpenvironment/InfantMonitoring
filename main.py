from server import app

if __name__ == '__main__':
    print('CV on')
    app.run(host='0.0.0.0', port=5000, debug=True)