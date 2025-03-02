"""Main application entry point for PDM Lite."""
import time
from flask import Flask, render_template, g
import config
import auth
import items
import views

app = Flask(__name__)
app.secret_key = config.secret_key

# Register auth routes
app.add_url_rule('/', 'index', auth.index, methods=["GET", "POST"])
app.add_url_rule('/register', 'register', auth.register, methods=["GET", "POST"])
app.add_url_rule('/logout', 'logout', auth.logout)

# Register item routes
app.add_url_rule('/pdm', 'pdm', items.pdm, methods=["GET", "POST"])
app.add_url_rule('/add_item', 'add_item', items.add_item, methods=["POST"])
app.add_url_rule('/search_items', 'search_items', items.search_items, methods=["POST"])
app.add_url_rule('/edit_item/<int:item_number>', 'edit_item', items.edit_item)
app.add_url_rule('/update_item/<int:item_number>', 'update_item', items.update_item, methods=["POST"])
app.add_url_rule('/delete_item/<int:item_number>', 'delete_item', items.delete_item, methods=["POST"])
app.add_url_rule('/user_page', 'user_page', views.user_page)
app.add_url_rule('/item_details/<int:item_number>', 'item_details', views.item_details)

# Statistics
app.add_url_rule('/statistics', 'statistics', views.statistics)

# Error handlers
@app.errorhandler(403)
def forbidden(e):
    """Render a 403 error page."""
    return render_template("403.html"), 403

# Printing elapsed time for each request
@app.before_request
def before_request():
    """Set the start time for the request."""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Log the elapsed time for the request."""
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

if __name__ == "__main__":
    app.run(debug=True)
