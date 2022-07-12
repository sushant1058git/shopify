from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect,get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import RegistrationForm,UserProfile,UserForm,UserProfileForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from cart.views import _get_cart_id
from cart.models import Cart,CartItem
import requests
from django.views.decorators.csrf import csrf_exempt
from orders.models import OrderProduct,Order

@login_required(login_url='login')
def dashboard(request):
    context={}
    # import pdb;pdb.set_trace()
    orders = OrderProduct.objects.filter(user=request.user, ordered=True)[::-1]
    
    # order_number_list=[]
    # for i in orders:
    #     order_number_list.append(i.order.order_number)
    # first=order_number_list[0]
    # ordId=Order.objects.get(order_number=first).id
    
    # product=OrderProduct.objects.filter(order_id=ordId)
    # for i in product:
    #     print(i.product.product_name)
    
    context['orders']=orders
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
def account(request):
    print(request.path)
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    profile=UserProfile.objects.get(user=request.user)
    context={
        'orders_count':orders.count(),
        'user':request.user,
        'profile':profile
    }
    return render(request,'accounts/account.html',context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username, password=password)
            user.phone_number = phone_number
            user.save()
            
            
            #Creating user profile
            profile=UserProfile()
            profile.user_id=user.id
            profile.profile_picture='default/default_pic.png'
            profile.save()

            # User Activaton

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Please activate your account by clicking on the link that we have sent to your email !! ')
            return redirect('/accounts/login/?command=verification&email=' + email)

    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save() 

            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are Logged in !!')
            # redirecting user to checkout page after login starts here
            #install requests package
            url=request.META.get('HTTP_REFERER')#It will grab previous url
            try:
                query=requests.utils.urlparse(url).query
                print(query) #next=/cart/checkout/
                params=dict(x.split('=') for x in query.split('&')) #-->{'next': '/cart/checkout/'} returned a dict with key 'next'
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)
            except:
                return redirect('store')

            # redirecting user to checkout page after login ends here
        else:
            messages.error(request, 'Invalid Credentials !!')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out !!!')
    return redirect(login)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations!! your account has been activated. Login now')
        return redirect(login)
    else:
        messages.error(request, 'Invalid link')
        return redirect(register)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Please reset  your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset link has been sent')
            return redirect(login)
        else:
            messages.error(request, 'User not registered ')
            return redirect(forgotPassword)

    return render(request, 'accounts/forgotPassword.html')


def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect(resetPassword)
    else:
        messages.error(request, 'This link has expired')
        return redirect(login)


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect(login)
    else:
       return render(request, 'accounts/resetPassword.html')

