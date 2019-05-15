import os
from backend import app, db
from flask import Flask, request, jsonify, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.models import Users, Login, SavedTrails


@app.route('/', methods=['GET'])
def hello_world():
    return 'i like cheese'


@app.route('/save-trail', methods=['POST'])
def save_trail():
    data = request.get_json()
    check_duplicate = db.session.query(SavedTrails).filter(
        SavedTrails.user_id == data.get('userId'), SavedTrails.trail_id == data.get('trailId')).first()
    if(check_duplicate):
        return jsonify({'status': 'error', 'message': "User has already saved trail"}), 400
    new_trail = SavedTrails(user_id=data.get('userId'), trail_id=data.get(
        'trailId'), trail_data=data.get('trailData'))
    db.session.add(new_trail)
    db.session.commit()
    return jsonify({'trail': new_trail.trail_id})


@app.route('/delete-trail', methods=['POST'])
def delete_trail_by_id():
    data = request.get_json()
    if(not data.get('userId') or not data.get('trailId')):
        return jsonify({'status': 'error', 'message': "Missing arguments"}), 400
    to_delete = db.session.query(SavedTrails).filter(
        SavedTrails.user_id == data.get('userId'), SavedTrails.trail_id == data.get('trailId')).delete()
    db.session.commit()
    return jsonify({'status': to_delete})


@app.route('/load-trails', methods=['POST'])
def load_trails():
    data = request.get_json()
    if(data):
        if(data.get('userId')):
            user_trails = db.session.query(SavedTrails).filter(
                SavedTrails.user_id == data.get('userId'))
            output = []
            if(user_trails != []):
                for trail_item in user_trails:
                    data = {}
                    data['trail'] = trail_item.trail_data
                    output.append(data)
                return jsonify({'trails': output})
            else:
                return jsonify({'status': 'error', 'message': "No trails match user"}), 400

    else:
        return jsonify({'status': 'error', 'message': "Missing data"}), 400


@app.route('/delete-user', methods=['POST'])
def delete_user_by_id():
    data = request.get_json()
    print("Called delete user", data.get('userId'))
    to_delete = db.session.query(Users).filter(
        Users.id == data.get('userId')).delete()
    db.session.commit()
    return jsonify({'status': to_delete})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("DATA", data)
    if(data == None):
        return jsonify({'status': 'error', 'message': "Make sure all form fields have been filled out"}), 400
    duplicate = db.session.query(Users).filter(
        Users.username == data.get('username')).first()
    if(data.get('confirmPassword') != data.get('password')):
        return jsonify({'status': 'error', 'message': "Passwords dont match"}), 400

    if(duplicate):
        return jsonify({'status': 'error', 'message': "Username already exists"}), 400

    if(data.get('email') and data.get('username') and data.get('password')):
        user = Users(email=data.get('email'),
                     username=data.get('username'))
        db.session.add(user)
        db.session.commit()
        login = Login(password=data.get('password'),
                      parent_id=user.id,
                      parent_username=user.username)
        db.session.add(login)
        db.session.commit()
        return jsonify({'id': user.id, 'username': user.username}), 201

    else:
        return jsonify({'status': 'error', 'message': "Missing form fields"}), 400


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    print("DATA", data)
    if(data.get('username') and data.get('password')):
        login_session = db.session.query(Login).filter(
            Login.parent_username == data.get('username')).first()
        if(login_session == None):
            return jsonify({'status': 'error', 'message': "No matching user in database", 'id': None, 'username': None}), 400

        if(login_session.check_password(data.get('password'))):
            return jsonify({'id': login_session.parent_id, 'username': login_session.parent_username}), 201
        else:
            return jsonify({'status': 'error', 'message': "Password is incorrect", 'id': None, 'username': None}), 400

    else:
        return jsonify({'status': 'error', 'message': "Missing form fields"}), 400


if __name__ == '__main__':
    app.run(debug=True)
