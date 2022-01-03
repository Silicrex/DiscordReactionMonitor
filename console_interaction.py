import os
import json


def get_console_confirmation(question):
    # Adds " (y/n)" text. Does not add the question mark.
    # example question input: 'Generate the file?'
    while True:  # Repeat until 'y'/'yes' or 'n'/'no' are given
        print(question + ' (y/n)')
        console_response = input().lower()
        if console_response in {'y', 'yes'}:
            return True
        elif console_response in {'n', 'no'}:
            return False


def get_bot_token():
    if os.path.isfile('token.json'):  # token.json exists, attempt to read the token from it
        with open('token.json') as file:
            try:
                token = json.load(file)  # If successful, then return token
                return token
            except json.JSONDecodeError:
                print('token.json could not parsed. Is it formatted correctly?', end='\n\n')
                if get_console_confirmation('Should I overwrite the token to it?'):
                    print()  # Newline
                    return write_token()  # Returns token back
                else:
                    quit()
    else:  # token.json file does not exist in directory
        print('ERROR: Could not find token.json file')
        if not get_console_confirmation('Should I generate it?'):  # Offer to generate token.json in directory
            quit()
        with open('token.json', 'w') as file:  # Confirmed; proceed to generate file
            pass
        print()  # Newline
        print('Generated token.json. It should contain your bot token as a double-quote string.')
        if get_console_confirmation('Should I write the token to it?'):
            print()  # Newline
            return write_token()  # Returns token back
        else:
            quit()


def write_token():
    with open('token.json', 'w') as file:
        print('Enter your token, without quotes:')
        token = input()
        json.dump(token, file)
        return token
