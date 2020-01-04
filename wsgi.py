from assemblr import app
from utl import models

models.db.init_app(app)
with app.app_context():
    models.db.create_all()

if __name__ == "__main__":
    app.run()
