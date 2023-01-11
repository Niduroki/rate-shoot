from flask import Flask, session, render_template, request, redirect, url_for, abort, jsonify, send_from_directory
from flask_babel import Babel
from random import choice
from datetime import datetime
import db
import os
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha256
from PIL import Image, ImageFont, ImageDraw
import pillow_avif

app = Flask(__name__)

try:
    import data.config as config
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.secret_key = config.SECRET_KEY
    try:
        app.config["DATABASE"] = config.DATABASE
    except AttributeError:
        pass
    try:
        app.config["WATERMARK_TEXT"] = config.WATERMARK_TEXT
    except AttributeError:
        pass
    app.config['LANGUAGES'] = {
        'en': 'English',
        'de': 'Deutsch',
        'nl': 'Nederlands',
    }
except ModuleNotFoundError:
    data_path = os.path.join(os.path.abspath(os.path.curdir), "data/")
    if not os.path.exists(os.path.join(data_path, "img/")):
        os.mkdir(os.path.join(data_path, "img/"))
    with open(data_path + "config.py", "w") as f:
        f.write("UPLOAD_FOLDER = '" + os.path.join(data_path, "img/") + "'\n")
        f.write("SECRET_KEY = " + str(os.urandom(20)) + "\n")
    db.get_session()

babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


class LinkConverter(BaseConverter):
    regex = r"[\w]{10}"


app.url_map.converters['link'] = LinkConverter


def generate_link(length=10):
    retval = ""
    for i in range(0, length):
        if i % 2 == 0:
            retval += choice("bcdfghjkmnpqrstvwxyz")
        else:
            retval += choice("aeiou")
    return retval


def check_login(session):
    if "login" in session and session["login"]:
        return True
    return False


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route('/', methods=["get", "post"])
def index():
    if request.method == "GET":
        if check_login(session):
            return redirect(url_for('.admin'))
        else:
            pw = "0"
            if request.args.get('pw') in ["1", "2"]:
                pw = request.args.get('pw')
            return render_template("index.html", pw=pw)
    if request.method == "POST":
        # Check password for admin login
        try:
            password = request.form['password']
        except KeyError:
            abort(400)
            raise

        db_session = db.get_session()
        try:
            instance = db_session.query(db.Passwords).one()
        except NoResultFound:  # Database is empty, accept default password, but give a warning
            if password == "DEF4ULT":
                session["login"] = True
                return redirect(url_for('.admin') + '?pw=1')
            else:
                return redirect('/?pw=1')
        
        if pbkdf2_sha256.verify(password, instance.password):
            session["login"] = True
            return redirect(url_for('.admin'))
        else:
            return redirect('/?pw=1')


@app.route('/help/')
def help_page():
    return render_template("help.html")


@app.route('/<link:shoot_link>/')
def shoot_overview(shoot_link):
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
    except NoResultFound:
        abort(404)
        raise

    pics = db_session.query(db.Pictures).filter_by(shoot=obj).order_by(db.Pictures.filename).all()

    return render_template("shoot_overview.html", shoot=obj, pics=pics)


