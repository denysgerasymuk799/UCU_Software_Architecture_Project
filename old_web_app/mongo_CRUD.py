from pymongo import MongoClient
from random import randint
from pprint import pprint


if __name__ == '__main__':
    client = MongoClient(
        "mongodb+srv://test_user21032022:Gvagd6gpPyFDK8b@cluster0.tk1iw.mongodb.net/web_banking?retryWrites=true&w=majority")
    db = client.web_banking

    # # ################### Insert ###################
    # # Step 2: Create sample data
    # names = ['Kitchen', 'Animal', 'State', 'Tastey', 'Big', 'City', 'Fish', 'Pizza', 'Goat', 'Salty', 'Sandwich',
    #          'Lazy', 'Fun']
    # company_type = ['LLC', 'Inc', 'Company', 'Corporation']
    # company_cuisine = ['Pizza', 'Bar Food', 'Fast Food', 'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
    # for x in range(1, 501):
    #     business = {
    #         'name': names[randint(0, (len(names) - 1))] + ' ' + names[randint(0, (len(names) - 1))] + ' ' +
    #                 company_type[randint(0, (len(company_type) - 1))],
    #         'rating': randint(1, 5),
    #         'cuisine': company_cuisine[randint(0, (len(company_cuisine) - 1))]
    #     }
    #     # Step 3: Insert business object directly into MongoDB via insert_one
    #     result = db.users.insert_one(business)
    #     # Step 4: Print to the console the ObjectID of the new document
    #     print('Created {0} of 500 as {1}'.format(x, result.inserted_id))
    # # Step 5: Tell us that you are done
    # print('finished creating 500 business users')

    # # ################### Exploring business review data ###################
    # # DOES NOT WORK
    # fivestar = db.users.find_one({'rating': 5})
    # print(fivestar)
    #
    # fivestarcount = db.users.find({'rating': 5}).count()
    # print(fivestarcount)

    # # ######## Showcasing the count() method of find, count the total number of 5 ratings ########
    # # print('The number of 5 star users:')
    # # fivestarcount = db.users.find({'rating': 5}).count()
    # # print(fivestarcount)
    #
    # # Now let's use the aggregation framework to sum the occurrence of each rating across the entire data set
    # print('\nThe sum of each rating occurance across all data grouped by rating ')
    # stargroup = db.users.aggregate(
    #     # The Aggregation Pipeline is defined as an array of different operations
    #     [
    #         # The first stage in this pipe is to group data
    #         {'$group':
    #              {'_id': "$rating",
    #               "count":
    #                   {'$sum': 1}
    #               }
    #          },
    #         # The second stage in this pipe is to sort the data
    #         {"$sort": {"_id": 1}
    #          }
    #         # Close the array with the ] tag
    #     ])
    # # Print the result
    # for group in stargroup:
    #     print(group)

    # ################ Updating data with PyMongo ################
    ASingleReview = db.users.find_one({})
    print('A sample document:')
    pprint(ASingleReview)

    result = db.users.update_one({'_id': ASingleReview.get('_id')}, {'$inc': {'likes': 1}})
    print('Number of documents modified : ' + str(result.modified_count))

    UpdatedDocument = db.users.find_one({'_id': ASingleReview.get('_id')})
    print('The updated document:')
    pprint(UpdatedDocument)
