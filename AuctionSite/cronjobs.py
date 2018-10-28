from django_cron import CronJobBase, Schedule
from django.core.mail import send_mail
from yaasApp.models import *
from django.utils import timezone


class ResolveAuctions(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'YAAS.ResolveAuctions'    # a unique code

    def do(self):
        print("Resolving auctions")
        auctions = Auction.objects.filter(end_date__lte=timezone.now())
        for a in auctions:
            if a.banned:
                # Banned auctions are not resolved
                pass
            else:
                winning_bid = Bid.getLatestBidForAuction(a)
                if winning_bid:
                    a.winner = winning_bid.bidder
                a.active = False
                a.save()

                # Auction resolved, send email to seller and bidders (including winner)
                receivers = [a.seller.email, ]
                bidders = a.getBidders()
                for b in bidders:
                    receivers.append(b.email)
                message = "The following auction has ended: \n\n"
                message += a.information()
                if winning_bid:
                    message += "\n\nThe winner was " + winning_bid.bidder.get_full_name()
                else:
                    message += "\n\nThere was no bidders."
                send_mail("Auction ended", message, "noreply@YAAS.com", receivers, fail_silently=False)

                print("Auction " + str(a.id) + " was resolved!")
