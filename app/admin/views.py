from flask_admin.contrib import sqla
from flask_security import current_user
from flask import has_request_context
from sqlalchemy import or_
from flask import redirect, url_for, request


# Model views for Flask-Admin
class AdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role("admin")
        )

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("login", next=request.url))


class TransactionView(sqla.ModelView):
    can_view_details = True
    page_size = 50

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("security.login", next=request.url))

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)

    def get_query(self):
        self.values = [current_user.username, current_user.email]
        # Customize the query to filter entries
        query = super().get_query()
        return query.filter(
            or_(
                getattr(self.model, "sender_id").in_(self.values),
                getattr(self.model, "recipient_id").in_(self.values),
            )
        )

    def get_count_query(self):
        # Customize the count query to filter entries
        self.values = [current_user.username, current_user.email]
        query = super().get_count_query()
        return query.filter(
            or_(
                getattr(self.model, "sender_id").in_(self.values),
                getattr(self.model, "recipient_id").in_(self.values),
            )
        )
