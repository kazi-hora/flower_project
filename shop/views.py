from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RefundForm
from .models import Refund
from .models import Flower, Order, Profile, Cart
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

# shop/views.py

from .models import Order

def place_order(request):
    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        order_type = request.POST.get('order_type')
        payment_method = request.POST.get('payment_method')
        flower_id = request.POST.get('flower_id')
        quantity = request.POST.get('quantity')

        flower = Flower.objects.get(id=flower_id)

        Order.objects.create(
            user=request.user,   # 🔥 यही लाइन IMPORTANT
            customer_name=customer_name,
            phone=phone,
            email=email,
            address=address,
            order_type=order_type,
            payment_method=payment_method,
            flower=flower,
            quantity=quantity,
        )

        return redirect('order_success')

# ===================== LOGIN =====================

def login_view(request):

    attempts = request.session.get("login_attempts", 0)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session["login_attempts"] = 0
            return redirect("home")

        else:
            attempts += 1
            request.session["login_attempts"] = attempts
            messages.error(request, "Invalid username or password")

    return render(request, "shop/login.html", {"attempts": attempts})

# ===================== LOGOUT =====================
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out 👋")
    return redirect("login")

# ===================== HOME =====================
@login_required(login_url="login")
def home(request):
    return render(request, "shop/home.html")


# ===================== PRODUCTS =====================
@login_required(login_url="login")
def flowers(request):
    flowers = Flower.objects.filter(category="flower")
    return render(request, "shop/flowers.html", {"flowers": flowers})


@login_required(login_url="login")
def shopplants(request):
    flowers = Flower.objects.filter(category="shopplant")
    return render(request, "shop/shopplants.html", {"flowers": flowers})


@login_required(login_url="login")
def weddings(request):
    flowers = Flower.objects.filter(category="wedding")
    return render(request, "shop/weddings.html", {"flowers": flowers})


@login_required(login_url="login")
def workshop(request):
    flowers = Flower.objects.filter(category="workshop")
    return render(request, "shop/workshop.html", {"flowers": flowers})

@login_required
def map(request):
    return render(request, "shop/map.html")

@login_required(login_url="login")
def about(request):
    return render(request, "shop/about.html")

def returns_view(request):
    return render(request, 'shop/returns.html')
@login_required
def contact(request):

    # GET request → page load हुँदा orders देखिन आवश्यक
    orders = Order.objects.filter(user=request.user).order_by("-id")
    total_orders = orders.count()

    if request.method == "POST":
        Refund.objects.create(
            user=request.user,
            order_id=request.POST.get("order_id"),   # Added order ID
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            issue_type=request.POST.get("issue_type"),
            description=request.POST.get("description"),
            photo=request.FILES.get("photo"),
        )

        messages.success(
            request,
            "Your support / refund request has been sent successfully ✅"
        )
        return redirect("contact")

    return render(request, "shop/contact.html", {
        "orders": orders,
        "total_orders": total_orders,
    })
# ===================== REGISTER =====================
def register(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.save()

        Profile.objects.create(
            user=user,
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "shop/register.html")


# ===================== CART SYSTEM =====================
@login_required(login_url="login")
def add_to_cart(request, product_id):
    flower = get_object_or_404(Flower, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        flower=flower
    )

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()
    return redirect("cart")


@login_required(login_url="login")
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required(login_url="login")
def remove_from_cart(request, product_id):
    Cart.objects.filter(
        user=request.user,
        flower_id=product_id
    ).delete()

    return redirect("cart")


# ===================== CHECKOUT =====================
@login_required(login_url="login")
def checkout(request):

    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")

        # ❌ nothing selected
        if not selected_items:
            messages.warning(request, "Please select at least one item to checkout.")
            return redirect("cart")

        # ✅ save selected ids in session
        request.session["selected_cart_items"] = selected_items

        return redirect("payment")

    # safety fallback
    return redirect("cart")

# ===================== BUY NOW =====================
@login_required(login_url="login")
def buy_now(request, flower_id):
    Cart.objects.filter(user=request.user).delete()
    Cart.objects.create(user=request.user, flower_id=flower_id, quantity=1)
    return redirect("checkout")   # 🔥 FIXED FLOW


# ===================== PAYMENT =====================
@login_required(login_url="login")
def payment(request):

    selected_ids = request.session.get("selected_cart_items")

    if not selected_ids:
        messages.warning(request, "Please select items first.")
        return redirect("cart")

    cart_items = Cart.objects.filter(
        user=request.user,
        id__in=selected_ids
    )

    if not cart_items.exists():
        messages.warning(request, "Selected items not found.")
        return redirect("cart")

    total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        order_type = request.POST.get("order_type")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        orders = []

        # ✅ save only selected items
        for item in cart_items:
            order = Order.objects.create(
                user=request.user,
                flower=item.flower,
                quantity=item.quantity,
                customer_name=name,
                phone=phone,
                email=email,
                address=address,
                order_type=order_type,
                payment_method=payment_method,
            )
            orders.append(order)

        # ✅ delete only paid items
        cart_items.delete()

        # ✅ store last order ids for success page
        request.session["last_orders"] = [o.id for o in orders]

        # ✅ clear selected cart session
        del request.session["selected_cart_items"]

        return redirect("payment_success")

    return render(request, "shop/payment.html", {
        "cart_items": cart_items,
        "total": total
    })

@login_required(login_url="login")
def payment_success(request):
    order_ids = request.session.get("last_orders", [])
    orders = Order.objects.filter(id__in=order_ids)

    return render(request, "shop/payment_success.html", {
        "orders": orders
    })

# ===================== ORDERS =====================
@login_required(login_url="login")
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request, "shop/orders.html", {"orders": orders})

def contact_refund(request):
    if request.method == 'POST':
        form = RefundForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'shop/contact.html', {
                'form': RefundForm(),
                'success': True
            })
    else:
        form = RefundForm()

    return render(request, 'shop/contact.html', {'form': form})
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == "Pending":
        order.status = "Cancelled"
        order.save()
    return redirect('my_orders')


@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == "Delivered":
        order.status = "Return Requested"
        order.save()
    return redirect('my_orders')

@login_required
def refund_request(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_orders = orders.count()

    if request.method == "POST":

        order_id = request.POST.get('order_id')
        name = request.POST.get("name")
        email = request.POST.get("email")
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')

        if not order_id or not issue_type or not description:
            messages.error(request, "All fields except photo are required.")
            return redirect('refund_request')

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if Refund.objects.filter(order=order).exists():
            messages.error(request, "Refund already requested for this order.")
            return redirect('refund_request')

        if timezone.now() > order.created_at + timedelta(hours=24):
            messages.error(request, "Refund allowed only within 24 hours of delivery.")
            return redirect('refund_request')

        # FIXED 🔥 Now saving name + email also
        Refund.objects.create(
            user=request.user,
            order=order,
            name=name,
            email=email,
            issue_type=issue_type,
            description=description,
            photo=photo
        )

        messages.success(request, "Refund request submitted successfully.")
        return redirect('refund_request')

    return render(request, 'shop/contact.html', {
        'orders': orders,
        'total_orders': total_orders
    })
