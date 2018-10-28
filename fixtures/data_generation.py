import random
from datetime import timedelta

from django.utils import timezone

from yaasApp.models import *


class Populate:

    def addUser(self, number):
        user = User()
        user.username = "user" + str(number)
        user.set_password("user" + str(number))
        user.first_name = "First" + str(number)
        user.last_name = "Last" + str(number)
        user.email = "user" + str(number) + "@yaasmail.com"
        user.save()

    def addAuction(self, number, seller):
        auction = Auction()
        auction.title = "Title" + str(number)
        auction.description = "This is a description of item number " + str(number)
        auction.minimum_price = 24.50 + number
        auction.end_date = timezone.now() + timedelta(days=random.randint(3, 7))
        auction.seller = seller
        auction.save()

        # make 0-8 bids on each auction
        for bidder_id in random.sample(range(1, 51), random.randint(0, 9)):
            if bidder_id is not seller.id:
                bidder = User.objects.get(username="user"+str(bidder_id))
                self.makeBid(auction, bidder)

    def makeBid(self, auction, bidder):
        bid = Bid()
        bid.auction = auction
        bid.bidder = bidder
        latest = auction.getLatestBid()
        if latest > 0:
            bid.bid = latest + 1
        else:
            bid.bid = auction.minimum_price + 1
        bid.save()

    def doPopulate(self):

        # Create admin
        User.objects.create_superuser(username="Admin", password="Admin2018", email="admin@yaasmail.com")

        # Create 50 users
        for number in range(1, 51):
            self.addUser(number)

        # Create 50 auctions with random sellers
        for number in range(1, 51):
            seller = User.objects.get(username="user"+str(random.randint(1, 50)))
            self.addAuction(number, seller)
