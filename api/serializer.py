from rest_framework import serializers
from userauths.models import User, Profile
from api import models as api_models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        type = api_models.Teacher.objects.filter(user=self.user).first()

        data.pop('refresh', None)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['id'] = self.user.id
        data['type'] = 'teacher' if type else "student"

        return data

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password', 'password2']
        extra_kwargs = {'full_name': {'required': False}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            full_name=validated_data.get('full_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email',]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Profile
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id',"title","course_count", "image", "slug","active",]
        model = api_models.Category

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id',"user","image","full_name","bio","facebook","instagram","imo","about","country"]
        model = api_models.Teacher

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["user","image","full_name","bio","facebook","instagram","imo","about","country","students","courses","review"]
        model = api_models.Teacher

class VariantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.VariantItem
        fields = ['id','title', 'description', 'file', 'duration', 'content_duration', 'preview', 'variant_item_id', 'date']

class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True, read_only=True)

    class Meta:
        model = api_models.Variant
        fields = ['course', 'title', 'variant_id', 'date', 'variant_items']


class Question_Answer_MessageSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer_Message

class Question_AnswerSerializer(serializers.ModelSerializer):
    messages = Question_Answer_MessageSerializer(many=True)
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer



class CartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = api_models.CartOrderItem

class CartOrderSerializer(serializers.ModelSerializer):
    order_items=CartOrderItemSerializer(many=True)
    
    class Meta:
        fields = '__all__'
        model = api_models.CartOrder

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = api_models.Certificate

class CompletedLessonSerializer(serializers.ModelSerializer):
    variant_item = VariantItemSerializer(many=False)
    class Meta:
        fields = '__all__'
        model = api_models.CompletedLesson

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = api_models.Note

class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)
    course = serializers.SerializerMethodField()
    class Meta:
        model = api_models.Review
        fields = "__all__"

    def get_course(self, obj):
        course = obj.course
        return course.title



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = api_models.Notification

class WishlistSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class Meta:
        fields = ['user', 'course']
        model = api_models.Wishlist

    def get_course(self, obj):
        course = obj.course
        return {
            "course_id": course.course_id,
            'title': course.title,
            'image': f"http://127.0.0.1:8000/{course.image.url}",
            'teacher': course.teacher.full_name,
            'price': course.price,
            'slug': course.slug
        }

class EnrolledCourseSerializer(serializers.ModelSerializer):
    lectures = VariantItemSerializer(many=True, read_only=True)
    completed_lessons =CompletedLessonSerializer(many=True, read_only=True)
    curriculum = VariantSerializer(many=True, read_only=True)
    note = NoteSerializer(many=True, read_only=True)
    question_answer = Question_AnswerSerializer(many=True, read_only=True)
    review = ReviewSerializer(many=False, read_only=True)
    user = serializers.SerializerMethodField()
    
    class Meta:
        fields = '__all__'
        model = api_models.EnrolledCourse

    def __init__(self, *args, **kwargs):
        super(EnrolledCourseSerializer, self).__init__(*args, **kwargs)
        request  = self.context.get('request')
        if request and request.method =="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth=1

    def get_user(self, obj):
        user = obj.user
        return {
            "username": user.username,
            "full_name": user.full_name
        }

class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True, read_only=True, required=False)
    curriculum = VariantSerializer(many=True, read_only=True, required=False)
    lectures = VariantItemSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, read_only=True, required=False)

    class Meta:
        fields = ["category","teacher","type","file","image","title","description","price","language","level","platform_status","teacher_course_status","featured","course_id","slug","date","students","curriculum","average_rating","rating_count","reviews", "lectures"] 
        # fields = ['students','reviews']
        model = api_models.Course

    def __init__(self, *args, **kwargs):
        super(CourseSerializer, self).__init__(*args, **kwargs)
        request  = self.context.get('request')
        if request and request.method =="POST":
            self.Meta.depth = 0
        else: 
            self.Meta.depth=1

class CartSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class Meta:
        fields = ['course', 'price', 'country', 'cart_id', 'date']
        model = api_models.Cart

    def get_course(self, obj):
        course = obj.course
        return {
            'image': f"http://127.0.0.1:8000/{course.image.url}",
            'title': course.title,
            'type': course.type
        }
    
class StudentSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(default=0)
    completed_lessons = serializers.IntegerField(default=0)
    achieved_certificates = serializers.IntegerField(default=0)

class TeacherSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(default=0)
    total_students = serializers.IntegerField(default=0)
    total_reviews = serializers.IntegerField(default=0)

class TeacherCourseListSerializer(serializers.ModelSerializer):
    lectures = serializers.SerializerMethodField()
    class Meta:
        model = api_models.Course
        fields = ['id', 'course_id', 'image', 'title', 'price', 'language', 'level', 'platform_status', 'teacher_course_status', 'slug', 'date', 'lectures']

    def get_lectures(self, obj):
        return obj.lectures().count()


# ----------------------------------------------------------------------------------------

class ForumCategorySerializer(serializers.ModelSerializer):
    threads = serializers.SerializerMethodField()
    closed_threads = serializers.SerializerMethodField()

    class Meta:
        model = api_models.ForumCategory
        fields = "__all__"

    def get_threads(self,obj):
        return api_models.Thread.objects.filter(category=obj).count()
    
    def get_closed_threads(self,obj):
        return api_models.Thread.objects.filter(category=obj, status='Closed').count()

class PostSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = api_models.Post
        fields = ['id', 'user', 'profile', 'message', "answer", 'thread',  'date']

class ThreadSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)
    num_posts = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    class Meta:
        model = api_models.Thread
        fields = ['id', 'title', 'status', 'description', 'category', 'slug', 'user', 'date', 'profile', 'num_posts']
        
    def get_num_posts(self, obj):
        return obj.num_posts()
    
    def get_category(self, obj):
        return obj.category.title