import datetime


def welcome(request):
    """Добавляет в контекст переменную greeting с приветствием."""
    return {
        "greeting": "Ennyn Pronin: pedo mellon a minno.",
    }


def year(request):
    """Добавляет переменную с текущим годом."""
    return {"year": datetime.date.today().year}
