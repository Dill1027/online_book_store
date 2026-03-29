# book-service/data_service.py

from pymongo import MongoClient
from models import Book
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from bson.objectid import ObjectId

class BookDataService:
    """MongoDB-based book data service with fallback to in-memory storage"""
    
    def __init__(self):
        """Initialize MongoDB connection with fallback to in-memory storage"""
        self.client = None
        self.db = None
        self.collection = None
        self.is_mock = False
        self.mock_books = {}
        
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✅ Connected to MongoDB")
            
            # Create index for title for faster searches
            try:
                self.collection.create_index("title")
                self.collection.create_index("author")
                self.collection.create_index("category")
            except Exception as e:
                print(f"⚠️  Could not create indexes: {e}")
            
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("📦 Using in-memory storage for testing...")
            self.is_mock = True
            # Initialize with sample data
            self._initialize_mock_data()

    def _initialize_mock_data(self):
        """Initialize mock data for testing when MongoDB is unavailable"""
        self.mock_books = {
            1: Book(id=1, title="Python Programming", author="Guido van Rossum", category="Programming", price=49.99, stock=10),
            2: Book(id=2, title="Web Development with FastAPI", author="Sebastian Ramirez", category="Web", price=59.99, stock=5),
            3: Book(id=3, title="Advanced Python", author="David Beazley", category="Programming", price=69.99, stock=8),
            4: Book(id=4, title="REST API Design", author="Apigee", category="Web", price=39.99, stock=12),
            5: Book(id=5, title="Microservices Architecture", author="Sam Newman", category="Architecture", price=79.99, stock=3),
        }

    def get_all_books(self, title: str = None, author: str = None, category: str = None):
        """Get all books with optional search filters"""
        if self.is_mock:
            books = list(self.mock_books.values())
            
            # Filter by title
            if title:
                books = [b for b in books if title.lower() in b.title.lower()]
            # Filter by author
            if author:
                books = [b for b in books if author.lower() in b.author.lower()]
            # Filter by category
            if category:
                books = [b for b in books if category.lower() in b.category.lower()]
            
            return books
        
        else:
            query = {}
            if title:
                query["title"] = {"$regex": title, "$options": "i"}
            if author:
                query["author"] = {"$regex": author, "$options": "i"}
            if category:
                query["category"] = {"$regex": category, "$options": "i"}
            
            books = []
            for doc in self.collection.find(query):
                books.append(self._doc_to_book(doc))
            return books

    def get_book_by_id(self, book_id: int):
        """Get a single book by ID"""
        if self.is_mock:
            return self.mock_books.get(book_id)
        else:
            doc = self.collection.find_one({"id": book_id})
            if doc:
                return self._doc_to_book(doc)
            return None

    def add_book(self, book_data):
        """Add a new book to the database"""
        if self.is_mock:
            # Get the next ID
            max_id = max(self.mock_books.keys()) if self.mock_books else 0
            next_id = max_id + 1
            
            book = Book(
                id=next_id,
                title=book_data.title,
                author=book_data.author,
                category=book_data.category,
                price=book_data.price,
                stock=book_data.stock
            )
            self.mock_books[next_id] = book
            return book
        else:
            # Get the next ID
            last_book = self.collection.find_one(sort=[("id", -1)])
            next_id = (last_book["id"] + 1) if last_book else 1
            
            book_dict = book_data.dict()
            book_dict["id"] = next_id
            
            result = self.collection.insert_one(book_dict)
            return self.get_book_by_id(next_id)

    def update_book(self, book_id: int, book_data):
        """Update an existing book"""
        if self.is_mock:
            if book_id not in self.mock_books:
                return None
            
            existing = self.mock_books[book_id]
            update_dict = book_data.dict(exclude_unset=True)
            
            updated = Book(
                id=book_id,
                title=update_dict.get("title", existing.title),
                author=update_dict.get("author", existing.author),
                category=update_dict.get("category", existing.category),
                price=update_dict.get("price", existing.price),
                stock=update_dict.get("stock", existing.stock)
            )
            self.mock_books[book_id] = updated
            return updated
        else:
            update_data = book_data.dict(exclude_unset=True)
            result = self.collection.update_one(
                {"id": book_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return self.get_book_by_id(book_id)
            return None

    def delete_book(self, book_id: int):
        """Delete a book by ID"""
        if self.is_mock:
            if book_id in self.mock_books:
                del self.mock_books[book_id]
                return True
            return False
        else:
            result = self.collection.delete_one({"id": book_id})
            return result.deleted_count > 0

    @staticmethod
    def _doc_to_book(doc):
        """Convert MongoDB document to Book model"""
        # Remove MongoDB's _id field if present
        if "_id" in doc:
            del doc["_id"]
        return Book(**doc)