@app.route('/<link:shoot_link>/<string:picturename>/', methods=["get", "post"])
def shoot_picture(shoot_link, picturename):
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
        pic = db_session.query(db.Pictures).filter_by(shoot=obj, filename=picturename).one()
    except NoResultFound:
        abort(404)
        raise

    if request.method == "GET":
        return render_template("shoot_picture.html", shoot=obj, pic=pic)
    elif request.method == "POST":
        try:
            rating = request.form['rating']
            if rating == "unsafe":
                pic.comment = request.form['comment']  # Unsafe must have a comment!
        except KeyError:
            return jsonify(error="Missing rating/comment data"), 400

        if rating not in ["yes_edited", "yes_unedited", "yes", "unsafe", "no", "none"]:
            return jsonify(error="invalid rating"), 400
        if not obj.unedited_images and rating in ["yes_edited", "yes_unedited"]:
            return jsonify(error="Not accepting edited/unedited data"), 400

        if obj.max_images > 0 and (  # If there is a limit for max (edited) images
            # and we want to keep this image, but we're full already
            (rating == "yes" and obj.keep_count() == obj.max_images)
            or
            # alternatively with edited/unedited options
            (rating == "yes_edited" and obj.keep_count()['edited'] == obj.max_images)
        ):
            return jsonify(error="too_many"), 400

        if obj.unedited_images and obj.max_unedited > 0 and (  # If there is a limit for max unedited images
            # and we want to keep this image, but we're full already
            rating == "yes_unedited" and obj.keep_count()['unedited'] == obj.max_unedited
        ):
            return jsonify(error="too_many"), 400

        if rating == "none":
            pic.status = None
        else:
            pic.status = rating
        db_session.commit()

        # TODO Removed
        """
        not_rated = db_session.query(db.Pictures).filter(
            db.Pictures.shoot_id == obj.id, db.Pictures.status == None
        ).count()
        if not_rated == 0:
            obj.done = True
        elif not_rated > 0:  # sanity
            obj.done = False
        db_session.commit()
        """

        try:
            next_pic = pic.next_pic()
            return jsonify(next=url_for('.shoot_picture', shoot_link=shoot_link, picturename=next_pic.filename))
        except StopIteration:
            return jsonify(next=url_for('.shoot_overview', shoot_link=shoot_link))


@app.route('/admin/')
def admin():
    if not check_login(session):
        abort(403)
    
    if request.args.get('pw') == "1":
        pw = True
    else:
        pw = False
    
    db_session = db.get_session()
    shoots = db_session.query(db.Shoot).order_by(db.Shoot.creation).all()
    return render_template("admin.html", shoots=shoots, pw=pw)


@app.route('/admin/password/', methods=["get", "post"])
def admin_password():
    if not check_login(session):
        abort(403)
    
    if request.method == "GET":
        if request.args.get('wrong') == "1":
            wrongpw = True
        else:
            wrongpw = False
        return render_template("pwchange.html", wrongpw=wrongpw)
    elif request.method == "POST":
        try:
            password = request.form['password']
            password2 = request.form['password2']
        except KeyError:
            abort(400)
            raise

        if password != password2:
            return redirect(url_for(".admin_password") + "?wrong=1")
        
        pwhash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

        db_session = db.get_session()
        db_session.query(db.Passwords).delete()
        db_session.commit()

        obj = db.Passwords(password=pwhash)
        db_session.add(obj)
        db_session.commit()
        
        session["login"] = False
        return redirect('/?pw=2')


@app.route('/logout/')
def admin_pwchange():
    if not check_login(session):
        abort(403)
    session.pop("login", None)
    return redirect('/')


@app.route('/admin/create/', methods=["get", "post"])
def admin_createshoot():
    if not check_login(session):
        abort(403)
    
    if request.method == "GET":        
        return render_template("create_shoot.html")
    elif request.method == "POST":
        try:
            description = request.form['description']
            limit = request.form['limit']
            try:
                # Unedited is checked
                if request.form['unedited'] == "on":
                    unedited = True
                try:
                    # Read Unedited limit
                    limit_unedited = request.form['limit_unedited']
                except KeyError:
                    # If it's not there: Error out
                    abort(400)
                    raise
            except KeyError:
                # Unedited is not checked -> Limit unedited is None
                unedited = False
                limit_unedited = None
        except KeyError:
            abort(400)
            raise

        link = generate_link()
        db_session = db.get_session()
        obj = db.Shoot(
            link=link, description=description, max_images=limit, done=False,
            unedited_images=unedited, max_unedited=limit_unedited,
            creation=datetime.now()
        )
        db_session.add(obj)
        db_session.commit()

        try:
            if request.form['img_list'] != "":
                images = request.form['img_list'].split(";")
                for image in images:
                    image_name, image_rating = image.split("&rating=")
                    pic_obj = db.Pictures(shoot=obj, filename=image_name)
                    if image_rating == "1":
                        pic_obj.star_rating = 1
                    if image_rating == "2":
                        pic_obj.star_rating = 2
                    db_session.add(pic_obj)
                db_session.commit()
        except KeyError:
            pass

        return redirect(url_for('.admin_shoot_overview', shoot_link=link))


