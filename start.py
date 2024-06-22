# By Doublegram Labs - www.doublegram.com
# Scrape hidden members on Telegram!
# Edit the configuration variables before running

from telethon import TelegramClient, errors
import asyncio
import os, csv, string, configparser



#----------------------------------------------------------------------------------------------
# Configuration variables
#This account will read the chat
api_id = 'YOUR API HERE'
api_hash = 'YOUR HASH HERE'
phone_number = 'YOUR PHONE NUMBER HERE'

# Those accounts will get the users data
accounts = [
    {'phone': '44444444444', 'api_id': '4444444', 'api_hash': '444444444444444444444444444'},
    # {'phone': 'account_phone_2', 'api_id': 'api_id_2', 'api_hash': 'api_hash_2'},
]

group_id = '@example'  # Group ID or group username (e.g., 'group_username')
batch_size = 50  # Number of messages to retrieve at a time
message_limit = 50  # Total limit of messages to analyze
requests_per_account = 5  # Number of requests per account

#-----------------------------------------------------------------------------------------------



# Global array to store found user IDs
user_ids = set()
user_data = []


# Initialize the Telethon client for the main account
client = TelegramClient(phone_number, api_id, api_hash)

async def get_user_data():
    user_ids_list = list(user_ids)
    total_users = len(user_ids_list)
    account_index = 0
    user_index = 0

    while user_index < total_users:
        account = accounts[account_index]
        temp_client = TelegramClient(account['phone'], account['api_id'], account['api_hash'])
        await temp_client.start(account['phone'])
        
        print(f"Using account: {account['phone']} to get user data...")
        
        requests_count = 0

        while requests_count < requests_per_account and user_index < total_users:
            user_id = user_ids_list[user_index]
            try:
                input_entity = await temp_client.get_input_entity(user_id)
                user = await temp_client.get_entity(input_entity)

                with open("members.csv",'a',encoding='UTF-8') as f:
                    writer = csv.writer(f,delimiter=",",lineterminator="\n")
                    if user.username:
                        username = user.username
                    else:
                        username = ""
                    if user.first_name:
                        first_name = user.first_name
                    else:
                        first_name = ""
                    if user.last_name:
                        last_name = user.last_name
                    else:
                        last_name = ""
                    
                    name = (first_name + ' ' + last_name).strip()

                    if user.photo:
                        dc_id = user.photo.dc_id
                        have_photo = True
                    else:
                        dc_id = False
                        have_photo = False

                    if user.bot != False:
                        is_bot = True
                    else:
                        is_bot = False

                    if user.phone != None:
                        phone = user.phone
                    else:
                        phone = False
                    
                    if user.premium == True:
                        is_premium = True
                    else:
                        is_premium = False

                    is_admin = False
                
                    writer.writerow([username, user.id, user.access_hash, name, 'HIDDEN MEMBERS GROUP', group_id, is_bot, is_admin, dc_id, have_photo, phone, 0, is_premium])      

                

                user_index += 1
                requests_count += 1
            except errors.UsernameNotOccupiedError:
                print(f"User with ID {user_id} does not have a username.")
                user_index += 1
            except errors.UserIdInvalidError:
                print(f"User ID {user_id} is invalid.")
                user_index += 1
            except Exception as e:
                print(f"Error getting data for user {user_id}: {e}")
                user_index += 1
        
        await temp_client.disconnect()
        account_index = (account_index + 1) % len(accounts)

async def main():
    await client.start(phone_number)
    print("Client connected!")

    try:
        total_messages_analyzed = 0
        async for message in client.iter_messages(group_id, limit=message_limit):
            if message.sender_id:
                user_ids.add(message.sender_id)
                total_messages_analyzed += 1

            if total_messages_analyzed % batch_size == 0:
                print(f'{total_messages_analyzed} messages analyzed...')
            
            if total_messages_analyzed >= message_limit:
                break

        print(f'Analysis complete. Total messages analyzed: {total_messages_analyzed}')
        print(f'Total users found: {len(user_ids)}')
        print('List of user IDs:', user_ids)

        await client.disconnect()

        await get_user_data()

    except errors.ChatIdInvalidError:
        print("Error: The group ID is invalid or the group does not exist.")
    except errors.ChatWriteForbiddenError:
        print("Error: You do not have the necessary permissions to view messages in this group.")
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
