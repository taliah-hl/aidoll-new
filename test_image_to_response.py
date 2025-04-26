from  AwsBot import AwsBot

if "__main__" == __name__:
    aws_bot = AwsBot()
    #while (True):
        #user_input = input("You:  ")
    image_label = aws_bot.image_content(None)
    response = aws_bot.chat_with_bot("你記得我喜歡你什麼嗎?", image_label)
    print("Bot: ", response)