@app.route('/admin/<link:shoot_link>/', methods=["get", "post"])
def admin_shoot_overview(shoot_link):
    if not check_login(session):
        abort(403)
    
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
    except NoResultFound:
        abort(404)
        raise

    if request.method == "GET":
        pics = db_session.query(db.Pictures).filter_by(shoot=obj).order_by(db.Pictures.filename).all()
        return render_template("admin_shoot_overview.html", shoot=obj, pics=pics)
    elif request.method == "POST":
        try:
            # Route 1: Updating Data
            description = request.form['description']
            limit = request.form['limit']

            try:
                # Unedited is checked
                if request.form['unedited'] == "on":
                    unedited = True
                try:
                    # Read Unedited limit
                    limit_unedited = request.form['limit_unedited']
                except KeyError:
                    # If it's not there: Error out
                    abort(400)
                    raise
            except KeyError:
                # Unedited is not checked -> Limit unedited is None
                unedited = False
                limit_unedited = None

            if obj.unedited_images and not unedited:
                # If we allowed unedited images before, but now don't we are going to ...
                # Change all yes_edited into yes ...
                # and change all yes_unedited to unsafe with a "Unedited" comment
                for picture in obj.pictures:
                    if picture.status == "yes_edited":
                        picture.status = "yes"
                    elif picture.status == "yes_unedited":
                        picture.status = "unsafe"
                        picture.comment = "Unedited"
            elif not obj.unedited_images and unedited:
                # If it is the other way around (before: Only edited, now: unedited) ...
                # We are going to make all yes into yes_edited
                for picture in obj.pictures:
                    if picture.status == "yes":
                        picture.status = "yes_edited"

            obj.description = description
            obj.max_images = limit
            obj.unedited_images = unedited
            obj.max_unedited = limit_unedited
            db_session.commit()
            return redirect(url_for(".admin_shoot_overview", shoot_link=shoot_link))
        except KeyError:
            # Route 2: Uploading images
            try:
                image_name = request.form['img_name']
                image_rating = request.form['img_rating']
                pic_obj = db.Pictures(shoot=obj, filename=image_name)
                if image_rating == "1":
                    pic_obj.star_rating = 1
                elif image_rating == "2":
                    pic_obj.star_rating = 2
                db_session.add(pic_obj)
                db_session.commit()

                return jsonify(data="success")
            except KeyError:
                abort(400)


@app.route('/admin/<link:shoot_link>/<string:picturename>/', methods=["get", "post"])
def admin_shoot_picture(shoot_link, picturename):
    if not check_login(session):
        abort(403)
    
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
        pic = db_session.query(db.Pictures).filter_by(shoot=obj, filename=picturename).one()
    except NoResultFound:
        abort(404)
        raise

    if request.method == "GET":
        return render_template("admin_shoot_picture.html", shoot=obj, pic=pic)
    else:
        try:
            raw_rating = request.form['rating']
            if raw_rating not in ["/", "0", "1", "2", "none"]:
                return jsonify(error="Invalid rating"), 400
            if raw_rating == "none":
                # Branch to remove image rating
                pic.status = None
                db_session.commit()
                return jsonify(data="success")
            elif raw_rating == "/":
                # From here on branch to set star rating
                rating = None
            else:
                rating = int(raw_rating)
            pic.star_rating = rating
            db_session.commit()
            return jsonify(data="success")
        except KeyError:
            abort(400)


