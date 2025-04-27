from  AwsBot import AwsBot

if "__main__" == __name__:
    aws_bot = AwsBot()
    while (True):
        user_input = input("輸入話語:  ")
        response = aws_bot.image_to_response(user_input,
                                                image_path='test_image', 
                                                chat_record_path='test_chat_reacord.txt')
        print("Bot: ", response)
