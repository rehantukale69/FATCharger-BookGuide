from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# ---------- MongoDB Setup ----------
client = MongoClient(
    "mongodb+srv://rehantukale69_db_user:ulZCEjXXGnJCHrLF@cluster.xe6ervb.mongodb.net/"
)
db = client.bookstore
books_collection = db.books
orders_collection = db.orders  # If you want to store orders

# ---------- Serve Website ----------
@app.route('/', methods=['GET'])
def home():
    # Optionally display all books on the page
    books = list(books_collection.find())
    return render_template('index.html', books=books)

# ---------- Dialogflow Webhook ----------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    intent_name = data['queryResult']['intent']['displayName']
    parameters = data['queryResult']['parameters']

    # -------- Intent 1: About Specific Book --------
    if intent_name == "AboutSpecificBook":
        book_name = parameters.get('BookName')
        print("Book parameter:", book_name)
        if book_name:
            book = books_collection.find_one({"title": {"$regex": f"^{book_name}$", "$options": "i"}})
            if book:
                response = {
                    "fulfillmentMessages": [
                        {
                            "payload": {
                                "richContent": [
                                    [
                                        {
                                            "type": "image",
                                            "rawUrl": book["image_url"],
                                            "accessibilityText": book["title"]
                                        },
                                        {
                                            "type": "info",
                                            "title": book["title"],
                                            "subtitle": f"{book['description']} | Price: ₹{book['price']}"
                                        }
                                    ]
                                ]
                            }
                        }
                    ]
                }
                return jsonify(response)
        return jsonify({"fulfillmentText": "Book not found"})

    # -------- Intent 2: Books by Genre --------
    if intent_name == "GetBooksByGenre":
        genre_name = parameters.get('Genre')
        print("Genre parameter:", genre_name)
        if genre_name:
            books = list(books_collection.find({"genre": {"$regex": f"^{genre_name}$", "$options": "i"}}))
            if books:
                rich_books = []
                for book in books:
                    rich_books.append(
                        [

                            
                            {
                                "type": "image",
                                "rawUrl": book["image_url"],
                                "accessibilityText": book["title"]
                            },
                            {
                                "type": "info",
                                "title": book["title"],
                                "subtitle": f"{book['description']} | Price: ₹{book['price']}"
                            }
                        ]
                    )
                response = {
                    "fulfillmentMessages": [
                        {
                            "payload": {
                                "richContent":[
  [
    {
      "type": "image",
      "rawUrl": book["image_url"],
      "accessibilityText": book["title"]
    },
    {
      "type": "info",
                                "title": book["title"],
                                "subtitle": f"{book['description']} | Price: ₹{book['price']}"
    }
  ]
]
                            }
                        }
                    ]
                }
                return jsonify(response)
        return jsonify({"fulfillmentText": f"No books found in genre {genre_name}"})

    # -------- Intent 3: Get Order Details --------
    if intent_name == "GetOrderDetails":
        # Expecting parameters: UserID, Password, PhoneNumber
        user_id = parameters.get("UserID")
        phone = parameters.get("PhoneNumber")
        password = parameters.get("Password")
        print("Order Details:", user_id, phone)
        
        # You can fetch orders from MongoDB
        order = orders_collection.find_one({"user_id": user_id})
        if order:
            response = {
                "fulfillmentText": f"Hello {user_id}, your last order was: {order['items']}. Total: ₹{order['total']}"
            }
            return jsonify(response)
        else:
            return jsonify({"fulfillmentText": "No orders found for this user."})

    return jsonify({"fulfillmentText": "Intent not recognized."})


# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
