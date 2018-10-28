from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from yaasApp.models import *
from yaasApp.serializers import *
from django.utils import timezone


@api_view(['GET'])
def api_list_auctions(request, format=None):
    # List all auctions

    if request.method == 'GET':
        auctions = Auction.getActive()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_search_auctions(request, criteria, format=None):
    # List all auctions that match the search criteria

    if request.method == 'GET':
        auctions = Auction.findActive(criteria)
        if auctions:
            serializer = AuctionSerializer(auctions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_auction(request, id, format=None):
    # List all auctions that match the search criteria
    if request.method == 'GET':
        auction = Auction.getActiveById(id)
        if auction:
            serializer = AuctionSerializer(auction, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticatedOrReadOnly,))
def api_bid(request, id, format=None):
    # Make a bid on an auction

    auction = Auction.getActiveById(id)
    if auction:
        latest_bid = Bid.getLatestBidForAuction(auction)
        if request.user.id == auction.seller.id:
            error = {"Error": "You can't bid on your own auctions!"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif latest_bid and request.user.id == latest_bid.bidder.id:
            error = {"Error": "You can't bid on an auction that you are already winning!"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif auction.end_date <= timezone.now():
            error = {"Error": "Sorry, bid not accepted Auction has ended!"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            serializer = MakeBidSerializer(data=request.DATA)
            if serializer.is_valid():
                bid_made = serializer.data.get("bid", -1)
                if bid_made > auction.getLatestBid():
                    bid = Bid()
                    bid.bid = bid_made
                    bid.bidder = request.user
                    bid.auction = auction
                    bid.save()
                    serializer = BidSerializer(bid, many=False)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    error = {"Error": "Amount is low!"}
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Bad request
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        # Auction not found
        return Response(status=status.HTTP_404_NOT_FOUND)