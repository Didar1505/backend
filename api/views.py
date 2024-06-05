from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from api import serializer as api_serializer
from api import models as api_models
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from distutils.util import strtobool
from django.core.files.uploadedfile import InMemoryUploadedFile
from userauths.models import User
import random
from decimal import Decimal
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import NotFound


# Email libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# simple function that send email to reset password
def send_email(email, subject, body):

    FROM = settings.EMAIL_SENDER
    TO = email
    PASSWORD = settings.PASSWORD

    # Create message
    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = subject

    # Email body
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to your email account
    server.login(FROM, PASSWORD)

    # Send the email
    text = msg.as_string()
    server.sendmail(FROM, TO, text)

    # Close the connection
    server.quit()
    print('success')

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer

class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = api_serializer.UserRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.create(serializer._validated_data)
        if user:
            user = api_serializer.UserSerializer(user)
            return Response(user.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email  = self.kwargs['email']

        user = User.objects.get(email=email)
        if user:
            user.otp = ''.join([str(random.randint(0,9)) for i in range(7)])
            user.save()

            uuidb64 = user.pk
            user.save()

            link = f'http://localhost:3000/auth/create-new-password/?otp={user.otp}&uuidb64={uuidb64}'
            body = f"""
                Hello, you requested a new password.
                To change your old password please click to the link below and your new password will be mailed to you.
                Link: {link}
                Thank you for your request. If you have any questions or concerns please Contact Us.
                """
            subject = "Caksiz Bilim - RESET PASSWORD"

            send_email(str(email), subject, body )
            
        return user
    
class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data['otp']
        uuidb64 = request.data['uuidb64']
        password = request.data['password']

        user = User.objects.get(id=uuidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ''
            user.save()
            return Response({'message': "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        return api_models.Profile.objects.get(user=user)
    
class TeacherProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.TeacherProfileSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Teacher.objects.all()
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        teacher = api_models.Teacher.objects.filter(user=user, active=True).first()

        if teacher:
            # If the teacher is found, use the serializer to return the teacher's data
            serializer = self.get_serializer(teacher)
            return Response(serializer.data)
        else:
            # If no teacher is found, return HTTP 204 No Content
            return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        user = User.objects.get(id=user_id)

        if user is not None:
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return Response({"title": "Password changed successfully", "icon": "success"})
            else:
                return Response({'title': 'Old password is incorrect', "icon": "warning"})
        else:
            return Response({'title': 'User does not exist', "icon": "error"})
                
class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]

class CourseListAPIView(generics.ListAPIView):
    queryset = api_models.Course.objects.filter(
        platform_status = "Published",
        teacher_course_status = 'Published')
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

class CourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        course = api_models.Course.objects.get(
            platform_status = "Published",
            teacher_course_status = 'Published',
            slug=slug)
        return course
    
class CartAPIView(generics.CreateAPIView):
    queryset = api_models.Cart.objects.all()
    serializer_class = api_serializer.CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course = request.data['course']
        user = request.user
        country_name = request.data['country']
        course = api_models.Course.objects.filter(course_id=course).first()
        price = course.price

        cart_exist = api_models.Cart.objects.filter(user=user, course=course).first()
        enrolled_course = api_models.EnrolledCourse.objects.filter(user=user, course=course).first()

        if enrolled_course:
            return Response({'message': "Siz eýýam bu kursa ýazyldyňyz!", 'icon': 'warning'})
        else:
            if cart_exist:
                return Response({"message": 'Bu kurs siziň sebediňizde bar', 'icon': 'warning' }, status=status.HTTP_200_OK)
            else:
                api_models.Cart.objects.create(
                    course=course,
                    user=user,
                    price=price,
                    country = country_name)

                #  Returns serialized cart instance
                # serializer = api_serializer.CartSerializer(cart, many=False)
                # return Response(serializer.data)

                return Response({"message": "Kurs sebediňize goşuldy", 'icon': 'success'}, status=status.HTTP_201_CREATED)
            
class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        # cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(user=user)
        return queryset
    
class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        user = self.request.user
    
        return api_models.Cart.objects.filter(user=user, cart_id = cart_id).first()
    
class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = api_models.CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        user = request.user

        cart_items = api_models.Cart.objects.filter(user=user)

        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user,
        )

        total_price = Decimal(0.00)

        for c in cart_items:
            api_models.CartOrderItem.objects.create(
                order=order,
                course = c.course,
                total = c.price,
                teacher = c.course.teacher
            )

            total_price += Decimal(c.price)
            order.teachers.add(c.course.teacher)

        order.total = total_price
        order.save()

        return Response({'message': 'order created successfully'}, status=status.HTTP_201_CREATED)

class DirectEnrollToCourseAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']

        user = User.objects.get(id=user_id)
        cart_items = api_models.Cart.objects.filter(user=user)

        online = []
        inperson = []

        for item in cart_items:
            enrolled_before = api_models.EnrolledCourse.objects.filter(user=user,course=item.course).first()
            if not enrolled_before:
                if item.course.type == "Online":
                    api_models.EnrolledCourse.objects.create(
                        user=user,
                        course=item.course,
                        teacher=item.course.teacher)
                    online.append(item.course.title)
                    item.delete()
                else:
                    inperson.append(item.course.title)
                    
                    body = f"""
                        Salam hormalty {item.course.teacher.full_name}. 

                        Siziň Çäksiz Bilim platformasyndaky "{item.course.title}" gatnaw kursyňyza okuwçy "{item.user.full_name}" gatnaşmaga höwes bildirdi.
                        Okuwçynyň email adresi: {item.user.email}
                        """
                    subject = "ÇÄKSIZ BILIM - TÄZE OKUWÇY"

                    send_email(item.course.teacher.user.email, subject, body )


            else:
                item.delete()


        return Response({'message': 'Siz üstinlikli kurslara ýazyldyňyz', 'online': online, 'inperson': inperson})

# handle the error
class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'

class PaymentSuccessAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    queryset = api_models.CartOrder.objects.all()
    
    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_id']

        order = api_models.CartOrder.objects.get(oid=order_oid)
        order_items = api_models.CartOrderItem.objects.filter(order=order)

        if order.payment_status == 'Processing':
            order.payment_status = 'Paid'
            order.save()
            api_models.Notification.objects.create(user=order.student, order=order, type="Course Enrollment Completed")

            for i in order_items:
                api_models.Notification.objects.create(
                    teacher=i.teacher,
                    order=order,
                    order_item = i,
                    type = "New Order"
                )
                api_models.EnrolledCourse.objects.create(
                    course = i.course,
                    user = order.student,
                    teacher = i.teacher,
                    order_item = i
                )

            return Response({'message': 'Payment Successfull'})
        else:
            return Response({"message": "Already Paid"})
    
class SearchCourseAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get('query')
        return api_models.Course.objects.filter(
            title__icontains=query, 
            platform_status = "Published",
            teacher_course_status = 'Published')

# DON'T FORGET TO ADD ISAUTH PERMISSION
class StudentSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.StudentSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        total_courses = api_models.EnrolledCourse.objects.filter(user=user).count()
        completed_lessons = api_models.CompletedLesson.objects.filter(user=user).count()
        achieved_certificates = api_models.Certificate.objects.filter(user=user).count()

        return [{
            "total_courses": total_courses,
            "completed_lessons": completed_lessons,
            "achieved_certificates": achieved_certificates,
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# DON'T FORGET TO ADD ISAUTH PERMISSION
class StudentCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        return api_models.EnrolledCourse.objects.filter(user=user)
    
# DON'T FORGET TO ADD ISAUTH PERMISSION
class StudentCourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]
    lookup_field = 'enrollment_id'

    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']

        user = User.objects.get(id=user_id)
        enrollment = api_models.EnrolledCourse.objects.get(user=user, enrollment_id=enrollment_id)
        return enrollment

# DON'T FORGET TO ADD ISAUTH PERMISSION
class StudentCourseCompletedCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CompletedLessonSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        variant_item_id = request.data['variant_item_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        variant_item = api_models.VariantItem.objects.get(variant_item_id = variant_item_id)

        completed_lessons = api_models.CompletedLesson.objects.filter(user=user, course=course, variant_item=variant_item).first()

        if completed_lessons:
            completed_lessons.delete()
            return Response({'message': 'Course marked as not completed'})
        else:
            api_models.CompletedLesson.objects.create(user=user, course=course, variant_item=variant_item)
            return Response({'message': 'Course marked as completed'})

class StudentNoteCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)

        return api_models.Note.objects.filter(user=user, course=enrolled.course)

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        enrollment_id = request.data['enrollment_id']
        title = request.data['title']
        note = request.data['note']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)

        api_models.Note.objects.create(user=user, course=enrolled.course, note=note, title=title)

        return Response({'message': 'Note created successfully'}, status=status.HTTP_201_CREATED)

class StudentNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        note_id = self.kwargs['note_id']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        note = api_models.Note.objects.get(user=user, course=enrolled.course, note_id=note_id)
        return note

class StudentRateCourseAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        rating = request.data['rating']
        review = request.data['review']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        api_models.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating
        )

        return Response({'message': 'Review created successfully'}, status=status.HTTP_201_CREATED)

class StudentRateCourseUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        review_id = self.kwargs['review_id']

        user = User.objects.get(id=user_id)
        return api_models.Review.objects.get(id=review_id, user=user)
    
class StudentWishListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.WishlistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        return api_models.Wishlist.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(course_id=course_id)

        wishlist = api_models.Wishlist.objects.filter(user=user, course=course).first()

        if wishlist:
            wishlist.delete()
            return Response({"message": "Wishlist deleted"}, status=status.HTTP_200_OK)
        else:
            api_models.Wishlist.objects.create(user=user, course=course)
            return Response({"message": "Wishlist created"}, status=status.HTTP_201_CREATED)
            
class QuestionAnswerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.Question_AnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.get(id=course_id)

        return api_models.Question_Answer.objects.filter(course=course)
    
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        title = request.data['title']
        message = request.data['message']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        question = api_models.Question_Answer.objects.create(
            course=course,
            user=user,
            title=title
        )

        api_models.Question_Answer_Message.objects.create(
            user=user,
            course=course,
            message=message,
            question=question
        )

        return Response({'message': 'Group conversation started'}, status=status.HTTP_201_CREATED)

class QuestionAnswerMessageSendAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.Question_Answer_MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        message = request.data['message']
        qa_id = request.data['qa_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        question = api_models.Question_Answer.objects.get(qa_id=qa_id)

        api_models.Question_Answer_Message.objects.create(
            course=course,
            question=question,
            user=user,
            message=message
        )
        question_serializer = api_serializer.Question_AnswerSerializer(question)
        return Response({'message': 'Messge Sent', 'question': question_serializer.data})

class TeacherSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        total_courses= api_models.Course.objects.filter(teacher=teacher)

        total_reviews = 0

        for i in total_courses:
            total_reviews += i.reviews().count()

        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)
                student = {
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url,
                    "country": user.profile.country,
                    "date": course.date,
                }
                students.append(student)
                unique_student_ids.add(course.user_id)
        
        return [{
            "total_courses": total_courses.count(),
            "total_students": len(students),
            'total_reviews': total_reviews
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class TeacherCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherCourseListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Course.objects.filter(teacher=teacher)

class TeacherReviewListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        return api_models.Review.objects.filter(course__teacher=teacher)
    
class TeacherReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        review_id = self.kwargs['review_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        return api_models.Review.objects.get(course__teacher=teacher, id=review_id)
    
class TeacherStudentsListAPIView(viewsets.ViewSet):
    def list(self, request, teacher_id=None):
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)
                # profile = api_models.Profile.objects.get(user=user)

                student = {
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url,
                    "country": user.profile.country,
                    "about":user.profile.about,
                    "date": course.date,
                }
                students.append(student)
                unique_student_ids.add(course.user_id)

        return Response(students)


class TeacherQuestionAnswerListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.Question_AnswerSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Question_Answer.objects.filter(course__teacher=teacher)
    
class TeacherNotificationListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Notification.objects.filter(teacher=teacher, seen=False)

class TeacherNotificationDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        noti_id = self.kwargs['noti_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Notification.objects.get(teacher=teacher, id=noti_id)
    
class CourseCreateAPIView(generics.CreateAPIView):
    queryset = api_models.Course.objects.all()
    serializer_class = api_serializer.CourseSerializer
    permisscion_classes = [AllowAny]


    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        course_instance = serializer.save()

        variant_data = []
        for key, value in self.request.data.items():
            if key.startswith('variant') and '[variant_title]' in key:
                index = key.split('[')[1].split(']')[0]
                title = value

                variant_dict = {'title': title}
                item_data_list = []
                current_item = {}
                # variant_data = []

                for item_key, item_value in self.request.data.items():
                    if f'variants[{index}][items]' in item_key:
                        field_name = item_key.split('[')[-1].split(']')[0]
                        if field_name == "title":
                            if current_item:
                                item_data_list.append(current_item)
                            current_item = {}
                        current_item.update({field_name: item_value})
                    
                if current_item:
                    item_data_list.append(current_item)

                variant_data.append({'variant_data': variant_dict, 'variant_item_data': item_data_list})

        for data_entry in variant_data:
            variant = api_models.Variant.objects.create(title=data_entry['variant_data']['title'], course=course_instance)

            for item_data in data_entry['variant_item_data']:
                preview_value = item_data.get("preview")
                preview = bool(strtobool(str(preview_value))) if preview_value is not None else False

                api_models.VariantItem.objects.create(
                    variant=variant,
                    title=item_data.get("title"),
                    description=item_data.get("description"),
                    file=item_data.get("file"),
                    preview=preview,
                )

    def save_nested_data(self, course_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={"course_instance": course_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course_instance) 

class CourseUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.CourseSerializer
    queryset = api_models.Course.objects.all()
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.get(course_id=course_id)
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        return course

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'image' in request.data and isinstance(request.data['image'], InMemoryUploadedFile):
            course.image = request.data['image']
        elif 'image' in request.data and str(request.data['image']) == 'No File':
            course.image = None

        if 'file' in request.data and not str(request.data['file']).startswith('http://'):
            course.file = request.data['file']

        if 'category' in request.data['category'] and request.data['category'] != 'NaN' and request.data['category'] != 'undefined':
            category = api_models.Category.objects.get(id=request.data['category'])
            course.category = category

        self.perform_update(serializer)
        self.update_variant(course,request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_variant(self, course, request_data):
        for key, value in request_data.items():
            if key.startswith('variants') and '[variant_title]' in key:
                index = key.split('[')[1].split(']')[0]
                title = value

                id_key = f'variants[{index}][variant_id]'
                variant_id = request_data.get(id_key)

                variant_data = {'title': title}
                item_data_list = []
                current_item = {}

                for item_key, item_value in request_data.items():
                    if f'variants[{index}][items]' in item_key:
                        field_name = item_key.split('[')[-1].split(']')[0]
                        if field_name == 'title':
                            if current_item:
                                item_data_list.append(current_item)
                            current_item = {}
                        current_item.update({field_name: item_value})
                
                if current_item: 
                    item_data_list.append(current_item)

                existing_variant = course.variant_set.filter(id=variant_id).first()

                if existing_variant:
                    existing_variant.title = title
                    existing_variant.save()

                    for item_data in item_data_list[1:]:
                        preview_value = item_data.get('preview')
                        preview = bool(strtobool(str(preview_value))) if preview_value is not None else False

                        variant_item = api_models.VariantItem.objects.filter(variant_item_id=item_data.get('variant_item_id')).first()

                        if not str(item_data.get('file')).startswith('http://'):
                            if item_data.get('file') != 'null':
                                file = item_data.get('file')
                            else:
                                file = None
                            title = item_data.get('title')
                            description = item_data.get('description')
                            
                            if variant_item:
                                variant_item.title = title
                                variant_item.description = description
                                variant_item.file = file
                                variant_item.preview = preview
                            else:
                                variant_item = api_models.VariantItem.objects.create(
                                    variant = existing_variant,
                                    title = title,
                                    description = description,
                                    file = file,
                                    preview = preview
                                )
                        else:
                            title = item_data.get('title')
                            description = item_data.get('desription')

                            if variant_item:
                                variant_item.title = title
                                variant_item.description = description
                                variant_item.file = file
                                variant_item.preview = preview
                            else:
                                variant_item = api_models.VariantItem.objects.create(
                                    variant = existing_variant,
                                    title = title,
                                    description = description,
                                    preview = preview
                                )
                        
                        variant_item.save()
                else:
                    new_variant = api_models.Variant.objects.create(
                        course = course, title = title
                    )

                    for item_data in item_data_list:
                        preview_value = item_data.get('preview')
                        preview = bool(strtobool(str(preview_value))) if preview_value is not None else False

                        api_models.VariantItem.objects.create(
                        variant=new_variant,
                        title=item_data.get('title'),
                        description=item_data.get('description'),
                        file=item_data.get('file'),
                        preview=preview,
                    )
                        
    def save_nested_data(self, course_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={'course_instance': course_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course_instance)

class TeacherCourseDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        course_id = self.kwargs['course_id']
        return api_models.Course.objects.get(course_id=course_id)
    
class CourseVariantDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.VariantSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        variant_id = self.kwargs['variant_id']
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']

        print("variant_id ========", variant_id)

        teacher = api_models.Teacher.objects.get(id=teacher_id)
        course = api_models.Course.objects.get(teacher=teacher, course_id=course_id)
        return api_models.Variant.objects.get(id=variant_id)
    
class CourseVariantItemDeleteAPIVIew(generics.DestroyAPIView):
    serializer_class = api_serializer.VariantItemSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        variant_id = self.kwargs['variant_id']
        variant_item_id = self.kwargs['variant_item_id']
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']


        teacher = api_models.Teacher.objects.get(id=teacher_id)
        course = api_models.Course.objects.get(teacher=teacher, course_id=course_id)
        variant = api_models.Variant.objects.get(variant_id=variant_id, course=course)
        return api_models.VariantItem.objects.get(variant=variant, variant_item_id=variant_item_id)

class TeacherCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.TeacherSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)

        profile = api_models.Profile.objects.get(user=user)

        teacher_exists = api_models.Teacher.objects.filter(user=user).first()

        if teacher_exists:
            return Response({'message': 'Your account is under verification by admin'})
        else:
            teacher = api_models.Teacher.objects.create(
                user = user,
                full_name = profile.full_name,
                image = profile.image,
                country = profile.country,
                about = profile.about
            )
            return Response({'message': 'Teacher is creted and under verification by admin'})

class TeachersListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherProfileSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Teacher.objects.all()


# ---------------------------------------------------------------------------------

class ForumCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.ForumCategorySerializer
    permission_classes = [AllowAny]
    queryset = api_models.ForumCategory.objects.all()


class ThreadList(generics.ListAPIView):
    serializer_class = api_serializer.ThreadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Thread.objects.filter(category__slug=self.kwargs['slug'])

class PostList(generics.ListCreateAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Post.objects.filter(thread__slug=self.kwargs['slug'])

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        message = request.data['message']
        thread_id = request.data['thread_id']

        user = User.objects.get(id=user_id)
        thread = api_models.Thread.objects.get(id=thread_id)
        
        post = api_models.Post.objects.create(
            user = user,
            message = message,
            thread = thread
        )

        return Response(api_serializer.PostSerializer(post, many=False).data)


class ThreadDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.ThreadSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']

        thread = api_models.Thread.objects.get(slug = slug)
        return thread

class ThreadCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.ThreadSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        title = request.data['title']
        description = request.data['description']
        category_title = request.data['category_title']

        user = User.objects.get(id= user_id)
        category = api_models.ForumCategory.objects.get(title=category_title)

        thread = api_models.Thread.objects.create(
            user=user,
            title=title,
            description= description,
            category = category
        )

        return Response(api_serializer.ThreadSerializer(thread, many=False).data)

class StudentQuestions(generics.ListAPIView):
    serializer_class = api_serializer.ThreadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        user = User.objects.get(id=user_id)

        threads = api_models.Thread.objects.filter(user=user)

        return threads

class PostUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        post_id = self.kwargs['post_id']

        return api_models.Post.objects.get(id=post_id)
    