from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from accounts.models import Account
from core.models import Transaction, Notification

# The money transfer logic

@login_required
def search_users_account_number(request):
    # account = Account.objects.filter(account_status="active")
    account = Account.objects.all()  # You can search through all available account or specify the active accounts only
    query = request.POST.get("account_number") # 217703423324

    if query:
        account = account.filter(
            Q(account_number=query)|
            Q(account_id=query)
        ).distinct()
    

    context = {
        "account": account,
        "query": query,
    }
    return render(request, "transfer/search-user-by-account-number.html", context)

# The Amount to Tansfer
def AmountTransfer(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)  # Get the account informationm of the corresponding accoiunt number
    except:
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")
    context = {
        "account": account,
    }
    return render(request, "transfer/amount-transfer.html", context)

#  Create new TRANSACTION entry for the new transaction about to happen
def AmountTransferProcess(request, account_number):
    account = Account.objects.get(account_number=account_number) ## Get the account that the money would be sent to - [RECEIVER ACCOUNT]
    sender = request.user # get the person that is logged in [SENDER USER]
    reciever = account.user ## get the user info of the  person that is going to reciver the money [RECEIVER USER]

    sender_account = request.user.account ## get the currently logged in users account that vould send the money [SENDER ACCOUNT]
    reciever_account = account # get the the person account that vould send the money [RECEIVER ACCOUNT]

    if request.method == "POST":
        amount = request.POST.get("amount-send")
        description = request.POST.get("description")
        if sender_account.account_balance >= Decimal(amount):
            new_transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                description=description,
                reciever=reciever,
                sender=sender,
                sender_account=sender_account,
                reciever_account=reciever_account,
                status="processing",
                transaction_type="transfer"
            )
            new_transaction.save()
            
            # Get the ID of the transaction that was created now
            transaction_id = new_transaction.transaction_id
            return redirect("core:transfer-confirmation", account.account_number, transaction_id)
        else:
            messages.warning(request, "Insufficient Fund.")
            return redirect("core:amount-transfer", account.account_number)
    else:
        messages.warning(request, "Error Occured, Try again later.")
        return redirect("account:account")

# Get the Account Number and Transaction id 
def TransferConfirmation(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transaction does not exist.")
        return redirect("account:account")
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "transfer/transfer-confirmation.html", context)

# Move the amount : Deduct amount from sender and add to receiver
def TransferProcess(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user 
    reciever = account.user

    sender_account = request.user.account 
    reciever_account = account

    completed = False

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        # Confirm the PIN NUMBER is correct 
        if pin_number == sender_account.pin_number:
            transaction.status = "completed"
            transaction.save()

            # Remove amount from sender's account and update the account
            sender_account.account_balance -= transaction.amount
            sender_account.save()

            # Add the amount that was removed from semder's account to the receiver's account and update the account
            account.account_balance += transaction.amount
            account.save()
            
            # Create Notification Object
            Notification.objects.create(
                amount=transaction.amount,
                user=account.user,
                notification_type="Credit Alert"
            )
            
            Notification.objects.create(
                user=sender,
                notification_type="Debit Alert",
                amount=transaction.amount
            )

            messages.success(request, "Transfer Successfull.")
            return redirect("core:transfer-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "Incorrect Pin.")
            return redirect('core:transfer-confirmation', account.account_number, transaction.transaction_id)
    else:
        messages.warning(request, "An error occured, Try again later.")
        return redirect('account:account')
    

# Get te
def TransferCompleted(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transfer does not exist.")
        return redirect("account:account")
    context = {
        "account":account,
        "transaction":transaction
    }
    return render(request, "transfer/transfer-completed.html", context)
