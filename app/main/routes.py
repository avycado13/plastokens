from app.main import bp
from flask import render_template, redirect, flash, url_for
from flask_security import login_required, current_user
from app.main.forms import TransferForm


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = TransferForm()
    if form.validate_on_submit():
        form.execute_transfer()
        flash("Transfer successful!", "success")
        return redirect(url_for("main.index"))
    return render_template(
        "index.html",
        username=current_user.username,
        balance=current_user.balance,
        form=form,
    )
