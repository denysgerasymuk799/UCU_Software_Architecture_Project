from sqlalchemy.sql import text
import configparser
import faust


config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
MONEY_TRANSACTION_TOPIC = config['Producer']['money_transaction_topic']
ip_address = config['Producer']['ip_address']

app = faust.App('telegram-messages-stream', broker=ip_address)
transaction_topic_obj = app.topic(MONEY_TRANSACTION_TOPIC)

# connect data base
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False
})
db.init_app(app)


@app.agent(transaction_topic_obj)
async def process_cards_transaction(transactions):
    async for transaction in transactions:
        # TODO: save info about transaction in MongoDB
        statement = text(
            """
            UPDATE user_money
            SET money_balance = (SELECT money_balance FROM user_money WHERE card_number = :from_card_number) - :money_amount
            WHERE card_number = :from_card_number;
            """
        )

        rs = db.session.execute(statement, {
            "from_card_number": transaction["from_card_number"],
            "money_amount": transaction["amount"]
        })

        statement = text(
            """
            UPDATE user_money
            SET money_balance = (SELECT money_balance FROM user_money WHERE card_number = :to_card_number) + :money_amount
            WHERE card_number = :to_card_number;
            """
        )

        rs = db.session.execute(statement, {
            "to_card_number": transaction["to_card_number"],
            "money_amount": transaction["amount"]
        })
        db.session.commit()
        db.session.close()

        results = rs.fetchall()
        print("request1_handle -- ", results)


if __name__ == '__main__':
    app.main()
