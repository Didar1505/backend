from django.db import models
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from userauths.models import User, Profile
from moviepy.editor import VideoFileClip

LANGUAGE = (
    ('English', 'English'),
    ('Russian', 'Russian'),
    ('Turkmen', 'Turkmen')
)

LEVEL = (
    ('Başlangyç', 'Başlangyç'),
    ('Orta', 'Orta'),
    ('Ýokary dereje', 'Ýokary dereje')
)

RATING = (
    (1, '1 Star'),
    (2, '2 Star'),
    (3, '3 Star'),
    (4, '4 Star'),
    (5, '5 Star')
)

TEACHER_STATUS = (
    ('Draft', 'Draft'),
    ('Disabled', 'Disabled'),
    ('Published', 'Published')
)

PLATFORM_STATUS = (
    ('Review', 'Review'),
    ('Draft', 'Draft'),
    ('Disabled', 'Disabled'),
    ('Published', 'Published'),
    ('Rejected', 'Rejected')
)

PAYMENT_STATUS = (
    ('Paid', 'Paid'),
    ('Processing', 'Processing'),
    ('Failed', 'Failed')
)

COURSE_TYPE = (
    ('Online', 'Online'),
    ('In-person', 'In-person')
)

NOTIFICATION_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
    ("New Course Question", "New Course Question"),
    ("Course Published", "Course Published"),
    ("Draft", "Draft"),
    ("Course Enrollment Completed", "Course Enrollment Completed"),
)

STATUS = (
    ("Open", "Open"),
    ("Closed", "Closed")
)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='course-file', blank=True, null=True, default="default.jpg")
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    imo = models.IntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self) -> str:
        return self.full_name

    def students(self):
        return CartOrderItem.objects.filter(teacher=self)

    def courses(self):
        return Course.objects.filter(teacher=self)

    def review(self):
        return Course.objects.filter(teacher=self).count()

class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to='course-file', default='category.jpg', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'
    
    def course_count(self):
        return Course.objects.filter(category=self).count()
    
    def save(self, *args, **kwargs):
        # Generate the slug only if it's not already set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Call the parent save method

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    type = models.CharField(choices=COURSE_TYPE, max_length=100, default='Online', null=True, blank=True)
    file = models.FileField(upload_to='course-file', null=True, blank=True)
    image = models.FileField(upload_to='course-file', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    language = models.CharField(choices=LANGUAGE, max_length=100, default='English')
    level = models.CharField(choices=LEVEL, max_length=100, default='Başlangyç')
    platform_status = models.CharField(choices=PLATFORM_STATUS, max_length=100, default='Published')
    teacher_course_status = models.CharField(choices=TEACHER_STATUS, max_length=100, default='Published')
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if self.type == 'Online': 
            self.price = 0.00
        # Generate the slug only if it's not already set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Call the parent save method

    def students(self):
        return EnrolledCourse.objects.filter(course=self)
    
    def curriculum(self):
        return Variant.objects.filter(course=self)
    
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)
    
    def average_rating(self):
        avarage_rating = Review.objects.filter(course=self, active=True).aggregate(avg_rating=models.Avg('rating'))
        return avarage_rating['avg_rating']

    def rating_count(self):
        return Review.objects.filter(course=self, active=True).count()

    def reviews(self):
        return Review.objects.filter(course=self, active=True)
    
class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    variant_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title

    def variant_items(self):
        return VariantItem.objects.filter(variant=self)

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='course-file', null=True, blank=True)
    duration = models.DurationField(blank=True, null=True)
    content_duration = models.CharField(max_length=1000, null=True, blank=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.variant.title} - {self.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file:
            clip = VideoFileClip(self.file.path)
            duration_seconds = clip.duration

            minutes, remainder = divmod(duration_seconds, 60)
            minutes = round(minutes)
            seconds = round(remainder)
            duration_text = f'{minutes}m {seconds}s'
            self.content_duration = duration_text
            # saves only the updated file in this model
            super().save(update_fields=['content_duration'])

class Question_Answer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        ordering = ['-date']

    def messages(self):
        return Question_Answer_Message.objects.filter(question=self)
    
    def profile(self):
        return Profile.objects.get(user=self.user)

class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    qam_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        ordering = ['date']

    def profile(self):
        return Profile.objects.get(user=self.user)
    
class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    country = models.CharField(max_length=100, null=True, blank=True)
    cart_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.course.title} - {self.user.username}"

class CartOrder(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default='Processing')
    full_name= models.CharField(max_length=100, null=True, blank=True)
    email= models.CharField(max_length=100, null=True, blank=True)
    country= models.CharField(max_length=100, null=True, blank=True )
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def order_items(self):
        return CartOrderItem.objects.filter(order=self)

    def __str__(self) -> str:
        return f"{self.student.username} - {self.oid}"
    
class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name='orderitem')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='order_item')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def order_id(self):
        return f'order ID #{self.order.oid}'

    def paymend_status(self) -> str:
        return f"{self.order.payment_status}"
    
    def __str__(self) -> str:
        return f"{self.course.title} - {self.order.student.username} - {self.oid}"
    
class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    certificate_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.course.title

class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.variant_item.title} - {self.course.title}'

class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    # order_item = models.ForeignKey(CartOrderItem, on_delete=models.CASCADE)
    enrollment_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return f"{self.user.full_name} - {self.course.title}"
    
    def lectures(self):
        return VariantItem.objects.filter(variant__course = self.course)
    
    def completed_lessons(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)

    def curriculum(self):
        return Variant.objects.filter(course=self.course)

    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)

    def question_answer(self):
        return Question_Answer.objects.filter(course=self.course, user=self.user)

    def review(self):
        return Review.objects.filter(course=self.course, user=self.user).first()
    
class Note(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    note = models.TextField(null=True,blank=True)
    note_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet='1234567890')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title}"

    def profile(self):
        return Profile.objects.get(user=self.user)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.type

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.course.title
    

class ForumCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Forum-Categories'
    
    def save(self, *args, **kwargs):
        # Generate the slug only if it's not already set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Call the parent save method


class Thread(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=STATUS, max_length=100, default='Open' )
    category = models.ForeignKey(ForumCategory, related_name='threads', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='threads', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def profile(self):
        return Profile.objects.get(user=self.user)
    
    def posts(self):
        return Post.objects.filter(thread=self)

    def num_posts(self):
        return Post.objects.filter(thread=self).count()
    
    def save(self, *args, **kwargs):
        # Generate the slug only if it's not already set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Call the parent save method

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    message = models.TextField()
    answer = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post by {self.user.username}"
    
    def profile(self):
        return Profile.objects.get(user=self.user)