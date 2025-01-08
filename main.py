import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests  # Pour envoyer des notifications Discord
import time


# Fonction pour envoyer une notification via Discord
def envoyer_notification_discord(webhook_url, title, message, image_url=None):
    # Structure du message à envoyer
    data = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 5814783,  # Couleur (facultatif)
                "image": {
                    "url": image_url  # URL de l'image (facultatif)
                } if image_url else {}
            }
        ]
    }

    # Envoi de la requête POST au webhook Discord
    response = requests.post(webhook_url, json=data)

    # Vérifie si l'envoi a réussi
    if response.status_code == 204:
        print("Notification envoyée avec succès!")
    else:
        print(f"Erreur lors de l'envoi de la notification: {response.status_code}")


def rechercher_annonces():
    """
    Ouvre le navigateur, accède à Vinted avec le filtre 'Derniers articles',
    effectue une recherche avec le mot-clé "lot de cartes Pokémon", puis extrait
    les titres, prix, liens et images des articles affichés.
    """
    # Configuration des options Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Exécution sans interface graphique
    chrome_options.add_argument("--disable-gpu")  # Désactive l'accélération matérielle
    chrome_options.add_argument("--no-sandbox")  # Désactive le sandboxing

    # Démarrage du navigateur (avec Selenium Manager)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # URL avec le filtre "Derniers articles"
        mot_cle = "lot de cartes Pokémon"  # Mot-clé fixe
        url = f"https://www.vinted.fr/catalog?search_text={mot_cle}&order=newest_first&page=1"
        driver.get(url)
        print(f"Page de recherche Vinted pour '{mot_cle}' avec tri par 'Derniers articles' chargée.")

        # Attendre et accepter les cookies (si le bouton est présent)
        try:
            accept_cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies_button.click()
            print("Cookies acceptés.")
        except Exception as e:
            print(f"Aucun bouton de cookies trouvé ou déjà accepté : {e}")

        # Attendre que les résultats se chargent
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "feed-grid__item"))
        )

        # Récupérer les liens des articles et les images
        items = driver.find_elements(By.CLASS_NAME, "feed-grid__item")

        # Vérifier si des articles ont été trouvés
        if not items:
            print("Aucun article trouvé.")
            return  # Sortir de la fonction si aucun article n'est trouvé

        article_data = []
        message = "Voici les derniers articles trouvés :\n"

        for item in items[:10]:  # Limite à 10 résultats
            try:
                # Trouver le lien de l'article
                article_link = item.find_element(By.CSS_SELECTOR, "a.new-item-box__overlay")
                article_url = article_link.get_attribute("href")  # Récupère l'URL de l'article

                # Trouver l'image de l'article
                image_element = item.find_element(By.CSS_SELECTOR, "img")
                image_url = image_element.get_attribute("src")  # Récupère l'URL de l'image

                # Extraire le titre et d'autres informations
                article_title = article_link.get_attribute("title")  # Récupère le titre de l'article
                article_data.append([article_title, article_url, image_url])

                # Formatage du message pour la notification
                message += f"**{article_title}**\n{article_url}\n\n"

                print(f"Article : {article_title}")
                print(f"Lien : {article_url}")
                print(f"Image : {image_url}")
                print("-" * 50)  # Séparateur pour chaque article

            except Exception as e:
                print(f"Erreur lors de l'extraction des données d'un article : {e}")


        # Envoyer une notification via Discord avec les articles
        webhook_url = "https://discord.com/api/webhooks/1322892176564424744/IRNz4YR1Ij8kJ4VE7iOfx64HtKgMyDXLFyoVA6srOQcebGCrJ4t7udIvHeuhxqF-6cM9"  # Remplace par ton URL de webhook
        title = "Nouveaux Articles Pokémon"
        envoyer_notification_discord(webhook_url, title, message)

    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")

    finally:
        # Fermer le navigateur
        driver.quit()
        print("Navigateur fermé.")



# Exécution du script toutes les 20 minutes
if __name__ == "__main__":
    while True:
        rechercher_annonces()
        time.sleep(1200)  # Pause de 20 minutes avant de relancer la recherche