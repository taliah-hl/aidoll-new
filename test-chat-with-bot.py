from AwsBot import AwsBot

if "__main__" == __name__:
    bot = AwsBot()
    while(True):
        print()
        print(f"You     : ", end="")
        user_input = input()
        response = bot.chat_with_bot(user_input)
        print("Bot: ",response)  # Expected to print the bot's response to the message.