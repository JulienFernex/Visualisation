"""
Point d'entrée principal du projet de visualisation
Lance l'application Dash du dashboard
"""

from dashboard.app import app

if __name__ == '__main__':
    app.run(debug=True)
