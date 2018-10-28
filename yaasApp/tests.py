from django.test import TestCase

from yaasApp.forms import *


# Create your tests here.
class AuctionSiteTest(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        self.user1 = "user1"
        self.user2 = "user2"
        self.createUrl = "/YAAS/auction/create/"
        self.confirmationUrl = "/YAAS/auction/create/confirmation/"
        self.bidUrl = "/YAAS/auction/1/bid/"

    def testAuthorizationCreateAuction(self):
        # If the client is not logged in, create_user should give a redirect status (302)
        response = self.client.get(self.createUrl)
        self.assertEqual(response.status_code, 302)

        # Login
        loggedIn = self.client.login(username=self.user1, password=self.user1)
        self.assertTrue(loggedIn)

        # If the client is logged in, create_user should give a success status (200)
        response = self.client.get(self.createUrl)
        self.assertEqual(response.status_code, 200)

    def testCreateAuction(self):
        auctionData = {
            "title": "title",
            "description": "description",
            "end_date": (timezone.now() + timedelta(days=5)).date(),
            "minimum_price": 10.50,
            "option": "Yes"
        }
        # Login
        loggedIn = self.client.login(username=self.user1, password=self.user1)
        self.assertTrue(loggedIn)

        auctions = Auction.objects.all().count()
        # create auction by posting data
        self.client.post(self.confirmationUrl, auctionData)
        # auction count is 1 higher than before
        self.assertEqual(Auction.objects.all().count(), auctions+1)
        self.client.logout()

    def testUnauthorizedBid(self):
        bid = 50.50
        # If the client is not logged in, bid should give a redirect status (302)
        response = self.client.post(self.bidUrl, {"bid": bid, "updated": timezone.now().date()})
        self.assertEqual(response.status_code, 302)

    def testSellerBid(self):
        # If seller makes a bid on his own auction, bid should not be saved

        bid = 50.50
        # Login as user1 (seller)
        loggedIn = self.client.login(username=self.user1, password=self.user1)
        self.assertTrue(loggedIn)

        auction = Auction.getActiveById(1)
        self.assertEqual(self.client.session['_auth_user_id'], auction.seller.id)

        bids = auction.getBidHistory().count()
        self.client.post(self.bidUrl, {"bid": bid, "updated": timezone.now().date()})

        self.assertEqual(auction.getBidHistory().count(), bids)
        self.client.logout()

    def testCorrectBid(self):
        # Bid should be saved

        bid = 50.50
        # Login as user2
        loggedIn = self.client.login(username=self.user2, password=self.user2)
        self.assertTrue(loggedIn)

        auction = Auction.getActiveById(1)
        self.assertNotEqual(self.client.session['_auth_user_id'], auction.seller.id)
        bids = auction.getBidHistory().count()

        self.client.post(self.bidUrl, {"bid": bid, "updated": timezone.now().date()})

        self.assertEqual(auction.getBidHistory().count(), bids+1)
        self.client.logout()