import uuid
import hashlib
import pymysql.cursors
import random

#################################################
###               Login Methods               ###
#################################################

# Allow user's to create an account
def create_account():
    
    # Get the user's information to create their account
    new_user = input('Enter a user name: ')
    new_pass = input('Enter a password: ')
    salt = uuid.uuid4()
    salt = str(salt)
    to_encode = new_pass + salt
    user_hash = hashlib.sha256(to_encode.encode())

    # Create the connection to the database
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO User(Username, Salt, Hash, InGameCurrency) VALUES (%s, %s, %s, %s) "
            to_sql = (new_user, salt, user_hash.hexdigest(), 10000)
            cursor.execute(sql, to_sql)
            connection.commit()
            print('\n\nTest your account credentials')
            login()
    except:
        print('\nError creating user, try a different username\n')
        print_menu()
    finally:
        connection.close()


# Provide user with standard login
def login():
    # Prompt users for their login information
    user = input('Enter your username: ')
    password = input('Enter your password: ')

    # Create the connection to the database
    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            salt = ''      #if db does not find value for salt or hash, makes it so if to_compare == str(user_hash) is to_compare == 0
            user_hash = ''
            # Get a list of the users from the Username table
            sql = "SELECT * FROM User WHERE Username = %s"
            to_sql = user
            cursor.execute(sql, to_sql)
            for row in cursor:
                valid_user = row['Username']
                salt = row['Salt']
                user_hash = row['Hash']
            salt = str(salt)
            to_encode = password + salt
            result_hash = hashlib.sha256(to_encode.encode())
            to_compare = result_hash.hexdigest()
            
            # Check to see if the hashed values match
            if to_compare == str(user_hash):
                print('\nLogin Successful\n\n')
                game_functions(valid_user)  
            else:
                # If the login failed take them to the home screen
                print('\nLogin failed, try again if you please\n\n')
                print_menu()
    except:
        print('\nError Logging In\n')
        login()
    finally:
        connection.close()


# Show the developer menu
def developer_login():
    # For double validation that the user is a developer
    user = input('Enter your username: ')
    password = input('Enter your password: ')
    connection = create_connection()

    try:
        with connection.cursor() as cursor:

            # If db does not find value for salt or hash, makes it so if to_compare == str(user_hash) is to_compare == 0
            salt = ''
            user_hash = ''
            
            # Get a list of all the users in the table
            sql = "SELECT * FROM User WHERE Username = %s"
            to_sql = user
            cursor.execute(sql, to_sql)
            for row in cursor:
                valid_user = row['Username']
                salt = row['Salt']
                user_hash = row['Hash']
            # Check to see if the user is an admin or not
            sql = "SELECT AdminID From Admin WHERE AdminID = %s"
            cursor.execute(sql, to_sql)
            admin = 'no'
            for row in cursor:
                admin = row['AdminID']
            salt = str(salt)
            to_encode = password + salt

            result_hash = hashlib.sha256(to_encode.encode())
            to_compare = result_hash.hexdigest()
            if to_compare == str(user_hash):
                if admin == user:
                    # If the user is an admin send them to the developer menu
                    print('\nAdmin permissions enabled')
                    developer_menu()
                else:
                    # Otherwise send them to a standard user menu
                    print('\nYou are not an admin, permissions denied, logging in to standard acount...\n')
                    game_functions(valid_user)
            else:
                print('\nLogin Failed\n')
                print_menu()
    except:
        print('\nError Logging In As Admin\n')
    finally:
        connection.close()

# Print the main menu for the users
def print_menu():
    menu_select = 0

    print('Enter 1: To create a new account.')
    print('Enter 2: To login to an existing account.')
    print('Enter 3: Developer login.')
    print('Enter 4: To exit')

    menu_select = int(input('Enter Selection: '))
    
    if menu_select == 1:
        create_account()
    elif menu_select == 2:
        login()
    elif menu_select == 3:
        developer_login()
    elif menu_select == 4:
        menu_select = 4
        
        
        
        
        
#################################################
###          Standard User Methods            ###
#################################################
        
# Provide the user with their options
def game_functions(valid_user):
    menu_select = 0

    print('Enter 1: To buy 5 card pack.')
    print('Enter 2: To trade in cards')
    print('Enter 3: Create a 5 card deck')
    print('Enter 4: View Inventory')
    print('Enter 5: View decks')
    print('Enter 6: Add Payment Info')
    print('Enter 7: Buy in game currency')
    print('Enter 8: Exit to login screen')

    menu_select = int(input('Enter Selection: '))
    
    # Based on user input go to function
    if menu_select == 1:
        buy_cards(valid_user)
    elif menu_select == 2:
        trade_in_cards(valid_user)
    elif menu_select == 3:
        create_deck(valid_user)
    elif menu_select == 4:
        view_inventory(valid_user)
    elif menu_select == 5:
        view_decks(valid_user)
    elif menu_select == 6:
        add_payment_info(valid_user)
    elif menu_select == 7:
        buy_game_currency(valid_user)
    elif menu_select == 8:
        print('\n')
        print_menu()


