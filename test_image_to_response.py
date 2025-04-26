from  AwsBot import AwsBot

if "__main__" == __name__:
    aws_bot = AwsBot()
    while (True):
        user_input = input("You:  ")
        image_label = aws_bot.image_content(None)
        response = aws_bot.chat_with_bot(user_input, None, '/home/pi/data/test/jw/aidoll-new/chat_record.txt')
        print("Bot: ", response)
