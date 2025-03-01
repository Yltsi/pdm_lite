"""Main application entry point for PDM Lite."""
from flask import Flask
import config
import auth
import items

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
app.add_url_rule('/user_page', 'user_page', items.user_page)
app.add_url_rule('/item_details/<int:item_number>', 'item_details', items.item_details)

if __name__ == "__main__":
    app.run(debug=True)
