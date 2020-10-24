from flask import Flask, session, render_template, request, redirect, url_for, abort, jsonify, send_from_directory
from string import ascii_lowercase
from random import choice
from datetime import datetime
import db
import os
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

try:
    import data.config as config
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['SITE_URL'] = config.SITE_URL
    app.secret_key = config.SECRET_KEY
except ModuleNotFoundError:
    app.config['UPLOAD_FOLDER'] = './data/img'
    app.config['SITE_URL'] = "example.com"
    app.secret_key = b'tetfhgdfghdfghfdghst'
    # TODO hier eigenständig einen secret_key erstellen? niemand trauert abgelaufenen sessions nach bei der app


class LinkConverter(BaseConverter):
    regex = r"[\w]{10}"


app.url_map.converters['link'] = LinkConverter


def generate_string(length=10):
    retval = ""
    for i in range(0, length):
        retval += choice(ascii_lowercase)
    return retval


def check_login(session):
    if "login" in session and session["login"]:
        return True
    return False


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

    pics = db_session.query(db.Pictures).filter_by(shoot=obj).all()

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
                pic.comment = request.form['comment']  # Bei Unsafe muss ein Kommentar dabei sein!
        except KeyError:
            abort(400)
            raise

        if rating not in ["yes", "unsafe", "no"]:
            abort(400)

        if obj.max_images > 0:
            if rating == "yes" and obj.keep_count() == obj.max_images:
                return jsonify(error="Too many images to keep!"), 400

        pic.status = rating
        db_session.commit()

        not_rated = db_session.query(db.Pictures).filter(
            db.Pictures.shoot_id == obj.id, db.Pictures.status == None
        ).count()
        if not_rated == 0:
            obj.done = True
        elif not_rated > 0:  # sanity
            obj.done = False
        db_session.commit()

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
        except KeyError:
            abort(400)
            raise

        link = generate_string()
        db_session = db.get_session()
        obj = db.Shoot(
            link=link, description=description, max_images=limit, done=False,
            creation=datetime.now()
        )
        db_session.add(obj)
        db_session.commit()

        try:
            if request.form['img_list'] != "":
                images = request.form['img_list'].split(";")
                for image in images:
                    pic_obj = db.Pictures(shoot=obj, filename=image)
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
        return render_template("admin_shoot_overview.html", shoot=obj, pics=obj.pictures)
    elif request.method == "POST":
        try:
            # Route 1: Updating Data
            description = request.form['description']
            limit = request.form['limit']
            obj.description = description
            obj.max_images = limit
            db_session.commit()
            return redirect(url_for(".admin_shoot_overview", shoot_link=shoot_link))
        except KeyError:
            # Route 2: Uploading images
            try:
                images = request.form['img_list'].split(";")
                for image in images:
                    pic_obj = db.Pictures(shoot=obj, filename=image)
                    db_session.add(pic_obj)
                db_session.commit()

                return jsonify(data="success")
            except KeyError:
                abort(400)


@app.route('/admin/<link:shoot_link>/<string:picturename>/')
def admin_shoot_picture(shoot_link, picturename):
    if not check_login(session):
        abort(403)
    
    db_session = db.get_session()
    try:
        obj = db_session.query(db.Shoot).filter_by(link=shoot_link).one()
        pic = db_session.query(db.Pictures).filter_by(shoot=obj, filename=picturename).one()
        return render_template("admin_shoot_picture.html", shoot=obj, pic=pic)
    except NoResultFound:
        abort(404)


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

    file = request.files["files[]"]
    filename = file.filename.replace(" ", "_")
    if filename == '':  # when no file is selected filename is empty, without data
        return jsonify(error="No file selected")
    if file:
        sec_filename = secure_filename(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], sec_filename))
        return jsonify(files=[{
            "name": filename,
            "url": "/img/" + filename,
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
