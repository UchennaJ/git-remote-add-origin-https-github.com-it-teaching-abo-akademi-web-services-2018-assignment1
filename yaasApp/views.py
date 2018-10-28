from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import authenticate, logout, login
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta
from django.utils import timezone

from django.utils import translation
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.contrib import auth
from yaasApp.models import *
from yaasApp.forms import *
from fixtures.data_generation import *


LANGUAGE_SESSION_KEY = 'language'

# Create your views here.

def home(request):
    template = "home.html"
    context = {"auctions": Auction.getActive()}

    return render(request, template, context)


def search(request):
    if request.method == "POST" and "criteria" in request.POST:
        criteria = request.POST["criteria"]
        template = "home.html"
        context = {"auctions": Auction.findActive(criteria)}

        return render(request, template, context)
    else:
        return HttpResponseRedirect("/YAAS/")


class LoginUser(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', '/YAAS/')
        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request,user)
            print(user.password)
            return HttpResponseRedirect(nextTo)
        else:
            messages.add_message(request, messages.ERROR, "Invalid username or password")
            return HttpResponseRedirect('/YAAS/login/')


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect('/YAAS/')


@login_required
def create_auction(request):
    if request.method == "POST":
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            template = "confirmation.html"
            context = {"form": ConfirmationForm(), "auctionform": form}
            # Valid auction form, redirect to confirmation page
            return render(request, template, context)
    else:
        form = CreateAuctionForm()
    template = "create_auction.html"
    context = {"form": form}
    return render(request, template, context)


