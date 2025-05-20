from django.db import models
from django.db import connection
# Create your models here.

class Friends(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    friendOf = models.CharField(max_length=20)

    @staticmethod
    def get_friends_name(friendOf):
        # Returns a list of distinct names of friends for a given friendOf
        return list(
            Friends.objects.filter(friendOf=friendOf)
            .values_list('name', flat=True)
            .distinct()
        )

    @staticmethod
    def get_summary(friendOf):
        # Returns a dict with distinct friend names as keys and total amount as values
        friends = Friends.objects.filter(friendOf=friendOf)
        summary = {}
        for friend in friends:
            # if friend.name in summary:
            #     summary[friend.name] += friend.amount
            # else:
                summary[friend.name] = friend.amount
        return summary

    def __str__(self):
        return f"{self.name} (Friend of {self.friendOf})"


class Transactions(models.Model):
    payer = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.FloatField()
    timeOfTransaction = models.DateTimeField()
    AccountID = models.CharField(max_length=20)

    @staticmethod
    def custom_query(AccountID, query):
        # Executes the raw SQL query with a filter on AccountID
        with connection.cursor() as cursor:
            cursor.execute(query, [AccountID])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def __str__(self):
        return f"{self.payer} paid {self.receiver} Rs.{self.amount} on {self.timeOfTransaction}"


class Feedback(models.Model):
    customerID=models.CharField(max_length=100)
    feedback=models.CharField(max_length=1000)
    timeOfSubmission = models.DateTimeField()
    
    def __str__(self):
        return f"{self.customerID} + {self.timeOfSubmission}"
    