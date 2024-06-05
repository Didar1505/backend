from django.urls import path
from api import views as api_views

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    # AUTHENTICATION ENDPOINTS
    path('user/login/', api_views.MyTokenObtainPairView.as_view(), name='user-get-token'),
    # path('user/token/refresh/', TokenRefreshView.as_view(), name='user-refresh-token'),
    path('user/register/', api_views.UserRegisterView.as_view(), name='user-register'),
    path('user/password-reset-email/<email>/', api_views.PasswordResetEmailVerifyAPIView.as_view(), name='user-password-reset'),
    path('user/password-change/', api_views.PasswordChangeAPIView.as_view(), name='password-change'),
    path("user/change-password/", api_views.ChangePasswordAPIView.as_view()),
    path("user/profile/<user_id>/", api_views.ProfileAPIView.as_view()),
    path("user/teacher-profile/<user_id>/", api_views.TeacherProfileAPIView.as_view()),

    # CORE ENDPOINTS
    path("course/category/", api_views.CategoryListAPIView.as_view()),
    path("course/search/", api_views.SearchCourseAPIView.as_view()),
    path("course/course-list/", api_views.CourseListAPIView.as_view()),
    path("course/course-detail/<slug>/", api_views.CourseDetailAPIView.as_view()),
    path("course/cart/", api_views.CartAPIView.as_view()),
    path("course/cart-list/", api_views.CartListAPIView.as_view()),
    path("course/cart-item-delete/<cart_id>/", api_views.CartItemDeleteAPIView.as_view()),
    path("order/create-order/", api_views.CreateOrderAPIView.as_view()),
    path("order/checkout/<oid>/", api_views.CheckoutAPIView.as_view()),
    path("payment/payment-success/", api_views.PaymentSuccessAPIView.as_view()),
    path("course/direct-enroll/", api_views.DirectEnrollToCourseAPIView.as_view()),

    # STUDENTS API ENDPOINTS
    path("student/summary/<user_id>/", api_views.StudentSummaryAPIView.as_view()),
    path("student/course-list/<user_id>/", api_views.StudentCourseListAPIView.as_view()),
    path("student/course-detail/<user_id>/<enrollment_id>/", api_views.StudentCourseDetailAPIView.as_view()),
    path('student/course-completed/', api_views.StudentCourseCompletedCreateAPIView.as_view()),
    path('student/course-note/<user_id>/<enrollment_id>/', api_views.StudentNoteCreateAPIView.as_view()),
    path('student/course-note/<user_id>/<enrollment_id>/<note_id>/', api_views.StudentNoteDetailAPIView.as_view()),
    path('student/rate-course/', api_views.StudentRateCourseAPIView.as_view()),
    path('student/review-detail/<user_id>/<review_id>/', api_views.StudentRateCourseUpdateAPIView.as_view()),
    path('student/wishlist/<user_id>/', api_views.StudentWishListCreateAPIView.as_view()),
    path('student/question-answer-list-create/<course_id>/', api_views.QuestionAnswerListCreateAPIView.as_view()),
    path('student/question-answer-message-create/', api_views.QuestionAnswerMessageSendAPIView.as_view()),
    path("student/<user_id>/forum-questions/", api_views.StudentQuestions.as_view()),


    # TEACHER ENDPOINTS
    path("teacher/new-account/", api_views.TeacherCreateAPIView.as_view()),
    path('teacher/summary/<teacher_id>/', api_views.TeacherSummaryAPIView.as_view()),
    path('teacher/course-lists/<teacher_id>/', api_views.TeacherCourseListAPIView.as_view()),
    path('teacher/review-lists/<teacher_id>/', api_views.TeacherReviewListAPIView.as_view()),
    path('teacher/review-detail/<teacher_id>/<review_id>/', api_views.TeacherReviewDetailAPIView.as_view()),
    path('teacher/student-list/<teacher_id>/', api_views.TeacherStudentsListAPIView.as_view({'get': 'list'})),
    path('teacher/question-answer-list/<teacher_id>/',api_views.TeacherQuestionAnswerListAPIView.as_view()),
    path('teacher/noti-list/<teacher_id>/',api_views.TeacherNotificationListAPIView.as_view()),
    path('teacher/noti-detail/<teacher_id>/<noti_id>/',api_views.TeacherNotificationDetailAPIView.as_view()),
    path('teacher/course-create/', api_views.CourseCreateAPIView.as_view()),
    path('teacher/course-update/<teacher_id>/<course_id>/', api_views.CourseUpdateAPIView.as_view()),
    path("teacher/course-detail/<course_id>/", api_views.TeacherCourseDetailAPIView.as_view()),
    path("teacher/course/variant-delete/<variant_id>/<teacher_id>/<course_id>/", api_views.CourseVariantDeleteAPIView.as_view()),
    path("teacher/course/variant-item-delete/<variant_id>/<variant_item_id>/<teacher_id>/<course_id>/", api_views.CourseVariantItemDeleteAPIVIew.as_view()),
    path('teacher/list/', api_views.TeachersListAPIView.as_view()),


    path('forum/categories/', api_views.ForumCategoryListAPIView.as_view()),
    path('forum/categories/<slug>/threads/', api_views.ThreadList.as_view()),
    path('forum/threads/<slug>/', api_views.ThreadDetailAPIView.as_view()),
    path('forum/posts/<slug>/', api_views.PostList.as_view()),
    path('forum/thread-create/', api_views.ThreadCreateAPIView.as_view()),
    path('forum/post-update/<post_id>/', api_views.PostUpdateAPIView.as_view()),
]