@app.route('/admin/<link:shoot_link>/<string:picturename>/delete/', methods=["delete", ])
def admin_delete_picture(shoot_link, picturename):
    if not check_login(session):
        abort(403)
    
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
        pic = db_session.query(db.Pictures).filter_by(shoot=obj, filename=picturename).one()
    except NoResultFound:
        abort(404)
        raise

    try:
        next_pic = pic.next_pic()
        next_link = url_for('.admin_shoot_picture', shoot_link=shoot_link, picturename=next_pic.filename)
    except StopIteration:
        next_link = url_for('.admin_shoot_overview', shoot_link=shoot_link)

    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], pic.filename)
    try:
        os.unlink(picture_path)
    except FileNotFoundError:
        pass
    db_session.delete(pic)
    db_session.commit()

    return jsonify(next=next_link)


@app.route('/admin/<link:shoot_link>/delete/', methods=["post", ])
def admin_shoot_delete(shoot_link):
    if not check_login(session):
        abort(403)

    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
    except NoResultFound:
        abort(404)
        raise

    for pic in obj.pictures:
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], pic.filename)
        try:
            os.unlink(picture_path)
        except FileNotFoundError:
            pass
        db_session.delete(pic)
    db_session.delete(obj)
    db_session.commit()
    return redirect(url_for(".admin"))
    

@app.route('/admin/upload/', methods=["post", ])
def admin_upload():
    if not check_login(session):
        abort(403)

    try:
        watermark = request.form['watermark'] == "true"
    except KeyError:
        return jsonify(error="No watermark instructions"), 400
    file = request.files["files[]"]
    filename = file.filename.replace(" ", "_")
    if filename == '':  # when no file is selected filename is empty, without data
        return jsonify(error="No file selected")
    if file:
        sec_filename = secure_filename(filename)
        # Check if the file already exists and rename it silently
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], sec_filename)):
            sec_filename = os.path.splitext(sec_filename)[0] + "_conflict" + os.path.splitext(sec_filename)[1]

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], sec_filename))

        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], sec_filename)
        rating = "/"  # Default for missing exif rating -> No rating
        try:
            exif_rating = Image.open(picture_path).getexif()[18246]
            if exif_rating == 3 or exif_rating == 4:
                rating = "1"
            if exif_rating == 5:
                rating = "2"
        except KeyError:
            pass

        if watermark:
            # Apply a watermark
            watermark_text = app.config.get('WATERMARK_TEXT', "SAMPLE")
            img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], sec_filename)).convert("RGBA")
            fnt = ImageFont.truetype("FreeSans", size=img.width//4)
            txt_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_img)
            offset = draw.textsize("SAMPLE", font=fnt)
            draw.text(
                (img.width//2 - (offset[0]//2), img.height//2 - (offset[1]//2)),
                watermark_text, font=fnt, fill=(255, 255, 255, 30)
            )
            rot = txt_img.rotate(30, expand=False, fillcolor=(255, 255, 255, 0))
            out = Image.alpha_composite(img, rot)
            out.convert("RGB").save(os.path.join(app.config['UPLOAD_FOLDER'], sec_filename))
            # If there is no watermark to apply we have nothing to do in an else, or so

        return jsonify(files=[{
            "name": sec_filename,
            "rating": rating,
            "url": "/img/" + sec_filename,
        }, ])


@app.route('/admin/prune/', methods=["post", ])
def admin_prune():
    if not check_login(session):
        abort(403)

    db_session = db.get_session()
    pics = db_session.query(db.Pictures).all()
    count = 0
    for pic in pics:
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], pic.filename)
        if not os.path.isfile(picture_path):
            count += 1
            db_session.delete(pic)
    db_session.commit()

    count2 = 0
    for pic in os.listdir(app.config['UPLOAD_FOLDER']):
        if db_session.query(db.Pictures).filter_by(filename=pic).all() == []:
            os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], pic))
            count2 += 1
    return jsonify(count=count, count2=count2)
    

@app.route('/img/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
