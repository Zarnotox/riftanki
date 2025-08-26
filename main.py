import genanki
import requests
import os
import time

API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXX"
API_URL = "https://europe.api.riotgames.com/riftbound-content/v1/content"
MEDIA_DIR = "riftbound_media"
OUTPUT_DECK_FILE = "Riftbound_Anki_Deck.apkg"

MODEL_ID_IMAGE_TO_NAME = 2121972233
DECK_ID_IMAGE_TO_NAME = 1841136991

MODEL_ID_NAME_TO_STATS = 1706022021
DECK_ID_NAME_TO_STATS = 1726608368

model_image_to_name = genanki.Model(
    MODEL_ID_IMAGE_TO_NAME,
    'Riftbound - Image to Name',
    fields=[
        {'name': 'CardName'},
        {'name': 'CardImage'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{CardImage}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{CardName}}',
        },
    ])

model_name_to_stats = genanki.Model(
    MODEL_ID_NAME_TO_STATS,
    'Riftbound - Name to Stats',
    fields=[
        {'name': 'CardName'},
        {'name': 'Energy'},
        {'name': 'Might'},
        {'name': 'Cost'},
        {'name': 'Power'},
        {'name': 'Description'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<h1>{{CardName}}</h1>',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div style="text-align: left; font-size: 18px;">
                    <b>Energy:</b> {{Energy}}<br>
                    <b>Might:</b> {{Might}}<br>
                    <b>Cost:</b> {{Cost}}<br>
                    <b>Power:</b> {{Power}}
                </div>
                <hr>
                <div style="font-style: italic;">{{Description}}</div>
            ''',
        },
    ])

def generate_anki_decks():
    print("Starting Anki deck generation for Riftbound...")

    os.makedirs(MEDIA_DIR, exist_ok=True)
    headers = {"X-Riot-Token": API_KEY}
    media_files = []

    try:
        print(f"Fetching card data from {API_URL}...")
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        card_data = response.json()
        print(f"Successfully fetched data for {len(card_data)} cards.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        print("Please check your API key and the API_URL.")
        return

    deck1 = genanki.Deck(DECK_ID_IMAGE_TO_NAME, 'Riftbound::Deck 1 (Image -> Name)')
    deck2 = genanki.Deck(DECK_ID_NAME_TO_STATS, 'Riftbound::Deck 2 (Name -> Stats)')

    print("Processing cards and downloading images...")
    for card in card_data:
        card_name = card.get('name', 'Unknown Card')
        image_url = card.get('imageUrl')

        if image_url:
            try:
                image_filename = f"rb_{''.join(filter(str.isalnum, card_name))}.jpg"
                image_path = os.path.join(MEDIA_DIR, image_filename)

                if not os.path.exists(image_path):
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    time.sleep(0.1)

                media_files.append(image_path)

                note1 = genanki.Note(
                    model=model_image_to_name,
                    fields=[card_name, f'<img src="{image_filename}">']
                )
                deck1.add_note(note1)

            except requests.exceptions.RequestException as e:
                print(f"Could not download image for {card_name}: {e}")
            except Exception as e:
                print(f"An error occurred processing image for {card_name}: {e}")


        note2 = genanki.Note(
            model=model_name_to_stats,
            fields=[
                card_name,
                str(card.get('energy', 'N/A')),
                str(card.get('might', 'N/A')),
                str(card.get('cost', 'N/A')),
                str(card.get('power', 'N/A')),
                card.get('description', 'N/A')
            ]
        )
        deck2.add_note(note2)

    print("All cards processed. Generating Anki package...")
    package = genanki.Package([deck1, deck2])
    package.media_files = media_files
    package.write_to_file(OUTPUT_DECK_FILE)
    print("Success!")


if __name__ == "__main__":
    generate_anki_decks()