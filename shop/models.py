from django.db import models
from django.contrib.auth.models import User

# ===================== FLOWER =====================
class Flower(models.Model):
    CATEGORY_CHOICES = [
        ('flower', 'Flower'),
        ('wedding', 'Wedding'),
        ('workshop', 'Workshop'),
        ('shopplant', 'Shop Plant'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


# ===================== CART =====================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'flower')

    def total_price(self):
        return self.flower.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.flower.name}"

# ===================== ORDER =====================
class Order(models.Model):
    ORDER_CHOICES = [
        ('Pickup', 'Pickup'),
        ('Delivery', 'Delivery'),
        ('Buy Now', 'Buy Now'),
    ]

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    address = models.CharField(max_length=300, blank=True, null=True)
    order_type = models.CharField(max_length=20, choices=ORDER_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.flower.price

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


# ===================== PROFILE =====================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


# ===================== REFUND =====================
class Refund(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    issue_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    photo = models.ImageField(upload_to='refunds/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund #{self.id} - {self.name} ({self.status})"
