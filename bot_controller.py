from bot import SpotifyBot
import os


if __name__ == "__main__":
    CREATE_ACCOUNT = False
    
    cards_file = input("cards filename: ")
    if not os.path.exists(cards_file):
        print("File not found!")
        exit(-1)

    cards_dict = {}
    with open(cards_file, "r") as f:
        for indx, card in enumerate(f.readlines()):
            card = card.strip()
            email, password, card_info = card.split(":")
            cards_dict[indx] = {
                "email": email,
                "password": password, 
                "card": card_info
             }

    for indx, info in cards_dict.items():
        bot = SpotifyBot (
            card=info["card"],
            email=info["email"],
            password=info["password"],
            reference=f"refer-{indx}",
            is_headless=False,
        )

        if CREATE_ACCOUNT:
            if not bot.create_account():
                print(f"Account Error: {bot.email}:{bot.password}:{info['card']}")
                print("Moving to next")
                bot.driver.quit()
                continue
        else:
            bot.login(info["email"], info["password"])

        res = bot.premify()
        if res:
            print("Success!")
        else:
            print(
                f"Error! failed to premify {info['email']}:{info['password']}:{info['card']}"
            )
            print("Moving to next")
            continue
