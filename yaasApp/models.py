from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext as _

#from djmoney.money import Money
#from djmoney.contrib.exchange.models import convert_money


#Creating Models
class Auction(models.Model):
    title = models.CharField(_("Title"), max_length=30)
    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(User, related_name='seller', on_delete=models.PROTECT)
    description = models.TextField(_("Description"), )
    start_date = models.DateTimeField(_("Start date"), auto_now_add=True)
    updated_date = models.DateTimeField(_("Updated date"), auto_now=True)
    end_date = models.DateTimeField(_("End date"), )
    minimum_price = models.DecimalField(_("Minimum price"), max_digits=10, decimal_places=2)
    active = models.BooleanField(_("Active"), default=True)
    banned = models.BooleanField(_("Banned"), default=False)
    winner = models.ForeignKey(User, related_name='winner', null=True, blank=True, on_delete=models.PROTECT)

    @classmethod
    def getActiveById(cls, auction_id):
        try:
            a = cls.objects.get(id=auction_id)
        except ObjectDoesNotExist:
            a = None
        if a and a.active and not a.banned:
            return a
        else:
            return None

    @classmethod
    def getActive(cls):
        return cls.objects.filter(Q(active=True) & Q(banned=False))

    @classmethod
    def findActive(cls, criteria):
        return cls.objects.filter((Q(title__contains=criteria) | Q(description__contains=criteria))
                                  & (Q(active=True) & Q(banned=False)))

    def getBidHistory(self):
        bids = Bid.getBidsForAuction(self)
        return bids

    def getLatestBid(self):
        bid = Bid.getLatestBidForAuction(self)
        if bid:
            return bid.bid
        else:
            return 0.00

    def getBidders(self):
        bids = self.getBidHistory()
        bidders = []
        for b in bids:
            if b.bidder not in bidders:
                bidders.append(b.bidder)

        return bidders

    def information(self):
        info = "ID: " + str(self.id) + "\n"
        info += "Title: " + self.title + "\n"
        info += "Description: " + self.description + "\n"
        info += "Started: " + str(self.start_date.date()) + "\n"
        info += "Updated: " + str(self.updated_date.date()) + "\n"
        info += "Ends: " + str(self.end_date.date()) + "\n"
        info += "Minimum price: " + str(self.minimum_price) + "\n"

        return info


class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    auction = models.ForeignKey(Auction, on_delete=models.PROTECT)
    bidder = models.ForeignKey(User, on_delete=models.PROTECT)
    bid = models.DecimalField(_("Bid"), max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)

    @classmethod
    def getBidsForAuction(cls, auction):
        bids = cls.objects.filter(auction=auction).order_by("-timestamp")
        return bids

    @classmethod
    def getLatestBidForAuction(cls, auction):
        try:
            bid = cls.objects.filter(auction=auction).latest("timestamp")
        except ObjectDoesNotExist:
            bid = None
        return bid


class UserLanguage(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    language = models.CharField(max_length=10, default="en")


User.language = property(lambda u: UserLanguage.objects.get_or_create(user=u)[0])

