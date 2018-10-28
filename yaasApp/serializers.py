from rest_framework import serializers
from yaasApp.models import *


# Model serializer class for auction bid view
class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'title', 'description', 'seller', 'start_date',
                  'updated_date', 'end_date', 'minimum_price', 'active', 'banned')


class MakeBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('bid',)


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('id', 'auction', 'bid', 'bidder', 'timestamp')