# Allow the user to buy new cards with in-game currency
def buy_cards(valid_user):
    connection = create_connection()
    
    # Get everything from Pack
    sql = "SELECT * FROM Pack"
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # Print information about the packs
            for row in cursor:
                PackName= row['PackName']
                Description= row['Description']
                print('\nPackname: ' + PackName)
                print('Description: ' + Description + '\n')

            # Allow the user to select a pack to buy cards from
            pack_name = input("Select pack to buy: ")
            sql = "SELECT PackID from Pack WHERE PackName = %s"
            cursor.execute(sql, pack_name)
            for row in cursor:
                packID = row['PackID']
            card_range = packID * 100
            
            # Select a random card from the pack that the user selects
            i = 0
            while i < 5:
                cardID = card_range + (random.randrange(0, 100))
                sql1 = "INSERT INTO Inventory(Username, CardID) VALUES(%s, %s)"
                to_sql1 = (valid_user, cardID)
                cursor.execute(sql1, to_sql1)
                connection.commit()
                i += 1
                
            # Get the cost of buying five cards
            sql = "SELECT CostOfFive FROM Pack WHERE PackID = %s"
            cursor.execute(sql, packID)
            
            for row in cursor:
                cost = row['CostOfFive']
            
            # Get the user's current value of in-game currency
            sql = "Select InGameCurrency From User Where Username = %s"
            cursor.execute(sql, valid_user)
            for row in cursor:
                gameCurrency = row['InGameCurrency']
            
            # If the user doesn't have enough currency, notify them
            # Else commit the changes
            if gameCurrency < cost:
                print("Sorry, you do not have enough currency to buy cards")
                game_functions(valid_user)
            else:
                gameCurrency = gameCurrency - cost
                # Update the user's current in-game currency into the user table
                sql = "UPDATE User SET InGameCurrency = %s WHERE Username = %s"
                to_sql = (gameCurrency, valid_user)
                cursor.execute(sql, to_sql)
                connection.commit()
            print('\nCards have been purchased, your new game balance is: ', gameCurrency, '\n\n')

    except:
        print('\nError Buying Cards\n')            
    finally:
        connection.close()
        game_functions(valid_user)
        


# Allow the user to trade in cards for in-game currency
def trade_in_cards(valid_user):
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            
            # Get a list of all cards in the user's inventory
            sql = "SELECT * FROM Card INNER JOIN Inventory ON Card.CardID = Inventory.CardID WHERE Username = %s"
            cursor.execute(sql, valid_user)

            print('Here is a list of cards in your inventory: ')
            
            # Print each card's information
            for row in cursor:
                cardID = row['CardID']
                cardDesc = row['Description']
                rarity = row['Rarity']
                print('\nCardID: ', cardID)
                print('Card Rarity: ' + rarity)
                print('Description: ' + cardDesc + '\n')

            # Get the rarity of a card that the user wants to trade in
            pack_name = input("Select card to trade in for in-game currency: ")
            sql = "SELECT RarityID, Cost FROM Rarity WHERE RarityID = %s"
            cursor.execute(sql, rarity)
            for row in cursor:
                cost = row['Cost']
            
            # Get the user's in-game currency
            sql = "SELECT InGameCurrency FROM User WHERE Username = %s"
            cursor.execute(sql, valid_user)
            for row in cursor:
                inGameCurrency = row['InGameCurrency']
                
            # Set the value of the user's in-game currency
            inGameCurrency = inGameCurrency + cost
            
            # Update the table's value of in-game currency for the current user and commit
            sql = "UPDATE User SET InGameCurrency = %s WHERE Username = %s"
            to_sql = (inGameCurrency, valid_user)
            cursor.execute(sql, to_sql)
            connection.commit()
            print('\nCards Have Been Traded Your New Balance Is: ', inGameCurrency, '\n\n')
    except:
        print('\nError Trading Cards\n')             
    finally:
        connection.close()
        game_functions(valid_user)
        

