from flask import Flask, render_template, request, redirect, session, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'Your seceret key'
db = SQLAlchemy(app)

class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, nullable=False)  # store image as binary
    mimetype = db.Column(db.String(50), nullable=False)  # like 'image/png'
    name = db.Column(db.String(100), nullable=False)  # this is missing in your error
 


@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['image']
        if not file:
            return 'No file uploaded.', 400

        new_img = UserImage(
            name=secure_filename(file.filename),
            image=file.read(),
            mimetype=file.mimetype
        )
        db.session.add(new_img)
        db.session.commit()
        return 'Image uploaded successfully!'
    
    return render_template('upload.html')

@app.route('/image/<int:id>')
def get_image(id):
    img = UserImage.query.get(id)
    if not img:
        return 'Image Not Found!', 404
    return send_file(
        io.BytesIO(img.image),
        mimetype=img.mimetype,
        download_name=img.name
    )









with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
