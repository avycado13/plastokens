import pytest
from flask import url_for
from app.models import User, Transaction
from app.extensions import db


def test_transfer(client):
    # Log in as test@me.com
    response = client.post(
        url_for("security.login"),
        data={"email": "test@me.com", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Check initial balances
    sender = User.query.filter_by(email="test@me.com").first()
    recipient = User.query.filter_by(email="test@you.com").first()
    assert sender.balance == 1000
    assert recipient.balance == 1000

    # Perform transfer
    response = client.post(
        url_for("main.index"),
        data={"recipient": "test@you.com", "amount": 100},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Transfer successful!" in response.data

    # Check updated balances
    sender = User.query.filter_by(email="test@me.com").first()
    recipient = User.query.filter_by(email="test@you.com").first()
    assert sender.balance == 900
    assert recipient.balance == 1100

    # Check transaction record
    transaction = Transaction.query.filter_by(
        sender_id=sender.id, recipient_id=recipient.id
    ).first()
    assert transaction is not None
    assert transaction.amount == 100
