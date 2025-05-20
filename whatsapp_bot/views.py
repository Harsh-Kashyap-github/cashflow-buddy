from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
# from .utils.gemini import *
from .utils.ai_agent import *
from datetime import datetime
from .models import Friends,Transactions,Feedback

# Create your views here.
@csrf_exempt
def whatsAppBotResponce(request):
    if request.method == 'POST':
        from_number = request.POST.get('From', '')
        message_body = request.POST.get('Body', '')

        print(f"User {from_number} said: {message_body}")

        # Create a Twilio response
        resp = MessagingResponse()
        msg = resp.message()

        try:
            customerQuery=engagement(message_body)
            result=extract_transactions_gemini(message_body)
            
            if customerQuery['isGreetingGiven']:
                msg.body(customerQuery['greeting_msg'] +'\n')
                
            if customerQuery['isFeedBackGiven']:
                feedback=Feedback(customerID=from_number,feedback=customerQuery['feedback'],timeOfSubmission=datetime.now())
                feedback.save()
                msg.body(customerQuery['feedback_accepted_msg'] + '\n')
            
            if customerQuery['founderQuestionsAsked']:
                msg.body(customerQuery['answer_for_quetion'] + '\n')
            
            

            
            if len(result)!=0:
                #detecting new friends and fixing the friends name
                oldFriends=Friends.get_friends_name(friendOf=from_number)
                new_friends_info,result=extract_new_friends(result,oldFriends)
                for info in new_friends_info:
                    new_friend=Friends(name=info,amount=0,friendOf=from_number)
                    new_friend.save()
                #Sending Responce
                message='''TRANSACTIONS RECORDED \n'''
                for t in result:
                    message+=f"-> {t['payer']} → {t['receiver']}:₹{abs(t['amount'])} \n"
                    #Adding new tranaction
                    new_transcation=Transactions(payer=t['payer'], receiver=t['receiver'],amount=float(abs(t['amount'])),timeOfTransaction=datetime.now(),AccountID=from_number)
                    new_transcation.save()
                    #Updating friend amount
                    name= t['receiver'] if t['payer']=='You' else t['payer']
                    friend=Friends.objects.get(name=name,friendOf=from_number)
                    friend.amount+=t['amount']
                    friend.save()
                    
                msg.body(message)
            else:
                msg.body(customerQuery['out_of_scope_question_answer'] + '\n')
                
            if customerQuery['asked_for_transaction_summary']:
                summary=Friends.get_summary(friendOf=from_number)
                sumi='''BUDDY SUMMARY \n'''
                for friend in summary:
                    sumi+=f"{friend}:₹{float(summary[friend])*-1} \n"
                msg.body(sumi)
        except NameError as e:
            msg.body('An error has occurred! \n')
            print('error:',e)

        return HttpResponse(str(resp), content_type='text/xml')

    return HttpResponse("Only POST allowed", status=405)