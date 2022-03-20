import configparser
import faust


config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
MONEY_TRANSACTION_TOPIC = config['Producer']['money_transaction_topic']
ip_address = config['Producer']['ip_address']

app = faust.App('telegram-messages-stream', broker=ip_address)
transaction_topic_obj = app.topic(MONEY_TRANSACTION_TOPIC)


@app.agent(transaction_topic_obj)
async def filter_messages(records):
    async for record in records:
        if record['id'] > 154_000:
            print("record['id'] -- ", record['id'])
            await important_topic_obj.send(value=record)


if __name__ == '__main__':
    app.main()