# Allow the user to create a deck of cards
def create_deck(valid_user):
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            
            # Selct each card in the current user's inventory
            sql = "SELECT * FROM Card INNER JOIN Inventory ON Card.CardID = Inventory.CardID WHERE Username = %s"
            cursor.execute(sql, valid_user)
            
            print("Here is a list of all cards in your inventory: ")

            # Print information about each card in the user's inventory
            for row in cursor:
                cardName = row['Name']
                print("\nName: ", cardName)
                cardID = row['CardID']
                print("Card ID: ", cardID)
                description = row['Description']
                print("Description: ", description)
                print('\n')
                
            # Get the deck name
            deckName = input('Enter a name for your deck: ')
            # Generate a unique id for each deck
            deckID = str(uuid.uuid4())
            
            # Allow the user to enter cards in a deck
            i = 0
            while i < 5:
                cardToDeck = input('Enter the Id of the card you want in your deck(must be valid): ')
                sql = "INSERT INTO Deck(DeckID, CardID, DeckName) VALUES (%s, %s, %s)"
                to_sql = (deckID, cardToDeck, deckName)
                cursor.execute(sql, to_sql)
                i += 1
                connection.commit()
            print('The cards you selected have been placed in the deck called: ', deckName, '\n\n')
    except:
        print('\nError Creating Deck\n') 
    finally:
        connection.close()
        game_functions(valid_user)
        

    
# Allows the current user to view their inventory
def view_inventory(valid_user):
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            
            # Get the inventory of the current user
            sql = "SELECT * FROM Card INNER JOIN Inventory ON Card.CardID = Inventory.CardID WHERE Username = %s"
            cursor.execute(sql, valid_user)
            
            print("Here is a list of all cards in your inventory: ")
            
            # Print information of each card in inventory
            for row in cursor:
                cardName = row['Name']
                print("\nName: ",cardName)
                cardID = row['CardID']
                print("Card ID: ",cardID)
                description = row['Description']
                print("Description: ",description)
                special = row['SpecialAbility']
                print("Special Ability: ",special)
                print('')
    except:
        print('\nError Viewing Inventory\n') 
    finally:
        connection.close()
        game_functions(valid_user)
        
    
# Allow the user to view their cards by deck
def view_decks(valid_user):
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            #Get the deck information for the user based on the current username
            sql = "SELECT * FROM Card INNER JOIN Deck ON Card.CardID = Deck.CardID \
                                      INNER JOIN Inventory ON Card.CardID = Inventory.CardID WHERE Username = %s"
            cursor.execute(sql, valid_user)
            
            print("Here is a list of your decks: \n")

            for row in cursor:
                deckName = row['DeckName']
                print("Deck Name: ",deckName)
                cardName = row['Name']
                print("Name: ",cardName)
                print('')
                
            print('Decks Viewed\n')
    except:
        print('\nError Viewing Deck\n')            
    finally:
        connection.close()
        game_functions(valid_user)

    
    
# Buy in-game currency using a card that is attached to the user's account
def buy_game_currency(valid_user):
    connection = create_connection()
    
    print("Select A Payment Method To Buy In Game Currency: ")
    
    try:
        with connection.cursor() as cursor:
            
            # List all the user's payment options
            sql = "SELECT * FROM PaymentInfo WHERE Username = %s"
            cursor.execute(sql, valid_user)

            for row in cursor:
                cardNumber = row['CreditCardNo']
                print('\nCard Number: ', cardNumber)
                first = row['FirstName']
                last = row['LastName']
                print("Name On Card: ", first, last)
                print('\n')
            
            # Allow the user to select the card they would like to use in the transaction
            card = input('Enter the credit card number of card you would like to use: ')
            
            # Get the user's current in-game balance
            sql = "SELECT InGameCurrency FROM User WHERE Username = %s"
            cursor.execute(sql, valid_user)
            for row in cursor:
                balance = row['InGameCurrency']
            
            # Ask the user how much in-game currency they would like to buy
            purchase = -1
            while purchase < 0:
                purchase = int(input('Enter the amount you would like to buy ($1 = 1 in-game credit): '))
                
            balance = balance + purchase
            
            # Update the user's in-game currency to the value that they requested above using prepared statement
            sql = "UPDATE User SET InGameCurrency = %s WHERE Username = %s"
            to_sql = (balance, valid_user)
            
            # Execute the query and commit it
            cursor.execute(sql, to_sql)
            connection.commit()
            print("Your new balance is: ",balance)
            print()
    except:
        print('\nError Buying In-Game Currency\n') 
    finally:
        connection.close()
        print()
        game_functions(valid_user)
        


