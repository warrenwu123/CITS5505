# profile.py (new file)
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from .forms import ProfilePictureForm
from .utils import save_profile_picture

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfilePictureForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.profile_image = picture_file
            db.session.commit()
            flash('Profile picture has been updated', 'success')
            return redirect(url_for('profile.profile'))
    return render_template('profile.html', title='Profile', form=form)