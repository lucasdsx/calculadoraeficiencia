from calculadoraeficiencia import database, app
from calculadoraeficiencia.models import Cliente


with app.app_context():
    database.create_all()