#add payment information to account
def add_payment_info(valid_user):
    connection = create_connection()
    
    print('\nHere is a list of your current payment methods: ')
    try:
        with connection.cursor() as cursor:
            
            # Get the users current payment options attached to their account
            sql = "SELECT * FROM PaymentInfo WHERE Username = %s"
            cursor.execute(sql, valid_user)
            for row in cursor:
                card_expiration = row['CardExpiration']
                first = row['FirstName']
                last = row['LastName']
                cardNumber = row['CreditCardNo']
                print(first + ' ' + last)
                print('Card Number:', cardNumber)
                print('Expiration: ' + card_expiration)
                print('')
            
            # Ask if the user would like to add a payment option
            add_info = input('Would you like to add a payment option to your account? (Y/N): ')
            
            # If they respond yes to the previous question ask them questions regarding their credit card
            if add_info is 'Y':
                first = input('\nEnter the first name on the card: ')
                last = input('Enter the last name on the card: ')
                cardNum = input('Enter the card number: ')
                expir = input('Enter the expiration date on the card (MM/YY): ')
                secNum = input('Enter the security number on the back of the card: ')
                address = input('Enter the billing address: ')
                email = input('Enter your email address: ')
                
                # Insert the payment info into the PaymentInfo table with the information that the user provided as a prepared statement
                sql = "INSERT INTO PaymentInfo(CardExpiration, FirstName, LastName, BillingAddress, Username, Email, CreditCardNo, SecurityNumber) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                to_sql = (expir, first, last, address, valid_user, email, cardNum, secNum)
                
                # Execute the query and commit it
                cursor.execute(sql, to_sql)
                connection.commit()
                
                print('Payment option added')
                add_payment_info(valid_user)
            else:
                print('\n')
                game_functions(valid_user)
    except:
        print('\nError Adding Payment Information\n') 
    finally:
        connection.close()
        print('\n\n')
        game_functions(valid_user)
        


        
       
    
    
    
#################################################
###             DEVELOPER METHODS             ###
#################################################
        
# Display the developer menu
def developer_menu():
    menu_select = 0

    print('\n\nEnter 1: To add a card.')
    print('Enter 2: To delete a card.')
    print('Enter 3: Delete account')
    print('Enter 4: To exit')
    menu_select = int(input('Enter Selection: '))
    if menu_select == 1:
        add_card()
    elif menu_select == 2:
        delete_card()
    elif menu_select == 3:
        ban_user()
    elif menu_select == 4:
        print('')
        print_menu()

#Add a card to the game
def add_card():
    
    # Prompt the admin to enter card details
    cardID = int(input("\nEnter the new card's ID: "))
    cardName = input("Enter the card's name: ")
    cardHP = int(input("Enter the card's HP: "))
    cardDesc = input("Enter the card's description: ")
    specialAbility = input("Enter the card's special ability: ")
    rarity = -1
    while(rarity < 0 or rarity > 3):
        rarity = int(input("Enter the card's rarity (0 - 3): "))
    packID = input("Enter the Pack ID that the card belongs to: ")
    
    # Connect to the database
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            # Insert all the card information that the admin specified
            sql = "INSERT INTO Card(CardID, Name, Healthpoints, SpecialAbility, Description, Rarity, PackID) VALUES (%s, %s, %s, %s, %s, %s, %s) "
            to_sql = (cardID, cardName, cardHP, specialAbility, cardDesc, rarity, packID)

            # Execute the SQL command and commit
            cursor.execute(sql, to_sql)
            connection.commit()
            print('\nCard Added')
    except:
        print('\nError Adding Card\n') 
    finally:
        connection.close()  
        developer_menu()


# Delete a card from Card
def delete_card():
    
    # Enter the id of the card that will be deleted
    toDelete = input("Enter the Card ID of the card you would like to delete: ")
    
    # Create connection to the database
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            # Delete the specified card
            sql = "DELETE FROM Card WHERE CardID = %s"
            to_sql = (toDelete)

            # execute the SQL command and commit it
            cursor.execute(sql, to_sql)
            connection.commit()
            print("\nCard has been deleted")
    except:
        print('\nError Deleting Card\n') 
    finally:
        connection.close()
        developer_menu()
    
    
#Delete a user for inexplicable behavior
def ban_user():
    # Allow the developer to delete a user by username
    toDelete = input("Enter the username of the user you would like to delete: ")
    
    # Create connection to the database
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            # Delete the user account
            sql = "DELETE FROM User WHERE Username = %s"
            to_sql = (toDelete)
            # Execute the SQL command and commit
            cursor.execute(sql, to_sql)
            
            #Delete the users inventory as well
            sql = "DELETE From Inventory WHERE Username = %s"
            to_sql = (toDelete)
            # Execute the SQL command and commit
            cursor.execute(sql, to_sql)
            connection.commit()
            print("\nUser has been deleted")
    except:
        print('\nError Deleting User\n')
    finally:
        connection.close()
        developer_menu()






#################################################
###          Connect To The Database          ###
#################################################


#create connection to database
def create_connection():
    connection = pymysql.connect(host='mrbartucz.com',
                                 user='jp6884xv',
                                 password='Baseball.6',
                                 db='jp6884xv_gachaGame',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def main():
    print_menu()


if __name__ == '__main__':  # for import
    main()