def confirmation(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        # Confirmation was 'Yes', save auction, send email and redirect to front page.
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            auction = Auction()
            auction.title = form.cleaned_data["title"]
            auction.seller = request.user
            auction.description = form.cleaned_data["description"]
            auction.end_date = form.cleaned_data["end_date"]
            auction.minimum_price = form.cleaned_data["minimum_price"]
            auction.save()
            message = "This is a confirmation message that the following auction has been created: \n\n"
            message += auction.information()
            send_mail("Auction created", message, "noreply@YAAS.com", [auction.seller.email], fail_silently=False)
            return HttpResponseRedirect('/YAAS/')

    template = "message.html"
    context = {"message": _("Auction was not created")}
    # Auction was not created
    return render(request, template, context)


def view_auction(request, id):
    auction = Auction.getActiveById(id)
    if auction:
        template = "view_auction.html"
        context = {"auction": auction, "bid_history": auction.getBidHistory(),
                   "bid_form": BidForm(initial={"updated": auction.updated_date})}
        return render(request, template, context)
    else:
        template = "message.html"
        context = {"message": _("Auction not found")}
        return render(request, template, context)


@login_required
def edit_auction(request, id):
    auction = Auction.getActiveById(id)
    if auction:
        if request.user.id != auction.seller.id:
            template = "message.html"
            context = {"message": _("Only the seller of an auction can edit it!")}
            # Error: Logged in user is not the same as the seller!
            return render(request, template, context)
        else:
            if request.method == "POST":
                form = EditAuctionForm(request.POST)
                if form.is_valid():
                    auction.description = form.cleaned_data["description"]
                    auction.save()
                    # If logged in user is the same as the seller and request is POST, save edits
                    return HttpResponseRedirect("/YAAS/auction/" + str(auction.id) + "/")
            else:
                form = EditAuctionForm({"description": auction.description})
            template = "edit_auction.html"
            context = {"form": form, "auction": auction}
            # If logged in user is the same as the seller and request is not POST, view edit form
            return render(request, template, context)
    else:
        template = "message.html"
        context = {"message": _("Auction not found")}
        # Error: Auction not found!
        return render(request, template, context)


# Baning an Auction
@login_required
def ban_auction(request, id):
    auction = Auction.getActiveById(id)
    template = "message.html"
    if auction:
        if request.user.is_superuser:
            auction.banned = True
            auction.save()

            # Auction banned, send email to seller and bidders
            receivers = [auction.seller.email, ]
            bidders = auction.getBidders()
            for b in bidders:
                receivers.append(b.email)
            message = "The following auction has been banned: \n\n"
            message += auction.information()
            send_mail("Auction banned", message, "noreply@YAAS.com", receivers, fail_silently=False)

            context = {"message": _("Auction number ") + str(auction.id) + _(" was banned!")}
            return render(request, template, context)
        else:
            context = {"message": _("You must be an admin to ban auction!")}
            # Error: Logged in user is not an admin!
            return render(request, template, context)
    else:
        context = {"message": _("Auction not found")}
        # Error: Auction not found!
        return render(request, template, context)


@login_required
def bid_auction(request, id):
    auction = Auction.getActiveById(id)
    if auction:
        latest_bid = Bid.getLatestBidForAuction(auction)
        if request.user.id == auction.seller.id:
            template = "message.html"
            context = {"message": _("You can't bid on your own auctions!")}
            # Error: Seller tried to bid on own auction
            return render(request, template, context)
        elif latest_bid and request.user.id == latest_bid.bidder.id:
            template = "message.html"
            context = {"message": _("You can't bid on an auction that you are already winning!")}
            # Error: Winning bidder tried to bid again
            return render(request, template, context)
        elif auction.end_date <= timezone.now():
            template = "message.html"
            context = {"message": _("Auction has ended, bid not accepted!")}
            # Error: Auction expired
            return render(request, template, context)
        else:
            if request.method == "POST":
                form = BidForm(request.POST)
                if (form.is_valid() and form.cleaned_data["bid"] > auction.minimum_price
                        and form.cleaned_data["bid"] > auction.getLatestBid()):
                    if form.cleaned_data['updated'] < auction.updated_date:
                        template = "message.html"
                        context = {"message": _("Auction has changed since page was loaded, bid was not accepted.")}
                        # Error: auction has been updated, bid was not accepted.
                        return render(request, template, context)
                    else:
                        # Create a bid
                        bid = Bid()
                        bid.bid = form.cleaned_data["bid"]
                        bid.auction = auction
                        bid.bidder = request.user
                        bid.save()

                        # Soft deadlines, A bid made within 5 minutes of deadline
                        # automatically extends the deadline with 5 minutes.
                        if (auction.end_date - timezone.now()).seconds < 5*60:
                            auction.end_date += timedelta(minutes=5)
                            auction.save()

                        # Notify bidder, last bidder and seller by email
                        receivers = [request.user.email, auction.seller.email]
                        if latest_bid:
                            receivers.append(latest_bid.bidder.email)
                        message = request.user.get_full_name() + " made a bid on the following auction: \n\n"
                        message += auction.information()
                        message += "\n\nThe new bid is " + str(bid.bid)
                        send_mail("New bid on auction", message, "noreply@YAAS.com", receivers, fail_silently=False)

                        return HttpResponseRedirect("/YAAS/auction/" + str(auction.id) + "/")
            else:
                form = BidForm(initial={"updated": auction.updated_date})
            template = "view_auction.html"
            context = {"auction": auction, "bid_history": auction.getBidHistory(), "bid_form": form}
            return render(request, template, context)
    else:
        template = "message.html"
        context = {"message": _("Auction not found")}
        # Error: Auction not found!
        return render(request, template, context)


def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user and show message
            form.save()
            template = "message.html"
            context = {"message": _("User successfully created, please login.")}
            return render(request, template, context)
    else:
        # Empty user form
        form = UserRegistrationForm()
    template = "register_user.html"
    context = {"form": form}
    return render(request, template, context)


@login_required
def edit_user(request):
    user = request.user
    if request.method == "POST":
        form = EditUserForm(request.POST)
        if form.is_valid():
            # Save user and show message
            user.email = form.cleaned_data["email"]
            user.set_password(form.cleaned_data["password"])
            user.save()
            template = "message.html"
            context = {"message": _("User info successfully updated.")}
            return render(request, template, context)
    else:
        form = EditUserForm(initial={"email": user.email})
    template = "edit_user.html"
    context = {"user": user, "form": form}
    return render(request, template, context)


# def change_language(request, next="/YAAS/"):
#     if request.method == "POST" and "language" in request.POST:
#         # Changing language
#         lan = request.POST['language']
#         if request.user.is_authenticated():
#             # Save user language
#             user_lang = request.user.language
#             user_lang.language = lan
#             user_lang.save()
#     else:
#         if request.user.is_authenticated():
#             # Loading user language
#             lan = request.user.language.language
#         else:
#             # Default language is english
#             lan = "en"
#
#     request.session[translation.LANGUAGE_SESSION_KEY] = lan
#     messages.add_message(request, messages.INFO, "Language Changed to " + lan)
#     return HttpResponseRedirect(next)


#from myblog
def change_language(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    messages.add_message(request, messages.INFO, "Language Changed to " + lang_code)
    return HttpResponseRedirect('/YAAS/')

@login_required
def email_view(request):
    body = "email body"
    from_email = 'noreply@yaas.com'
    to_email = 'customer@yaas.com'
    send_mail('Test Email Subject', body, from_email, [to_email,], fail_silently=False)
    return HttpResponse('Email sent')


def generatedata(request):
    Populate().doPopulate()
    return HttpResponseRedirect("/YAAS/")