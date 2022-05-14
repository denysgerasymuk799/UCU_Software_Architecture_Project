# importing Mongoclient from pymongo
import os

from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    client = MongoClient(os.getenv('MONGODB_URL'))

    # database
    db = client["web_banking"]

    # Created or Switched to collection
    # names: GeeksForGeeks
    collection = db["registration_cards"]

    with open('./20K.txt', 'r', encoding='utf-8') as f:
        cards_info = f.readlines()

    batch = []
    card_ids = set()
    for idx, card_info in enumerate(cards_info):
        card_id, expiration_date, cvv = card_info.strip().split()
        if card_id in card_ids:
            continue

        card_ids.add(card_id)
        batch.append({"card_id": card_id, "expiration_date": expiration_date, "cvv": cvv, "enabled": False})

        if len(batch) >= 100:
            # Inserting the entire list in the collection
            collection.insert_many(batch)
            print(f'Last added card index -- {idx}/{len(cards_info)}')
            batch = []
