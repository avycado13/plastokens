from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_security import current_user
from app.models import User, Transaction
from app.extensions import db


class TransferForm(FlaskForm):
    recipient = StringField("Username or Email", validators=[DataRequired()])
    amount = IntegerField("Amount", validators=[DataRequired()])
    submit = SubmitField("Transfer")

    def validate(self, **kwargs):
        if not super(TransferForm, self).validate(**kwargs):
            return False

        amount = self.amount.data

        recipient = User.query.filter(
            (User.username == self.recipient.data) | (User.email == self.recipient.data)
        ).first()
        if not recipient:
            self.recipient.errors.append("Recipient does not exist.")
            return False

        if amount <= 0:
            self.amount.errors.append("Amount must be greater than zero.")
            return False

        if current_user.balance < amount:
            self.amount.errors.append("Insufficient balance.")
            return False

        return True

    def execute_transfer(self):
        amount = self.amount.data
        recipient = User.query.filter(
            (User.username == self.recipient.data) | (User.email == self.recipient.data)
        ).first()

        if recipient and current_user.balance >= amount:
            current_user.balance -= amount
            recipient.balance += amount

            # Create a new transaction record
            transaction = Transaction(
                sender_id=current_user.id, recipient_id=recipient.id, amount=amount
            )
            db.session.add(transaction)
            db.session.commit()
