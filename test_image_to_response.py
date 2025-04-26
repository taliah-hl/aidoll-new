from  AwsBot import AwsBot

if "__main__" == __name__:
    aws_bot = AwsBot()
    while (True):
        user_input = input("You:  ")
        image_label = aws_bot.image_content('/home/pi/data/test/mh/aidoll-new/imgs/people.jpg')
        response = aws_bot.chat_with_bot(user_input, image_label, '/home/pi/data/test/mh/aidoll-new/chat_record.txt')
        print("Bot: ", response)
